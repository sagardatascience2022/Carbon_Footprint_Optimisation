import streamlit as st
import pandas as pd
import joblib
import folium
import openrouteservice
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import socket
import requests
from io import StringIO

# === 🌐 Internet Check ===
def internet_check():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except OSError:
        return False

if not internet_check():
    st.error("❌ No internet connection. Please check your network.")
    st.stop()

# === 🔐 API Keys ===
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjE3NjU3M2I4ZjlmMDQ2ZjY4YTcyNjNhM2U1ZDcyYWM2IiwiaCI6Im11cm11cjY0In0="  # This is a sample key, get your own from openrouteservice.org
WEATHER_API_KEY = "24c13097b08b6d33810e03d052c6f3e3"  # This is a sample key, get your own from openweathermap.org

client = openrouteservice.Client(key=ORS_API_KEY)
model = joblib.load("carbon_emission_model.pkl")

# === Constants ===
mileage = {"Bike": 40, "Car": 15, "Van": 12, "Truck": 5}
co2_factor = {"Bike": 2.3, "Car": 2.3, "Van": 2.6, "Truck": 2.7}

# === 🌦️ Get Weather by City ===
def get_weather_by_city(city_name):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url, timeout=10)
        if res.status_code == 401:
            st.error("❌ Invalid OpenWeatherMap API key. Please check your API key.")
            return "⚠️ Weather data not available (API key error)"
        elif res.status_code != 200:
            st.warning(f"⚠️ Weather API error: {res.status_code}")
            return "⚠️ Weather data not available (API error)"
        
        data = res.json()
        if 'weather' not in data or 'main' not in data:
            st.warning("⚠️ Unexpected weather data format")
            return "⚠️ Weather data format error"
            
        desc = data['weather'][0]['description'].title()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return f"{desc}, {temp}°C, Humidity: {humidity}%"
    except requests.Timeout:
        return "⚠️ Weather data not available (timeout)"
    except Exception as e:
        st.error(f"❌ Weather API error: {str(e)}")
        return "⚠️ Weather data not available (error)"

# === Session State Init ===
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "dashboard_data" not in st.session_state:
    st.session_state.dashboard_data = []

# === Streamlit UI ===
st.set_page_config(page_title="CO₂ Emission Estimator", layout="wide")
st.title("🚛 Carbon Footprint Optimization in Supply Chain Logistics")
st.header("📍 Enter Start and Destination Locations")

# === Input Fields ===
col1, col2 = st.columns(2)
with col1:
    start_place = st.text_input("Start Location", value="Hyderabad")
with col2:
    end_place = st.text_input("Destination Location", value="Warangal")

st.markdown("### 🚚 Delivery & Environment Details")
col3, col4 = st.columns(2)
with col3:
    vehicle = st.selectbox("Vehicle Type", ["Bike", "Car", "Van", "Truck"])
    weight = st.number_input("Cargo Weight (kg)", min_value=0)
with col4:
    traffic = st.selectbox("Traffic Level", ["Low", "Medium", "High"])
    weather = st.selectbox("Weather Condition (User Choice)", ["Clear", "Rainy"])
    fuel_price = st.number_input("Fuel Price (₹/L)", min_value=50, value=100)

# === Predict Button ===
if st.button("🔍 Predict CO₂ and Show Route"):
    st.session_state.show_results = True

