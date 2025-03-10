///////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////Find Normalized Difference Vegetation Index (NDVI) as a proxy for vegetation health//////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////
//Import Landsat 9 image collection
var l9 = ee.ImageCollection('ee.ImageCollection("LANDSAT/LC09/C02/T1_TOA');

//Area of interest (example is LA County)
var county = ee.FeatureCollection('projects/servir-sco-assets/assets/LosAngeles_County')
//Make the inside of the geometry transparent
var fc = ee.FeatureCollection(county).style({fillColor:'00000000'})

//Filtering Landsat Image Collection for different years to derive the 
//Normalized Difference Vegetation Index (proxy for vegetation health)

//DRY YEAR - - California experienced a three-year drought from 2020 to 2022, which was 
//the driest period on record for the state
var l9_2022_ = l9.filterDate('2022-01-01', '2022-02-28').filterBounds(county);

//WET SEASON 22-23, BUT DRY in the beginning of the year
var l9_2023_ = l9.filterDate('2023-01-01', '2023-02-28').filterBounds(county);

//VERY DRY YEAR
var l9_2024_ = l9.filterDate('2024-01-01', '2024-02-28').filterBounds(county);

//DRY January - Fires Occurred
var l9_2025_ = l9.filterDate('2025-01-01', '2025-01-11').filterBounds(county);

//CloudScore - this is to filter clouds from each years' worth of images
//2022
var withCloudiness22 = l9_2022_.map(function(image) {
  var cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud');
  var cloudiness = cloud.reduceRegion({
    reducer: 'mean', 
    geometry: county, 
    scale: 30,
    maxPixels: 1e13
  });
  return image.set(cloudiness);
});
//Apply the filter to the 2022 image collection
var filteredCollection2022 = withCloudiness22.filter(ee.Filter.lt('cloud', 20));
print(filteredCollection2022, '2022');

//Cloudscore 2023
var withCloudiness23 = l9_2023_.map(function(image) {
  var cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud');
  var cloudiness = cloud.reduceRegion({
    reducer: 'mean', 
    geometry: county, 
    scale: 30,
    maxPixels: 1e13
  });
  return image.set(cloudiness);
});
//Apply the filter to the 2023 image collection
var filteredCollection2023 = withCloudiness23.filter(ee.Filter.lt('cloud', 20));
print(filteredCollection2023, '2023');

//CloudScore 2024
var withCloudiness24 = l9_2024_.map(function(image) {
  var cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud');
  var cloudiness = cloud.reduceRegion({
    reducer: 'mean', 
    geometry: county, 
    scale: 30,
    maxPixels: 1e13
  });
  return image.set(cloudiness);
});
//Apply the filter to the 2024 image collection
var filteredCollection2024 = withCloudiness24.filter(ee.Filter.lt('cloud', 20));
print(filteredCollection2024, '2024');

//CloudScore 2025
var withCloudiness25 = l9_2025_.map(function(image) {
  var cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud');
  var cloudiness = cloud.reduceRegion({
    reducer: 'mean', 
    geometry: county, 
    scale: 30,
    maxPixels: 1e13
  });
  return image.set(cloudiness);
});
//Apply the filter to the 2022 image collection
var filteredCollection2025 = withCloudiness25.filter(ee.Filter.lt('cloud', 30));
print(filteredCollection2025, '2025');

//Create NDVI from the CloudScore filtered Landsat collections

//Determine colorscale for NDVI results
var ndviParams = {min: -1, max: 1, palette: ['blue', 'white', 'green']};

//NDVI 2022
var b4_22 = filteredCollection2022.select('B4');
var b4_22_ = b4_22.mean();//take mean of band 4 across all 2022 Landsat images
print(b4_22_, 'b4_22')
var b5_22 = filteredCollection2022.select('B5');
var b5_22_ = b5_22.mean();//take mean of band 5 across all 2022 Landsat images
print(b5_22_, 'b5_22')
var ndvi2022 = b5_22_.subtract(b4_22_).divide(b5_22_.add(b4_22_)).rename('NDVI');
Map.addLayer(ndvi2022, ndviParams, 'ndvi 2022')
print(ndvi2022, 'ndvi2022', true)

//NDVI 2023
var b4_23 = filteredCollection2023.select('B4');
var b4_23_ = b4_23.mean();
print(b4_23_, 'b4_23')
Map.addLayer(b4_23_, {}, 'b4 23', false)
var b5_23 = filteredCollection2023.select('B5');
var b5_23_ = b5_23.mean();
print(b5_23_, 'b5_23')
Map.addLayer(b5_23_, {}, 'b5 23', false)
var ndvi2023 = b5_23_.subtract(b4_23_).divide(b5_23_.add(b4_23_)).rename('NDVI').clip(county);
Map.addLayer(ndvi2023, ndviParams, 'ndvi 2023', true)
print(ndvi2023, 'ndvi2023')

//NDVI 2024
var b4_24 = filteredCollection2024.select('B4');
var b4_24_ = b4_24.mean();
print(b4_24_, 'b4_24')
Map.addLayer(b4_24_, {}, 'b4 24', false)
var b5_24 = filteredCollection2024.select('B5');
var b5_24_ = b5_24.mean();
print(b5_24_, 'b5_24')
Map.addLayer(b5_24_, {}, 'b5 24', false)
var ndvi2024 = b5_24_.subtract(b4_24_).divide(b5_24_.add(b4_24_)).rename('NDVI');
Map.addLayer(ndvi2024, ndviParams, 'ndvi 2024', true)
print(ndvi2024, 'ndvi2024')

//NDVI 2025
var b4_25 = filteredCollection2025.select('B4');
var b4_25_ = b4_25.mean();
print(b4_25_, 'b4_25')
Map.addLayer(b4_25_, {}, 'b4 25', false)
var b5_25 = filteredCollection2025.select('B5');
var b5_25_ = b5_25.mean();
print(b5_25_, 'b5_25')
Map.addLayer(b5_25_, {}, 'b5 25', false)
var ndvi2025 = b5_25_.subtract(b4_25_).divide(b5_25_.add(b4_25_)).rename('NDVI');
Map.addLayer(ndvi2025, ndviParams, 'ndvi 2025', true)
print(ndvi2025, 'ndvi2025')

//FIND THE CHANGE IN NDVI FROM ONE YEAR TO ANOTHER
//what the results will look like:
var changeParams = {min: -1, max: 1, palette: ['blue', 'white', 'orange']} //change - orange if it was wetter in 2022 than 2024

//Change from 2022 to 2024
var ndviChange_22_24 = ndvi2024.subtract(ndvi2022).rename('NDVIchange22_24')
print(ndviChange_22_24, 'ndvi change 22 24')
Map.addLayer(ndviChange_22_24, changeParams, 'NDVI change 22 24')

//Overlay transparent LA County boundary with an outline over the results
Map.addLayer(fc, {}, 'LA county')
