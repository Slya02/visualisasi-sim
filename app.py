import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

st.set_page_config(layout="wide")
st.title("Analisis Penjualan Mobil di USA")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("carSales.csv", delimiter=';')
    df.columns = df.columns.str.strip()  # hilangkan spasi ekstra
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    return df

df = load_data()

# 1. Asal Negara (Peta Lokasi Dealer)
st.subheader("1. Asal Wilayah Penjualan Mobil")
geolocator = Nominatim(user_agent="dealer_locator")
regions = df['Dealer_Region'].dropna().unique()

locations = []
for region in regions:
    try:
        loc = geolocator.geocode(region + ", USA")
        if loc:
            locations.append({'region': region, 'lat': loc.latitude, 'lon': loc.longitude})
        time.sleep(1)
    except:
        continue

m = folium.Map(location=[39.5, -98.35], zoom_start=4)
for loc in locations:
    folium.Marker([loc['lat'], loc['lon']], popup=loc['region']).add_to(m)
st_folium(m, width=700, height=500)

# 2. Brand Pesaing Terbesar
st.subheader("2. Brand Mobil Pesaing Terbesar")
top3 = df['Company'].value_counts().nlargest(3)
fig1, ax1 = plt.subplots()
ax1.pie(top3, labels=top3.index, autopct='%1.1f%%', explode=[0.05]*3, shadow=True)
ax1.set_title("Top 3 Brand Mobil Terlaris")
st.pyplot(fig1)

# 3. Brand Teratas per Region
st.subheader("3. Distribusi 5 Brand Terlaris per Region")
top5 = df['Company'].value_counts().nlargest(5).index.tolist()
df_top5 = df[df['Company'].isin(top5)]
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.countplot(data=df_top5, y='Dealer_Region', hue='Company', ax=ax2)
ax2.set_title("Top 5 Brand per Wilayah")
st.pyplot(fig2)

# 4. Body Style Populer per Region
st.subheader("4. Tipe Mobil Terpopuler per Region")
region_body = df.groupby(['Dealer_Region', 'Body_Style']).size().reset_index(name='Count')
top3_body = region_body.sort_values(['Dealer_Region', 'Count'], ascending=[True, False]).groupby('Dealer_Region').head(3)
g = sns.FacetGrid(top3_body, col='Dealer_Region', col_wrap=3, height=4)
g.map_dataframe(sns.barplot, x='Count', y='Body_Style', hue='Body_Style', dodge=False)
g.set_titles("{col_name}"); g.set_axis_labels("Jumlah", "Body Style")
st.pyplot(g.fig)

# 5. Rata-rata Harga per Brand/Region
st.subheader("5. Rata-rata Harga per Brand per Region")
avg_price = df_top5.groupby(['Dealer_Region', 'Company'])['Price'].mean().reset_index()
fig3, ax3 = plt.subplots(figsize=(12, 6))
sns.barplot(data=avg_price, x='Dealer_Region', y='Price', hue='Company', ax=ax3)
ax3.set_title("Harga Rata-rata Mobil per Brand/Region")
st.pyplot(fig3)

# 6. Tren Penjualan Tahunan
st.subheader("6. Tren Penjualan per Tahun")
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.to_period('M').astype(str)
df = df[df['Year'] >= 2022]
available_years = sorted(df['Year'].unique())
selected_year = st.selectbox("Pilih Tahun", available_years)
df_filtered = df[df['Year'] == selected_year]
trend = df_filtered.groupby(['Month', 'Dealer_Region']).size().reset_index(name='Total_Sales')
trend['Month'] = pd.to_datetime(trend['Month'])
trend = trend.sort_values('Month')
fig4, ax4 = plt.subplots(figsize=(12, 6))
sns.lineplot(data=trend, x='Month', y='Total_Sales', hue='Dealer_Region', marker='o', ax=ax4)
ax4.set_title(f"Tren Penjualan Mobil per Wilayah per Bulan - {selected_year}", fontsize=14, fontweight='bold')
ax4.set_xlabel("Bulan")
ax4.set_ylabel("Total Penjualan")
ax4.tick_params(axis='x', rotation=45) 
st.pyplot(fig4)