# === Prediction Section ===
if st.session_state.show_results:
    try:
        geolocator = Nominatim(user_agent="geoapi", timeout=10)  # Increased timeout to 10 seconds
        
        with st.spinner(f"Finding coordinates for {start_place}..."):
            start_location = geolocator.geocode(start_place)
            if not start_location:
                st.error(f"⚠️ Could not find location: {start_place}. Please check spelling.")
                st.stop()
        
        with st.spinner(f"Finding coordinates for {end_place}..."):
            end_location = geolocator.geocode(end_place)
            if not end_location:
                st.error(f"⚠️ Could not find location: {end_place}. Please check spelling.")
                st.stop()

        start_lat, start_lon = start_location.latitude, start_location.longitude
        end_lat, end_lon = end_location.latitude, end_location.longitude
        start_coords = (start_lon, start_lat)
        end_coords = (end_lon, end_lat)

        start_weather = get_weather_by_city(start_place)
        end_weather = get_weather_by_city(end_place)

        st.info(f"📍 **Weather at Start ({start_place})**: {start_weather}")
        st.info(f"📍 **Weather at Destination ({end_place})**: {end_weather}")

        route = client.directions(
            coordinates=[start_coords, end_coords],
            profile='driving-car',
            format='geojson'
        )

        distance_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000
        duration_min = route['features'][0]['properties']['segments'][0]['duration'] / 60

        traffic_map = {"Low": 0, "Medium": 1, "High": 2}
        traffic_level = traffic_map[traffic]
        weather_level = 0 if weather == "Clear" else 1
        vehicle_encoded = ["Bike", "Car", "Van", "Truck"].index(vehicle)

        input_data = [[distance_km, traffic_level, weight, weather_level, vehicle_encoded, duration_min]]
        prediction = model.predict(input_data)[0]

        fuel_used = distance_km / mileage[vehicle]
        fuel_cost = fuel_used * fuel_price
        alt_emission = fuel_used * co2_factor[vehicle]

        st.markdown("### ✅ Results")
        st.success(f"🌍 ML-Predicted CO₂ Emission: **{prediction:.2f} kg**")
        st.info(f"⛽ Fuel Used: **{fuel_used:.2f} L** | 💰 Fuel Cost: ₹{fuel_cost:.2f}")
        st.warning(f"📏 CO₂ (Formula Based): **{alt_emission:.2f} kg**")
        st.write(f"📏 Distance: **{distance_km:.2f} km**, 🕒 Time: **{duration_min:.1f} mins**")

        st.subheader("🗺️ Route Map")
        coords = route['features'][0]['geometry']['coordinates']
        coords = [[lat, lon] for lon, lat in coords]

        m = folium.Map(location=coords[0], zoom_start=8)
        folium.PolyLine(coords, color="green", weight=5, tooltip="Delivery Route").add_to(m)
        folium.Marker(coords[0], tooltip="Start", icon=folium.Icon(color="blue")).add_to(m)
        folium.Marker(coords[-1], tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)
        st_folium(m, width=700, height=500)

        # === Save to Dashboard ===
        record = {
            "Start_Location": start_place,
            "End_Location": end_place,
            "Distance_km": distance_km,
            "Time_min": duration_min,
            "Traffic_Level": traffic,
            "User_Selected_Weather": weather,
            "Vehicle": vehicle,
            "Cargo_Weight_kg": weight,
            "Fuel_Used_L": fuel_used,
            "Fuel_Cost_Rs": fuel_cost,
            "Predicted_CO2_kg": prediction,
            "Formula_CO2_kg": alt_emission
        }
        st.session_state.dashboard_data.append(record)

        # === Download This Delivery Only ===
        single_df = pd.DataFrame([record])
        single_csv = StringIO()
        single_df.to_csv(single_csv, index=False)
        st.download_button("📥 Download This Delivery CSV", data=single_csv.getvalue(),
                           file_name="delivery_report.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Failed to calculate route or prediction: {e}")

# === 📊 Multi-Delivery Dashboard ===
st.markdown("---")
st.markdown("## 📊 Delivery Dashboard")

if len(st.session_state.dashboard_data) == 0:
    st.info("No delivery records yet. Run a prediction to see data here.")
else:
    dashboard_df = pd.DataFrame(st.session_state.dashboard_data)
    st.dataframe(dashboard_df)

    st.subheader("📈 CO₂ Emission Per Delivery")
    st.bar_chart(dashboard_df["Predicted_CO2_kg"])

    st.subheader("💰 Fuel Cost Per Delivery")
    st.bar_chart(dashboard_df["Fuel_Cost_Rs"])

    st.subheader("📏 Distance vs Time")
    st.line_chart(dashboard_df[["Distance_km", "Time_min"]])

    # === Dashboard CSV Download ===
    dash_csv = StringIO()
    dashboard_df.to_csv(dash_csv, index=False)
    st.download_button("📥 Download Full Dashboard CSV", data=dash_csv.getvalue(),
                       file_name="delivery_dashboard.csv", mime="text/csv")

    # === Clear Dashboard Option ===
    if st.button("🔄 Clear All Dashboard Records"):
        st.session_state.dashboard_data = []
        st.success("✅ Dashboard cleared.")







