// Function to visualize wind vectors for a given region and date range
function visualize_wind_vectors(region, start_date, end_date, num_samples) {
  // Load wind data
  var uv = ee.ImageCollection('NOAA/GFS0P25')
    .select(['u_component_of_wind_10m_above_ground', 'v_component_of_wind_10m_above_ground'])
    .filterDate(start_date, end_date);

  // Get the first image and rename bands
  var uv0 = uv.first().rename(['u', 'v']);

  // Sample wind data
  var scale = 25000; // 25 km per pixel
  var samples = uv0.sample({
    region: region,
    scale: scale,
    numPixels: num_samples,
    geometries: true
  });

  // Create wind vectors (arrows)
  var createArrows = function(feature) {
    var u = feature.get('u');
    var v = feature.get('v');
    var coords = ee.Geometry(feature.geometry()).coordinates();
    var scaleFactor = 0.1; // Normalize arrow length
    var arrowEnd = [
      ee.Number(coords.get(0)).add(ee.Number(u).multiply(scaleFactor)),
      ee.Number(coords.get(1)).add(ee.Number(v).multiply(scaleFactor))
    ];
    return ee.Feature(ee.Geometry.LineString([coords, arrowEnd]), feature.toDictionary());
  };

  // Apply the function to create arrows
  var arrows = samples.map(createArrows);

  // Add arrows to the map
  Map.addLayer(arrows, {color: 'blue'}, 'Wind Vectors');
}

// Example: Visualize wind vectors for California
var california = ee.FeatureCollection('TIGER/2018/States')
  .filter(ee.Filter.eq('NAME', 'California'))
  .geometry();
  

// Set the  dates
var startDate= '2025-01-07'
var endDate = ee.Date(Date.now());

visualize_wind_vectors(california, startDate, endDate, 500);
