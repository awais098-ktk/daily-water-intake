from fastapi import FastAPI, Request
import requests
import re

app = FastAPI()

# N8N webhook URL - update this to match your n8n setup
N8N_URL = "http://localhost:5678/webhook/voice-log"

# Flag to use mock response for testing when n8n is not available
USE_MOCK_RESPONSE = True

@app.get("/")
async def root():
    """Root endpoint for testing if the server is running"""
    return {"status": "FastAPI server is running", "endpoints": ["/voice-input"]}

@app.post("/voice-input")
async def voice_input(req: Request):
    """Process voice input text and send to n8n webhook"""
    try:
        data = await req.json()
        text = data.get("text", "")  # e.g., "I drank 400 ml"

        if not text:
            return {"error": "No text provided"}

        print(f"Received voice input: {text}")

        try:
            # Try to send to n8n webhook
            response = requests.post(N8N_URL, json={"text": text}, timeout=5)
            print(f"n8n response status: {response.status_code}")

            if response.status_code == 200:
                return {"n8n_response": response.json()}
            else:
                print(f"n8n error: {response.text}")
                if USE_MOCK_RESPONSE:
                    return {"n8n_response": generate_mock_response(text)}
                else:
                    return {"error": f"n8n webhook returned status code {response.status_code}"}

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to n8n: {e}")
            if USE_MOCK_RESPONSE:
                return {"n8n_response": generate_mock_response(text)}
            else:
                return {"error": f"Could not connect to n8n: {str(e)}"}

    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Error processing request: {str(e)}"}

def generate_mock_response(text):
    """Generate a mock response for testing when n8n is not available"""
    print(f"Generating mock response for: {text}")

    # Extract volume using regex
    volume_match = re.search(r'(\d+)\s*(ml|milliliters|millilitres|oz|ounces|cups?|glasses?|bottles?|liters?|litres?)', text.lower())
    volume = "0 ml"

    if volume_match:
        amount = int(volume_match.group(1))
        unit = volume_match.group(2)

        # Convert to ml based on unit
        if unit in ['oz', 'ounces']:
            amount = int(amount * 29.57)  # 1 oz = 29.57 ml
        elif unit in ['cup', 'cups']:
            amount = int(amount * 237)  # 1 cup = 237 ml
        elif unit in ['glass', 'glasses']:
            amount = int(amount * 250)  # Assume 1 glass = 250 ml
        elif unit in ['bottle', 'bottles']:
            amount = int(amount * 500)  # Assume 1 bottle = 500 ml
        elif unit in ['liter', 'liters', 'litre', 'litres']:
            amount = int(amount * 1000)  # 1 liter = 1000 ml

        volume = f"{amount} ml"

    # Extract drink type
    drink_type = "Water"  # Default
    if "coffee" in text.lower():
        drink_type = "Coffee"
    elif "tea" in text.lower():
        drink_type = "Tea"
    elif "juice" in text.lower() or "orange" in text.lower():
        drink_type = "Juice"
    elif "milk" in text.lower():
        drink_type = "Milk"
    elif "soda" in text.lower() or "coke" in text.lower():
        drink_type = "Soda"
    elif "pepsi" in text.lower():
        drink_type = "Pepsi"

    return {
        "volume": volume,
        "drink_type": drink_type,
        "text": text,
        "source": "mock_response"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
