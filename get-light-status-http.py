import requests
import json
import time
from datetime import datetime

# Set your Shelly device URL (ensure SHELLY is set as an environment variable or replace it with the actual IP)
SHELLY = "192.168.68.102"  # Replace with your actual Shelly device IP or hostname

# Define the request URL
url = f"http://{SHELLY}/rpc"

# Define the JSON payload
payload = {"id": 1, "method": "Light.GetStatus", "params": {"id": 0}}

# Headers for the request
headers = {"Content-Type": "application/json"}

while True:
    try:
        # Send the request
        response = requests.post(url, json=payload, headers=headers)

        # Ensure the request was successful
        if response.status_code == 200:
            data = response.json()

            # Extract output and brightness values
            result = data.get("result", {})
            output = result.get("output")
            brightness = result.get("brightness")

            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Print the values
            print(f"[{timestamp}] Output: {output}, Brightness: {brightness}")
        else:
            print(f"Error: Received status code {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

    # Wait for 3 seconds before the next iteration
    time.sleep(2)