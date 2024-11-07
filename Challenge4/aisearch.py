from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery

class AISearch:
    def __init__(self, endpoint, index_name, credential):
        self.topK = 3
        self.search_client = SearchClient(endpoint, index_name, credential=credential)

    def get_results(self, text):
        vector_query = VectorizableTextQuery(text=text, k_nearest_neighbors=self.topK, fields="vector", exhaustive=True)
        results = self.search_client.search(  
            search_text=text,  
            vector_queries= [vector_query],
            select=["parent_id", "chunk_id", "chunk", "title"],
            top=self.topK
        )

        return results
        
    def get_context(self, text):
        
        def format_doc(doc: dict):
            return f"Content: {doc['Content']}\nSource: {doc['Source']}"
        
        vector_query = VectorizableTextQuery(text=text, k_nearest_neighbors=self.topK, fields="vector", exhaustive=True)
        results = self.search_client.search(  
            search_text=None,  
            vector_queries= [vector_query],
            select=["parent_id", "chunk_id", "chunk", "title"],
            top=self.topK
        )  
    
        _context = []
        metadata = []
        for result in results:
            source = result['title']
            _context.append({
                "Content": result['chunk'],
                "Source": f"[{source}](https://github.com/MicrosoftDocs/azure-docs/tree/main/articles/ai-service/openai/{source})"})
            
            metadata.append({"score": result['@search.score'], "chunk_id": result['chunk_id'], "parent_id": result['parent_id'], "title": result["title"]})
    
        context = "\n\n".join(format_doc(doc) for doc in _context)
        return context, metadata