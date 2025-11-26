import sqlite3
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- 1. THE SELF-HEALING MECHANISM ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# IMPORTANT: Run this setup immediately when the app starts!
init_db()

# --- 2. DATABASE HELPER ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- 3. WEATHER LOGIC ---
def get_weather_description(code):
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light Drizzle", 53: "Moderate Drizzle",
        55: "Dense Drizzle", 61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        80: "Slight Showers", 81: "Moderate Showers", 82: "Violent Showers",
    }
    return weather_codes.get(code, "Unknown")

# --- NEW HELPER FUNCTION ---
def get_coordinates(city_name):
    print(f"Looking up coordinates for: {city_name}")
    # We use a DIFFERENT Open-Meteo URL specifically for finding cities
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    
    response = requests.get(url)
    data = response.json()
    
    # Safety Check: Did we find a city?
    if not data.get('results'):
        return None, None # Return "Nothing" if city not found
        
    # Grab the first result
    first_match = data['results'][0]
    return first_match['latitude'], first_match['longitude']

# --- UPDATED WEATHER ENDPOINT ---
@app.route('/api/weather', methods=['GET'])
def get_weather():
    # 1. GET THE CITY NAME FROM THE FRONTEND
    # The frontend will send it like: /api/weather?city=Paris
    city = request.args.get('city')
    
    if not city:
        return jsonify({"error": "Please provide a city name"}), 400

    # 2. STEP 1: CONVERT TEXT TO NUMBERS (Geocoding)
    lat, lon = get_coordinates(city)
    
    if not lat:
        return jsonify({"error": "City not found"}), 404

    # 3. STEP 2: GET WEATHER USING NUMBERS
    print(f"Fetching weather for {city} at {lat}, {lon}")
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=fahrenheit"
    
    response = requests.get(weather_url)
    data = response.json()
    current_weather = data['current_weather']
    
    return jsonify({
        "city": city.title(), # Capitalize (paris -> Paris)
        "temperature": current_weather['temperature'],
        "condition": get_weather_description(current_weather['weathercode'])
    })

# --- 4. FAVORITES ENDPOINTS ---
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    conn = get_db_connection()
    favorites = conn.execute('SELECT * FROM favorites').fetchall()
    conn.close()
    favorites_list = [{'id': row['id'], 'city': row['city']} for row in favorites]
    return jsonify(favorites_list)

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    new_data = request.get_json()
    city_name = new_data['city']
    
    conn = get_db_connection()
    
    # 1. Check for duplicates
    existing_city = conn.execute('SELECT * FROM favorites WHERE city = ?', (city_name,)).fetchone()
    
    if existing_city:
        conn.close()
        # Make sure this return is indented INSIDE the if
        return jsonify({"message": "City already in favorites!"}), 409 

    # 2. Save the new city
    conn.execute('INSERT INTO favorites (city) VALUES (?)', (city_name,))
    conn.commit()
    conn.close()
    
    # CRITICAL: This return must be here, at this indentation level!
    return jsonify({"message": "City saved successfully!"}), 201

# --- 5. SERVE HTML ---
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# --- DELETE ENDPOINT ---
# The <int:favorite_id> is crucial. It tells Flask to expect a number in the URL.
@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    conn = get_db_connection()
    
    # Run the delete command for this specific ID
    conn.execute('DELETE FROM favorites WHERE id = ?', (favorite_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "City deleted!"}), 200
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)