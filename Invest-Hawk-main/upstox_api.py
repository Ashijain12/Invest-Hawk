# api_key = "4b48e5c5-72cc-459e-a8f0-4cb4dca73cd4"
# access_token = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2VUJUN1ciLCJqdGkiOiI2N2NlOGIwNjQ5OGQ1MzE4ZTg1MTY1MDEiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaWF0IjoxNzQxNTg5MjU0LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NDE2NDQwMDB9.sO1pnFXP2BQLA9ZquIXs7OTlh6J4TiGxwM9Fx12s45Q"
# u = Upstox(api_key,access_token)

# Import necessary modules
import asyncio
import json
import ssl
import websockets
import requests
from google.protobuf.json_format import MessageToDict

import MarketDataFeedV3_pb2 as pb


def get_market_data_feed_authorize_v3():
    """Get authorization for market data feed."""
    access_token = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2VUJUN1ciLCJqdGkiOiI2N2NmZDgzY2Q4MGZiMDM1MDBjZmU5MTkiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaWF0IjoxNzQxNjc0NTU2LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NDE3MzA0MDB9.5VAwcmpLvLwjKUAc0H7NQgOX7k5TjLLtu_1wn94yMNY'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    url = 'https://api.upstox.com/v3/feed/market-data-feed/authorize'
    api_response = requests.get(url=url, headers=headers)
    response_json = api_response.json()
    print("API Response:", response_json)  # Debugging line
    return api_response.json()


def decode_protobuf(buffer):
    """Decode protobuf message."""
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return feed_response


async def fetch_market_data():
    """Fetch market data using WebSocket and print it."""

    # Create default SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Get market data feed authorization
    response = get_market_data_feed_authorize_v3()
    # Connect to the WebSocket with SSL context
    async with websockets.connect(response["data"]["authorized_redirect_uri"], ssl=ssl_context) as websocket:
        print('Connection established')

        await asyncio.sleep(1)  # Wait for 1 second

        # Data to be sent over the WebSocket
        data = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": ["NSE_INDEX|Nifty Bank", "NSE_INDEX|Nifty 50"]
            }
        }

        # Convert data to binary and send over WebSocket
        binary_data = json.dumps(data).encode('utf-8')
        await websocket.send(binary_data)

        # Continuously receive and decode data from WebSocket
        while True:
            message = await websocket.recv()
            decoded_data = decode_protobuf(message)

            # Convert the decoded data to a dictionary
            data_dict = MessageToDict(decoded_data)

            # Print the dictionary representation
            print(json.dumps(data_dict))


# Execute the function to fetch market data
asyncio.run(fetch_market_data())    