# Mumbai boundary coordinates (simplified polygon for demo purposes)
mumbai_boundary_coords = [
    (19.2716, 72.8530),
    (19.2465, 72.8777),
    (19.2183, 72.8580),
    (19.1910, 72.8340),
    (19.1603, 72.8613),
    (19.1510, 72.8495),
    (19.1702, 72.8122),
    (19.2117, 72.8179),
    (19.2292, 72.7955),
    (19.2637, 72.8182),
    (19.2716, 72.8530)
]

# Create a Shapely Polygon (note: Polygon expects (lon, lat))
city_polygon = Polygon([(lon, lat) for lat, lon in mumbai_boundary_coords])

# Streamlit UI
st.set_page_config(page_title="Mumbai Location Checker", layout="centered")
st.title("📍 Mumbai Location Checker")

st.markdown("Enter a latitude and longitude to check if it's inside Mumbai boundary.")

# Input fields
lat = st.number_input("Enter Latitude:", value=19.0760, format="%.6f")
lon = st.number_input("Enter Longitude:", value=72.8777, format="%.6f")

# Button to check location
if st.button("Check Location"):
    point = Point(lon, lat)
    if city_polygon.contains(point):
        st.success("✅ This point is **INSIDE** Mumbai.")
    else:
        st.error("❌ This point is **OUTSIDE** Mumbai.")

    # Create map centered at the input location
    m = folium.Map(location=[lat, lon], zoom_start=12)

    # Add Mumbai boundary to map
    folium.PolyLine(mumbai_boundary_coords, color="blue", weight=2.5).add_to(m)

    # Add marker for the input point
    folium.Marker(
        [lat, lon],
        popup="Your Location",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Display the map in Streamlit
    folium_static(m)
