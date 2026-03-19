import streamlit as st
import requests

if 'history' not in st.session_state:
    st.session_state.history = []
    
def set_bg_color(condition):
    color = "#f0f2f6"  # Default light grey
    if "Clear" in condition:
        color = "#81D4FA"  # Light sunny yellow
    elif "Rain" in condition or "Drizzle" in condition:
        color = "#CFD8DC"  # Rainy grey-blue
    elif "Clouds" in condition:
        color = "#ECEFF1"  # Cloudy white-grey
    
    # This "injects" custom styling into the page
    st.markdown(
        f"""
        <style>
        /* 1. Change the main background */
        .stApp {{
            background-color: {color};
        }}
        
        /* 2. Remove the top padding (The white space fix) */
        .block-container {{
            padding-top: 0rem;
            padding-bottom: 0rem;
        }}
        
        /* 3. Make the header transparent so it doesn't block the color */
        header {{
            visibility: hidden;
        }}
        
        /* 4. Remove any extra gap at the top */
        #root > div:nth-child(1) > div > div > div > div > section > div {{
            padding-top: 0px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the page title
st.set_page_config(page_title="My Weather App")

st.title("🌦️ Real-Time Weather App")
# 1. Create the Sidebar
st.sidebar.header("Settings")
unit_choice = st.sidebar.radio("Select Temperature Unit:", ["Celsius", "Fahrenheit"])

st.sidebar.markdown("---")
st.sidebar.subheader("Recent Searches")
for h_city in st.session_state.history:
    st.sidebar.write(f"📍 {h_city}")

# Convert the choice to the word Flask expects
unit_code = "metric" if unit_choice == "Celsius" else "imperial"
st.write("Enter a city name below to get the current weather.")

# 1. The Input Box (The Order)
city = st.text_input("City Name", placeholder="e.g. New York")

if st.button("Get Weather"):
    if city:
        # 2. Call our Flask 'Kitchen'
        # We send the city name to our backend running on port 5000
        try:
            response = requests.get(f"http://127.0.0.1:5000/weather?city={city}&units={unit_code}")
            data = response.json()
              
            if response.status_code == 200:
                if data['city'] not in st.session_state.history:
                    st.session_state.history.insert(0, data['city']) # Add to the top
                # Keep only the last 5 searches
                st.session_state.history = st.session_state.history[:5]
                
                set_bg_color(data['condition'])
                st.success(f"Weather in {data['city']}")
            
                # 1. Create 4 columns for our metrics
                m1, m2, m3, m4 = st.columns(4)
                
                with m1:
                    st.metric("Temperature", data['temperature'])
                with m2:
                    st.metric("Feels Like", data['feels_like'])
                with m3:
                    st.metric("Humidity", data['humidity'])
                with m4:
                    st.metric("Wind Speed", data['wind'])
                
                # 2. Condition and Icon below the metrics
                icon = "☀️" if "Clear" in data['condition'] else "☁️"
                if "Rain" in data['condition']: icon = "🌧️"
                st.markdown(f"### {icon} {data['condition']}")

                # 1. Add a visual separator
                st.markdown("---")
                
                # 2. Use columns for Sunrise and Sunset
                s1, s2 = st.columns(2)
                with s1:
                    st.write(f"🌅 **Sunrise:** {data['sunrise']}")
                with s2:
                    st.write(f"🌇 **Sunset:** {data['sunset']}")
                
                # Add a Map! 
                # Streamlit maps need a "dataframe" or a simple dictionary of coordinates
                map_data = {"lat": [data['lat']], "lon": [data['lon']]}
                st.map(map_data)
                
                # --- NEW: Forecast Chart Section ---
                st.markdown("---")
                st.subheader("Temperature Trend (Next 24 Hours)")
                
                forecast_res = requests.get(f"http://127.0.0.1:5000/forecast?city={city}&units={unit_code}")
                
                if forecast_res.status_code == 200:
                    forecast_data = forecast_res.json()
                    
                    # Prepare data for the chart
                    # Streamlit charts love dictionaries where keys are the columns
                    chart_dict = {
                        "Time": [item["time"] for item in forecast_data],
                        "Temp": [item["temp"] for item in forecast_data]
                    }
                    
                    # Display the line chart
                    st.line_chart(data=chart_dict, x="Time", y="Temp")
                else:
                    st.warning("Could not load forecast chart.")
            else:
                st.error(f"Error: {data.get('error', 'Something went wrong')}")
        
        except Exception as e:
            st.error("Could not connect to the backend. Is Flask running?")
    else:
        st.warning("Please enter a city name first!")

