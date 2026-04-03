import requests

ENDEE_BASE_URL = "http://localhost:8080/api/v1"
INDEX_NAME = "documents"

def search_endee(query_vector, top_k=3):
    """Searches specific index for matching vectors"""
    url = f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/search"
    
    payload = {
        "vector": query_vector,
        "top_k": top_k
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json() 
    except Exception as e:
        print(f"search failed: {e}")
        return []
