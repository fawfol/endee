import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import uvicorn

from test_pipeline import setup_endee, ingest_text, retrieve_context, generate_answer

app = FastAPI()

class ChatRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    print(f"Received question: {req.question}")
    
    context = retrieve_context(req.question)
    
    if context:
        answer = generate_answer(req.question, context)
        return {"answer": answer}
    else:
        return {"answer": "I don't know the answer based on my database"}

if __name__ == "__main__":
    print("\nSTARTING WEB SERVER & DATANBASE...\n")
    setup_endee()
    
    print("\nloading documents data form file")
    
    # Check if the file exists, then read it
    if os.path.exists("knowledge_base.txt"):
        with open("knowledge_base.txt", "r", encoding="utf-8") as file:
            full_text = file.read()
            
            # Split the document into chunks by double newlines (paragraphs)
            chunks = full_text.split("\n\n") 
            
            # Ingest each paragraph into Endee
            for i, chunk in enumerate(chunks):
                if chunk.strip(): # Ignore empty lines
                    ingest_text(i, chunk.strip())
                    
        print(f"\nSuccessfully loade data")
    else:
        print("\nNo file found")
    
    print("\nDatabase loaded adn Starting UI:::")
    
    # Start the web server
    uvicorn.run(app, host="0.0.0.0", port=3000)
