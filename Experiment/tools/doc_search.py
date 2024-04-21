import os 

from azure.core.credentials import AzureKeyCredential  

service_endpoint = os.getenv("AZSCH_ENDPOINT")  
key = os.getenv("AZSCH_KEY")  
credential = AzureKeyCredential(key)
index_name = os.getenv("AZSCH_INDEX_NAME")  

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery, QueryType

search_client = SearchClient(service_endpoint, index_name, credential=credential)

def get_manifest():
    manifest = {
        "name": "search_document",
        "description": "search and get the company information about work manual, policy, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search keyword to find the information. e.g., Policy, Work Manual, etc."
                }
            },
            "required": ["keyword"]
        }
    }
    return manifest

def get_results(text, n=2):
    vector_query = VectorizableTextQuery(text=text, k_nearest_neighbors=n, fields="vector", exhaustive=True)
    results = search_client.search(  
        search_text=text,
        vector_queries=[vector_query],
        select=["parent_id", "chunk_id", "chunk", "title"],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='semantic-config'
    )
    return results

def search_document(keyword, n=2):
    print(f"tool: search the document of \"{keyword}\"")

    try:
        results = list(get_results(keyword, n))
        
        context = []
        for i in range(n):
            if i < len(results):
                context.append( f"{results[i]['chunk']}\n[Reference {i}]({results[i]['parent_id']}/{results[i]['chunk_id']})")

        # return context
        return "\n\n".join(context)
    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred while fetching data"

if __name__ == "__main__":
    print("doc_search.py")