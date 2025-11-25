import requests # <--- The new tool we just bought
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# A helper function to translate Open-Meteo's numeric codes into words
def get_weather_description(code):
    # Codes from: https://open-meteo.com/en/docs
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
        61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        80: "Slight Showers", 81: "Moderate Showers", 82: "Violent Showers",
    }
    # Return the description, or "Unknown" if the code isn't in our list
    return weather_codes.get(code, "Unknown")

@app.route('/api/weather', methods=['GET'])
def get_weather():
    print("Fetching real data from Open-Meteo...")
    
    # 1. DEFINE THE TARGET
    # We are aiming at New York City (Lat: 40.71, Long: -74.00)
    # This URL is the "Phone Number" of the Open-Meteo server.
    url = "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current_weather=true&temperature_unit=fahrenheit"
    
    # 2. MAKE THE CALL (The "Pipe" to the outside world)
    # Python uses the 'requests' library to hit that URL
    response = requests.get(url)
    
    # 3. UNPACK THE SATELLITE DATA
    external_data = response.json()
    
    # 4. FILTER/CLEAN THE DATA
    # The satellite gives us A LOT of data. We only want a few specific pieces.
    current_weather = external_data['current_weather']
    
    # We build our own clean package to send to the Frontend
    formatted_data = {
        "city": "New York", # Hardcoded for now
        "temperature": current_weather['temperature'],
        "condition": get_weather_description(current_weather['weathercode']),
        "windspeed": current_weather['windspeed']
    }
    
    # 5. SEND IT HOME
    return jsonify(formatted_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)