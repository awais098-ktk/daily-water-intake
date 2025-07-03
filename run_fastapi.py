"""
Standalone script to run the FastAPI server for voice input processing.
This script doesn't require uvicorn to be installed.
"""
import sys
import os
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from urllib.parse import parse_qs

# N8N webhook URL - update this to match your n8n setup
N8N_URL = "http://localhost:5678/webhook/voice-log"

# Flag to use mock response for testing when n8n is not available
USE_MOCK_RESPONSE = True

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

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == '/':
            self._set_headers()
            response = {
                "status": "Server is running",
                "endpoints": ["/voice-input"]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        if self.path == '/voice-input':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                text = data.get('text', '')
                
                if not text:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "No text provided"}).encode())
                    return
                
                print(f"Received voice input: {text}")
                
                try:
                    # Try to send to n8n webhook
                    response = requests.post(N8N_URL, json={"text": text}, timeout=5)
                    print(f"n8n response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        self._set_headers()
                        self.wfile.write(json.dumps({"n8n_response": response.json()}).encode())
                    else:
                        print(f"n8n error: {response.text}")
                        if USE_MOCK_RESPONSE:
                            self._set_headers()
                            self.wfile.write(json.dumps({"n8n_response": generate_mock_response(text)}).encode())
                        else:
                            self._set_headers(500)
                            self.wfile.write(json.dumps({"error": f"n8n webhook returned status code {response.status_code}"}).encode())
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error connecting to n8n: {e}")
                    if USE_MOCK_RESPONSE:
                        self._set_headers()
                        self.wfile.write(json.dumps({"n8n_response": generate_mock_response(text)}).encode())
                    else:
                        self._set_headers(500)
                        self.wfile.write(json.dumps({"error": f"Could not connect to n8n: {str(e)}"}).encode())
            
            except Exception as e:
                print(f"Error processing request: {e}")
                import traceback
                traceback.print_exc()
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Error processing request: {str(e)}"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run()
