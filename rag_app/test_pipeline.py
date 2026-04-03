import requests
import json
import re
from sentence_transformers import SentenceTransformer

ENDEE_BASE_URL = "http://localhost:8080/api/v1"
OLLAMA_URL = "http://localhost:11434/api/generate"
INDEX_NAME = "my_docs_v2"  

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

    prompt = f"""You are a helpful assistant. Use ONLY the following context to answer the question. If the answer is not in the context, say "I don't know."

Context:
{context_text}

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
        return f" LLM Error: {res.text}"

if __name__ == "__main__":
    print("\n STARTING RAG PIPELINE TEST\n")

    setup_endee()

    doc_1 = "Endee is a high-performance vector database written in C++. It is designed for semantic search."
    doc_2 = "Ollama is a lightweight tool for running Large Language Models locally without needing API keys."
    doc_3 = "The internship requires building a RAG system and pays a stipend of ₹20,000 for the first 3 months."

    print("\n---ingesting docs---")
    ingest_text(1, doc_1)
    ingest_text(2, doc_2)
    ingest_text(3, doc_3)

    user_question = "What is the endee?"
    print(f"\n Question: {user_question}")

    print(" Searching Endee for context...")
    context = retrieve_context(user_question)

    if context:
        print(f" Found Context!")

        final_answer = generate_answer(user_question, context)
        print(f"\n FINAL AI ANSWER:\n{final_answer}\n")
    else:
        print(" No context found in the database.")

