from kiteconnect import KiteConnect
import time

# Initialize KiteConnect with API Key
API_KEY = "wjcydche0yvjiiuy"
API_SECRET = "92c1gqdu9foufub9c2vy68q8356kewym"

kite = KiteConnect(api_key=API_KEY)


# Generate the login URL
print("Login URL:", kite.login_url())

# Once logged in, get the request token from the redirected URL and exchange it for an access token
REQUEST_TOKEN = "SYogjpiC0PZCbqaGTVGkAHpD9g7v29Ow"  # Enter manually after login

# Generate Access Token
data = kite.generate_session(REQUEST_TOKEN, api_secret=API_SECRET)
ACCESS_TOKEN = data["access_token"]

# Set access token
kite.set_access_token(ACCESS_TOKEN)

# Fetch live stock price function
def get_live_stock_price(trading_symbol, exchange="NSE"):
    instrument_token = None

    # Fetch instrument list and find the instrument token
    instruments = kite.instruments(exchange)
    for instrument in instruments:
        if instrument['tradingsymbol'] == trading_symbol:
            instrument_token = instrument['instrument_token']
            break

    if instrument_token:
        # Fetch live price
        quote = kite.ltp(f"{exchange}:{trading_symbol}")
        return quote[f"{exchange}:{trading_symbol}"]["last_price"]
    else:
        return "Instrument not found"

# Example Usage
while True:
    stock_symbol = "RELIANCE"
    live_price = get_live_stock_price(stock_symbol)
    print(f"Live price of {stock_symbol}: ₹{live_price}")
    time.sleep(5)  # Fetch data every 5 seconds
