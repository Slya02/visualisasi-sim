import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

st.set_page_config(layout="wide")
st.title("Analisis Wilayah Penjualan Mobil")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("carSales.csv", sep=';')
    df.columns = df.columns.str.strip()
    df['Dealer_Region'] = df['Dealer_Region'].str.strip()
    return df

sales_df = load_data()

# Peta Wilayah Penjualan
st.subheader("Peta Lokasi Dealer Berdasarkan Wilayah")

regions = sales_df['Dealer_Region'].dropna().unique()
geolocator = Nominatim(user_agent="dealer_locator")

locations = []
for region in regions:
    try:
        location = geolocator.geocode(region + ", USA")
        if location:
            locations.append({
                'region': region,
                'lat': location.latitude,
                'lon': location.longitude
            })
        time.sleep(1)
    except:
        continue

# Buat peta
map_dealers = folium.Map(location=[39.5, -98.35], zoom_start=4)

for loc in locations:
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=loc['region'],
        icon=folium.Icon(color='blue', icon='car', prefix='fa')
    ).add_to(map_dealers)

# Tampilkan di Streamlit
st_folium(map_dealers, width=700, height=500)
