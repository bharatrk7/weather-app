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

@app.route('/api/weather', methods=['GET'])
def get_weather():
    # CHANGED: London Coordinates
    url = "https://api.open-meteo.com/v1/forecast?latitude=51.50&longitude=-0.12&current_weather=true&temperature_unit=fahrenheit"
    
    response = requests.get(url)
    data = response.json()
    current_weather = data['current_weather']
    
    return jsonify({
        "city": "London", # <--- CHANGED NAME
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)