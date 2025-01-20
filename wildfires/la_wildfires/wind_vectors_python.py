import ee
import geemap

# Initialize the Earth Engine
ee.Authenticate()
ee.Initialize(project='') #enter your cloud project name

# Define the collection and filter by bounding box and time range
collection = ee.ImageCollection("NOAA/NWS/RTMA")
bounding_box = ee.Geometry.BBox(-125, 25, -65, 50)  # Example bounding box for the US
start_date = '2023-01-01'
end_date = '2023-01-31'

# Filter the collection
filtered_collection = collection.filterBounds(bounding_box).filterDate(start_date, end_date)

# Get the first image from the filtered collection and select 'UGRD' and 'VGRD' bands
uv0 = filtered_collection.select(['UGRD', 'VGRD']).first()

# Define the region and scale
region = bounding_box
scale = 1000  # Adjust as needed
num_pixels = 10000

# Sample the image
samples = uv0.rename(['u', 'v']).sample(
    region=region,
    scale=scale,
    numPixels=num_pixels,
    geometries=True
)

# Scale vector for plotting
scale_vector = 0.1

# Function to create vectors
def create_vector(feature):
    u = ee.Number(feature.get('u')).multiply(scale_vector)
    v = ee.Number(feature.get('v')).multiply(scale_vector)
    origin = feature.geometry()
    
    # Translate
    proj = origin.projection().translate(u, v)
    end = ee.Geometry.Point(origin.transform(proj).coordinates())
    
    # Construct line
    geom = ee.Algorithms.GeometryConstructors.LineString([origin, end], None, True)
    return feature.setGeometry(geom)

# Map the vector creation function
vectors = samples.map(create_vector)

# Visualize the data
Map = geemap.Map()
Map.addLayer(uv0.pow(2).reduce(ee.Reducer.sum()).sqrt(), 
             {'palette': ['#440154', '#31688e', '#35b779', '#fde725'], 'min': 0, 'max': 10}, 
             'UV (speed)', True)
Map.addLayer(vectors.style({'color': 'white', 'width': 1}), {}, 'UV (vectors)')
Map.addLayer(samples.style({'pointSize': 1, 'color': 'red'}), {}, 'UV (samples)', True, 0.7)

# Add the bounding box to the map
Map.addLayer(bounding_box, {}, 'Bounding Box')

# Display the map
Map.centerObject(region)
Map
