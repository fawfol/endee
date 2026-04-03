import requests
import json
import re
from sentence_transformers import SentenceTransformer

ENDEE_BASE_URL = "http://localhost:8080/api/v1"
OLLAMA_URL = "http://localhost:11434/api/generate"
INDEX_NAME = "ui_database_v1"
HEADERS = {"Content-Type": "application/json"}

print("Loading embedding model (this might take a few seconds)...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def setup_endee():
    """Creates the index in Endee"""
    print(f"Creating index '{INDEX_NAME}' in Endee...")

    payload = {
        "index_name": INDEX_NAME, 
        "dim": 384,
        "space_type": "cosine" 
    }

    try:
        res = requests.post(f"{ENDEE_BASE_URL}/index/create", json=payload, headers=HEADERS)
        if res.status_code in [200, 201, 409]:
            print(" Index ready.")
        else:
            print(f" Index setup issue: {res.text}")
    except Exception as e:
        print(f" Cannot connect to Endee: {e}. Is 'bash run.sh' running?")
        exit(1)

def ingest_text(chunk_id, text):
    """Embeds text and stores it in Endee"""
    vector = embedder.encode(text).tolist()
    payload = [{
        "id": str(chunk_id),
        "vector": vector,
        "meta": json.dumps({"text": text}) 

    }]

    res = requests.post(f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/vector/insert", json=payload, headers=HEADERS)

    if res.status_code != 200:
        print(f" Insert failed for chunk {chunk_id}. Endee says: {res.text}")
    else:
        print(f" Inserted chunk {chunk_id} into Endee.")

def retrieve_context(question, top_k=2):
    """Searches Endee and parses the custom binary/text response"""
    query_vector = embedder.encode(question).tolist()

    payload = {
        "vector": query_vector, 
        "k": top_k
    }

    res = requests.post(f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/search", json=payload, headers=HEADERS)

    if res.status_code != 200:
        print(f" Search failed. Endee says: {res.text}")
        return []

    retrieved_texts = []

    matches = re.findall(r'\{"text":\s*".*?"\}', res.text)

    for match in matches:
        try:

            meta_dict = json.loads(match)
            retrieved_texts.append(meta_dict.get("text", ""))
        except Exception as e:
            print(f" Regex extraction parsed invalid JSON: {match}")
            pass

    return retrieved_texts

def generate_answer(question, context_chunks):
    """Asks the local Qwen model to answer based ONLY on the context"""
    context_text = "\n\n".join(context_chunks)
    
    print(f"\n[DEBUG] Context successfully retrieved from Endee:\n{context_text}\n")
    
    prompt = f"""Based on the following text, answer the question.
    
Text: {context_text}

Question: {question}
Answer:"""

    print("asking local LLM...")
    res = requests.post(OLLAMA_URL, json={
        "model": "qwen2:0.5b", 
        "prompt": prompt,
        "stream": False
    })
    
    if res.status_code == 200:
        return res.json().get("response", "No response generated.")
    else:
        return f"LLM Error: {res.text}"

if __name__ == "__main__":
    print("\n STARTING RAG PIPELINE TEST\n")

    setup_endee()

    doc_1 = "Endee is a high-performance open-source vector database built for AI search and retrieval workloads. It is designed for teams building RAG pipelines, semantic search, hybrid search, recommendation systems, and filtered vector retrieval APIs that need production-oriented performance and control."
    doc_2 = "Ollama is a lightweight tool for running Large Language Models locally without needing API keys."
    doc_3 = "The internship requires building a RAG system and pays a stipend of ₹20,000 for the first 3 months."

    print("\n---ingesting docs---")
    ingest_text(1, doc_1)
    ingest_text(2, doc_2)
    ingest_text(3, doc_3)

    #chat loop
    print("\n" + "="*50)
    print("TERMINAL RAG BOT INITIALIZED")
    print("Type 'exit' or 'quit' to stop.")
    print("="*50 + "\n")

    while True:
        user_question = input("\n @You: ")
        
        if user_question.lower() in ['exit', 'quit']:
            print("Shutting down... Goodbye!")
            break
        print("Searching Endee for context...")
        context = retrieve_context(user_question)

        if context:
            print(f"Found Context!")
            final_answer = generate_answer(user_question, context)
            print(f"\nAI: {final_answer}\n")
        else:
            print("\nAI: I couldn't find any relevant context in the database.\n")

##you know aanyone can wrap an OpenAI API key in five lines of code BUT building a custom C++ database pipeline on a constrained Linux machine then handling binary data streams and optimizing for a 0.5B parameter edge model?? meh i think thats Senior Engineer material
