# app.py
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")

st.title('New York City Taxi Fare Prediction App 🚕')

col1, col2, col3, col4 = st.columns(4)

with col1:
    pickup_datetime = st.date_input("Enter the pickup date", value=None, min_value=None, max_value=None)

with col2:
    pickup_address = st.text_input("Enter the pickup address", "Manhattan, New York, NY")

with col3:
    dropoff_address = st.text_input("Enter the dropoff address", "Brooklyn, New York, NY")

with col4:
    passenger_count = st.number_input("Enter the number of passengers", min_value=1, max_value=8, value=1, step=1)

api_url = "https://taxifare-sn3joh6ghq-ew.a.run.app/predict"

# Create a map

# Function to get coordinates
def get_coordinates(address):
    geolocator = Nominatim(user_agent="taxi_fare_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

if 'map' not in st.session_state:
    st.session_state['map'] = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

def update_map(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude, pickup_address, dropoff_address):
    # recreate the map
    st.session_state['map'] = folium.Map(location=[40.7128, -74.0060], zoom_start=10)
    folium.Marker(location=[pickup_latitude, pickup_longitude], popup='Pickup: ' + pickup_address).add_to(st.session_state['map'])
    folium.Marker(location=[dropoff_latitude, dropoff_longitude], popup='Dropoff: ' + dropoff_address).add_to(st.session_state['map'])
    folium.PolyLine(locations=[[pickup_latitude, pickup_longitude], [dropoff_latitude, dropoff_longitude]], color='blue').add_to(st.session_state['map'])


if 'predicted_fare' not in st.session_state:
    st.session_state['predicted_fare'] = None
    

    
# Submit button
if st.button('Get Fare Prediction'):
    pickup_latitude, pickup_longitude = get_coordinates(pickup_address)
    dropoff_latitude, dropoff_longitude = get_coordinates(dropoff_address)
    
    pickup_datetime = str(pickup_datetime)
    if pickup_latitude is None or dropoff_latitude is None:
        st.write("Error: Could not geocode one or both of the addresses.")
    else:
        params = {
            'pickup_latitude': pickup_latitude,
            'pickup_longitude': pickup_longitude,
            'dropoff_latitude': dropoff_latitude,
            'dropoff_longitude': dropoff_longitude,
            'passenger_count': passenger_count,
            'pickup_datetime': pickup_datetime
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            fare_prediction = response.json().get('fare', 'No prediction available')
            predicted_fare = fare_prediction
            update_map(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude, pickup_address, dropoff_address)
            st.session_state['predicted_fare'] = fare_prediction
            
        else:
            st.error("Error: Could not retrieve prediction")
            

        
st_folium(st.session_state['map'], width=1800, height=500)
        
if st.session_state['predicted_fare'] is not None:
    st.write(f"Predicted Fare: ${round(st.session_state['predicted_fare'], 2)}")
    
