import requests

ENDEE_BASE_URL = "http://localhost:8080/api/v1"
INDEX_NAME = "documents"

def create_index_if_not_exists(dimension=384):
    """Creates the index to store our vectors"""
    # sentence-transformers all-MiniLM-L6-v2 outputs 384 dimensions
    payload = {
        "name": INDEX_NAME,
        "dimension": dimension
    }
    #guessing the payload structure ...  may need to adjust!
    requests.post(f"{ENDEE_BASE_URL}/index/create", json=payload)

def store_in_endee(chunk_id, text_chunk, vector):
    """Sends the vector to the specific index"""
    url = f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/vector/insert"
    
    payload = {
        "id": str(chunk_id),
        "vector": vector,
        "metadata": {"text": text_chunk} #sttoring the text so we can retrieve it
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"inserted chunk {chunk_id}")
    except Exception as e:
        print(f"failed to insert: {e} | Response: {response.text}")
