# user_function

import json
import os
from colorama import Fore, Back, Style

#https://community.openai.com/t/gpt-4-1106-preview-messes-up-function-call-parameters-encoding/478500/32
def fix_bad_encoding(text: str) -> str:
    words = text.split(' ')
    for i in range(len(words)):
        while True:
            try:
                new_word = words[i].encode('latin1').decode('utf8')
                if new_word == words[i]:
                    break
                words[i] = new_word
            except UnicodeError:
                break
    return ' '.join(words)

## stock function
#latest version is not working, use previous version, `pip yfinance==0.2.36``
#https://pypi.org/project/yfinance/
import yfinance as yf


def get_current_stock_price(stock_symbol) -> str:
    print(Fore.BLUE, f"tool: get current stock price of {stock_symbol}", Style.RESET_ALL)
    try:
        stock_data = yf.Ticker(stock_symbol)

        return stock_data.info["currentPrice"]
    except Exception as e:
        print(Fore.RED, f"Error: {e}", Style.RESET_ALL)
        return json.dumps({"stock_symbol": stock_symbol, "error": "An error occurred while fetching data"})
    
# Currency pair, example USDJPY, USDKRW
def get_current_currency_rate(currency_pair) -> str:
    print(Fore.BLUE, f"tool: get current currency of {currency_pair}", Style.RESET_ALL)
    try:
        stock_data = yf.Ticker(f"{currency_pair}=X")

        return stock_data.info["open"]
    except Exception as e:
        print(Fore.RED, f"Error: {e}", Style.RESET_ALL)
        return json.dumps({"currency_pair": currency_pair, "error": "An error occurred while fetching data"})

from azure.core.credentials import AzureKeyCredential  

service_endpoint = os.getenv("AZSCH_ENDPOINT")  
key = os.getenv("AZSCH_KEY")  
credential = AzureKeyCredential(key)
index_name = os.getenv("AZSCH_INDEX_NAME")  

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery

search_client = SearchClient(service_endpoint, index_name, credential=credential)

def get_results(text, n=2):
    vector_query = VectorizableTextQuery(text=text, k_nearest_neighbors=n, fields="vector", exhaustive=True)
    results = search_client.search(  
        search_text=None,  
        vector_queries= [vector_query],
        select=["parent_id", "chunk_id", "chunk", "title"],
        top=n)
    return results

def search_document(keyword, n=2) -> str:
    keyword = fix_bad_encoding(keyword)
    print(Fore.BLUE, f"tool: search the document of \"{keyword}\"", Style.RESET_ALL)

    try:
        results = list(get_results(keyword, n))
        
        context = []
        for i in range(n):
            if i < len(results):
                context.append( f"{results[i]['chunk']}\n[Reference {i}]({results[i]['chunk_id']})")

        # return context
        return "\n\n".join(context)
    except Exception as e:
        print(Fore.RED, f"Error: {e}", Style.RESET_ALL)
        return "Error occurred while fetching data"
    
# Warning: this is for demo purpose
def simple_math(expression) -> str:
    print(Fore.BLUE, f"tool: {expression}", Style.RESET_ALL)
    try:

        return eval(expression)
    except Exception as e:
        print(Fore.RED, f"Error: {e}", Style.RESET_ALL)
        return "Error occurred while evaluating math expression"