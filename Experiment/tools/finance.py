# user_function

import json
import yfinance as yf

def get_manifest():
    manifest = {
                "name": "get_current_stock_price",
                "description": "get the current stock price of ticker symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stock_symbol": {
                            "type": "string",
                            "description": "The symbol of the finance ticker, e.g., MSFT, AAPL, GOOGL"
                        }
                    },
                    "required": ["stock_symbol"]
                }
            }
    return manifest

def get_current_stock_price(stock_symbol):
    print(f"get current stock price of `{stock_symbol}`")
    try:
        stock_data = yf.Ticker(stock_symbol)

        return stock_data.info["currentPrice"]
    except Exception as e:
        print(f"Error: {e}")
        return json.dumps({"stock_symbol": stock_symbol, "error": "An error occurred while fetching data"})
    
if __name__ == "__main__":
    print("finace module")
    print(get_current_stock_price("MSFT"))

