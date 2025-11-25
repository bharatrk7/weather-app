import requests
# 1. We import 'send_from_directory' to serve files
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_weather_description(code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
        61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        80: "Slight Showers", 81: "Moderate Showers", 82: "Violent Showers",
    }
    return weather_codes.get(code, "Unknown")

@app.route('/api/weather', methods=['GET'])
def get_weather():
    print("Fetching real data from Open-Meteo...")
    url = "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current_weather=true&temperature_unit=fahrenheit"
    response = requests.get(url)
    external_data = response.json()
    current_weather = external_data['current_weather']
    
    formatted_data = {
        "city": "New York",
        "temperature": current_weather['temperature'],
        "condition": get_weather_description(current_weather['weathercode']),
        "windspeed": current_weather['windspeed']
    }
    return jsonify(formatted_data)

# --- NEW PLUMBING BELOW ---

# This tells Flask: "When the user visits '/', serve the 'index.html' file"
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)