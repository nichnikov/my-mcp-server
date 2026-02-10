import weaviate
import weaviate.classes.init
import requests
import os

# Configuration
WEAVIATE_URL = os.getenv("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", 8080))
WEAVIATE_GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))
TRANSFORMERS_URL = os.getenv("TRANSFORMERS_URL", "http://localhost:9090/vectors")

def get_weaviate_client():
    """Returns a configured Weaviate v4 client."""
    return weaviate.connect_to_local(
        host=WEAVIATE_URL,
        port=WEAVIATE_PORT,
        grpc_port=WEAVIATE_GRPC_PORT,
        additional_config=weaviate.classes.init.AdditionalConfig(
            timeout=weaviate.classes.init.Timeout(init=2, query=10, insert=30)
        )
    )

def get_embedding(text: str):
    """
    Get vector embedding from the local transformers service.
    This mimics the behavior of Weaviate's text2vec-transformers but allows
    us to get the vector manually for hybrid search.
    """
    try:
        response = requests.post(TRANSFORMERS_URL, json={"text": text}, timeout=10)
        response.raise_for_status()
        return response.json().get("vector")
    except Exception as e:
        print(f"Error getting vector from {TRANSFORMERS_URL}: {e}")
        return None
