from datetime import datetime

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Replace this with your actual API key from OpenWeatherMap
API_KEY = "91b6ad22996f45c3913cfffd79178a85"

@app.route('/weather')
def get_weather():
    # 1. Get the city name from the user's request (e.g., /weather?city=Miami)
    city = request.args.get('city')
    # 1. Catch the unit preference (default to metric if not sent)
    unit = request.args.get('units', 'metric')
    
    if not city:
        return jsonify({"error": "Please provide a city name"}), 400

    # 2. Build the URL for the 'Grocery Store' (OpenWeatherMap)
    # units=metric gives us Celsius. Change to 'imperial' for Fahrenheit.
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
    
    # 3. Send the runner to get the data
    response = requests.get(url)
    print(f"Requesting weather data for {city} from OpenWeatherMap...")
    data = response.json()
    print(data)
    

    # 4. If the city wasn't found, tell the user
    if data.get("cod") != 200:
        return jsonify({"error": "City not found"}), 404
    # 3. Use a symbol based on the unit
    symbol = "°C" if unit == "metric" else "°F"
    
    # 5. Pick out only the 'ingredients' we want to show
# Inside get_weather() in backend.py
    
    # 1. Convert the timestamps
    # we use 'fromtimestamp' to turn that big number into a Python time object
    sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p')
    sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p')

    weather_info = {
        "city": data["name"],
        "temperature": f"{data['main']['temp']}{symbol}",
        "feels_like": f"{data['main']['feels_like']}{symbol}",
        "humidity": f"{data['main']['humidity']}%",
        "wind": f"{data['wind']['speed']} m/s",
        "condition": data["weather"][0]["description"].title(),
        "sunrise": sunrise_time, # NEW
        "sunset": sunset_time,   # NEW
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"]
    }    
    
    return jsonify(weather_info)

@app.route('/forecast')
def get_forecast():
    city = request.args.get('city')
    unit = request.args.get('units', 'metric')
    
    # New URL for Forecast data
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"
    
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != "200":
        return jsonify({"error": "Forecast not found"}), 404

    # We only want the next 8 data points (8 * 3 hours = 24 hours)
    forecast_list = []
    for entry in data['list'][:8]:
        forecast_list.append({
            "time": entry['dt_txt'].split(" ")[1][:5], # Just the HH:MM
            "temp": entry['main']['temp']
        })
    
    return jsonify(forecast_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)