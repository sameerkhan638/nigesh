# Parameters
COVERAGE_RADIUS = 1500  # in meters
MAX_TOWERS = 10
GRID_SPACING = 1000  # meters

st.set_page_config(page_title="Mumbai Cell Tower Optimization", layout="wide")

st.title("📡 Mumbai Cell Tower Optimization")
st.markdown("This app uses a greedy algorithm to place cell towers for maximum population coverage in Mumbai.")

# Step 1: Mumbai boundary (approximate)
st.subheader("Step 1: Define Mumbai Boundary")
mumbai_boundary_coords = [
    (72.775, 19.002), (72.775, 19.30), (72.986, 19.30), (72.986, 19.002)
]
city_polygon = Polygon(mumbai_boundary_coords)
city_gdf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[city_polygon])

# Step 2: Simulate population
st.subheader("Step 2: Simulate Population Points")
population_points = []
np.random.seed(42)
minx, miny, maxx, maxy = city_polygon.bounds

for _ in range(500):
    while True:
        x = np.random.uniform(minx, maxx)
        y = np.random.uniform(miny, maxy)
        pt = Point(x, y)
        if city_polygon.contains(pt):
            weight = np.random.randint(50, 500)
            population_points.append((pt, weight))
            break

pop_gdf = gpd.GeoDataFrame(
    {"population": [w for _, w in population_points]},
    geometry=[pt for pt, _ in population_points],
    crs="EPSG:4326"
)

# Step 3: Project to meters
pop_gdf = pop_gdf.to_crs(epsg=3857)
city_proj = city_gdf.to_crs(epsg=3857)
city_polygon_proj = city_proj.geometry.iloc[0]

# Step 4: Generate candidate towers
st.subheader("Step 3: Generate Candidate Tower Locations")
minx, miny, maxx, maxy = city_polygon_proj.bounds
x_coords = np.arange(minx, maxx, GRID_SPACING)
y_coords = np.arange(miny, maxy, GRID_SPACING)

candidate_points = []
for x in x_coords:
    for y in y_coords:
        pt = Point(x, y)
        if city_polygon_proj.contains(pt):
            candidate_points.append(pt)

candidates_gdf = gpd.GeoDataFrame(geometry=candidate_points, crs="EPSG:3857")

# Step 5: Greedy Optimization
st.subheader("Step 4: Optimize Tower Placement")
covered = set()
towers = []

for _ in range(MAX_TOWERS):
    best_score = 0
    best_tower = None
    best_covered = set()

    for idx, tower in candidates_gdf.iterrows():
        buffer = tower.geometry.buffer(COVERAGE_RADIUS)
        within = pop_gdf[pop_gdf.geometry.within(buffer)]
        new_covered = set(within.index.tolist()) - covered
        score = within.loc[list(new_covered)]["population"].sum()

        if score > best_score:
            best_score = score
            best_tower = tower.geometry
            best_covered = new_covered

    if best_tower:
        towers.append(best_tower)
        covered |= best_covered

# Step 6: Folium Map
st.subheader("📍 Final Output Map")
m = folium.Map(location=[19.0760, 72.8777], zoom_start=11, tiles="cartodbpositron")

# Add towers
for tower in towers:
    lon, lat = gpd.GeoSeries([tower], crs="EPSG:3857").to_crs(epsg=4326).geometry[0].coords[0]
    folium.Circle(
        location=(lat, lon), radius=COVERAGE_RADIUS,
        color="blue", fill=True, fill_opacity=0.1
    ).add_to(m)
    folium.Marker(
        location=(lat, lon),
        icon=folium.Icon(color='blue')
    ).add_to(m)

# Add population
for _, row in pop_gdf.iterrows():
    lon, lat = gpd.GeoSeries([row.geometry], crs="EPSG:3857").to_crs(epsg=4326).geometry[0].coords[0]
    folium.CircleMarker(
        location=(lat, lon), radius=3,
        color="red", fill=True, fill_opacity=0.6
    ).add_to(m)

# Show map in Streamlit
st_data = st_folium(m, width=1200, height=600)
