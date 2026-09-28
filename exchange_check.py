import requests

# We use a free, public API to get currency data
url = "https://er-api.com"

print("Connecting to the currency API...")

try:
    # 1. Send the request
    response = requests.get(url)
    
    # 2. Check if the connection was successful
    if response.status_code == 200:
        data = response.json()
        
        # 3. Extract specific exchange rates
        usd_rate = data["rates"]["USD"]
        eur_rate = data["rates"]["EUR"]
        
        print("\n--- Success! Current Rates for 1 GBP ---")
        print(f"US Dollars: ${usd_rate:.2f}")
        print(f"Euros: €{eur_rate:.2f}")
        
    else:
        print(f"Failed to connect. Server responded with status code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")