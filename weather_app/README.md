# 🌦️ Real-Time Full-Stack Weather Dashboard

A sophisticated, interactive weather application built using a **Flask API** backend and a **Streamlit** frontend. This project demonstrates a complete data pipeline: fetching live data from an external provider, processing it through a custom server, and displaying it via a modern web interface.

## 🚀 Features
- **Live Data:** Fetches real-time weather details from the OpenWeatherMap API.
- **Dynamic Metrics:** Displays Temperature, "Feels Like," Humidity, and Wind Speed.
- **Visual Analytics:** Includes an interactive 24-hour temperature trend chart.
- **Geospatial Mapping:** Built-in map showing the exact coordinates of the searched city.
- **Astronomy Data:** Automated conversion of Unix timestamps to show local Sunrise and Sunset times.
- **Adaptive UI:** Custom CSS-injected background that changes color based on weather conditions (Clear, Clouds, Rain).
- **Search History:** Sidebar tracking for the last 5 searched cities.
- **Unit Toggle:** Switch between Celsius and Fahrenheit on the fly.

## 🛠️ Tech Stack
- **Backend:** Python, Flask (RESTful API)
- **Frontend:** Streamlit (Data Dashboard)
- **Data Source:** OpenWeatherMap API
- **Styling:** Custom CSS & Streamlit Layouts

## ⚙️ Installation & Setup

1. **Clone the project** or create a folder named `weather_app`.
2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate