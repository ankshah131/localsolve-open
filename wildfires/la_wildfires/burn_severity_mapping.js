
//===========================================================================================
//             BURN SEVERITY MAPPING USING THE NORMALIZED BURN RATIO (NBR)
//===========================================================================================
// Normalized Burn Ratio will be applied to imagery from before and after a wild fire. By
// calculating the difference afterwards (dNBR) Burn Severity is derived, showing the spatial
// impact of the disturbance. Imagery used in this process comes from either Sentinel-2 or 
// Landsat 8.
//===========================================================================================

//:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//                                    RUN A DEMO (optional)

// If you would like to run an example of mapping burn severity you can use the predefined 
// geometry below as well as the other predefined parameter settings. The code will take you
// to Los Angeles, CA, US where wildfires occurred in January 2025. 
// --> Remove the comment-symbol (//) below to so Earth Engine recognizes the polygon.

// var geometry = 
//     ee.Geometry.Polygon(
//         [[[-118.7341914264289, 34.1657598213888],
//           [-118.7341914264289, 33.99059095699506],
//           [-118.47326613346014, 33.99059095699506],
//           [-118.47326613346014, 34.1657598213888]]], null, false);

// Now hit Run to start the demo! 
// Do not forget to delete/outcomment this geometry before creating a new one!
//:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

//*******************************************************************************************
//                             SELECT YOUR OWN STUDY AREA   

// Use the polygon-tool in the top left corner of the map pane to draw the shape of your 
// study area. Single clicks add vertices, double-clicking completes the polygon.
// **CAREFUL**: Under 'Geometry Imports' (top left in map pane) uncheck the 
//                geometry box, so it does not block the view on the imagery later.

//*******************************************************************************************
//                                     SET TIME FRAME

// Set start and end dates of a period BEFORE the fire. Make sure it is long enough for 
// Sentinel-2 to acquire an image (repitition rate = 5 days). Adjust these parameters, if
// your ImageCollections (see Console) do not contain any elements.
var prefire_start = '2024-12-15';   
var prefire_end = '2025-01-05';

// Now set the same parameters for AFTER the fire.
var postfire_start = '2025-01-07';
var postfire_end = '2025-01-17';

// Used for Sentinel 2 cloud masking
var MAX_CLOUD_PROBABILITY = 65;

//*******************************************************************************************
//                            SELECT A SATELLITE PLATFORM

// You can select remote sensing imagery from two availible satellite sensors. 
// Consider details of each mission below to choose the data suitable for your needs.

// Landsat 8                             |  Sentinel-2 (A&B)
//-------------------------------------------------------------------------------------------
// launched:        February 11th, 2015  |  June 23rd, 2015 & March 7th, 2017
// repitition rate: 16 days              |  5 day (since 2017)
// resolution:      30 meters            |  10 meters 
// advantages:      longer time series   |  9 times higher spatial detail
//                  smaller export file  |  higher chance of cloud-free images

// SELECT one of the following:   'L8'  or 'S2' 

var platform = 'S2';               // <--- assign your choice to the platform variable

//*******************************************************************************************
//---->>> DO NOT EDIT THE SCRIPT PAST THIS POINT! (unless you know what you are doing) <<<---
//------------------->>> NOW HIT 'RUN' AT THE TOP OF THE SCRIPT! <<<-------------------------
//--> THE FINAL BURN SEVERITY PRODUCT WILL READY FOR DOWNLOAD ON THE RIGHT (UNDER TASKS) <---

//*******************************************************************************************


//---------------------------------- Translating User Inputs --------------------------------

// Print Satellite platform and dates to console
if (platform == 'S2' | platform == 's2') {
  var ImCol = 'COPERNICUS/S2_SR_HARMONIZED';
  var s2Clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY');
  var pl = 'Sentinel-2';
} else {
  var ImCol = 'LANDSAT/LC08/C02/T1_L2';
  var pl = 'Landsat 8';
}
print(ee.String('Data selected for analysis: ').cat(pl));
print(ee.String('Fire incident occurred between ').cat(prefire_end).cat(' and ').cat(postfire_start));

// Location
var area = ee.FeatureCollection(geometry);

// Set study area as map center.
Map.centerObject(area);

//----------------------- Select imagery by time and location -----------------------

var imagery = ee.ImageCollection(ImCol);

// In the following lines imagery will be collected in an ImageCollection, depending on the
// location of our study area, a given time frame and the ratio of cloud cover.
var prefireImCol = ee.ImageCollection(imagery
    // Filter by dates.
    .filterDate(prefire_start, prefire_end)
    // Filter by location.
    .filterBounds(area));
    
// Select all images that overlap with the study area from a given time frame
var postfireImCol = ee.ImageCollection(imagery
    // Filter by dates.
    .filterDate(postfire_start, postfire_end)
    // Filter by location.
    .filterBounds(area));
    
// Value scaling for Landsat 8 Collection 2
// Reflectance bands have new scaling factors in collection 2. 
// Collection 1 used a 0.0001 scale factor. Collection 2 uses a 2.75e-05 scale factor and -0.2 offset. 
// The thermal band also has new scale and offset factors. 
// The following code block defines a function to apply Collection 2 surface reflectance and temperature band scaling factors and maps it over an image collection.

var applyScaleFactors = function(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBand = image.select('ST_B10').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
              .addBands(thermalBand, null, true);
};

// Value scaling only to be applied for Landsat 8

if (platform == 'L8' | platform == 'l8') {
  var prefireImCol = prefireImCol.map(applyScaleFactors);
  var postfireImCol = postfireImCol.map(applyScaleFactors);
  }

// Add the clipped images to the console on the right
print("Pre-fire Image Collection: ", prefireImCol); 
print("Post-fire Image Collection: ", postfireImCol);

//------------------------------- Apply a cloud and snow mask -------------------------------

function maskClouds(img) {
  var clouds = ee.Image(img.get('cloud_mask')).select('probability');
  var isNotCloud = clouds.lt(MAX_CLOUD_PROBABILITY);
  return img.updateMask(isNotCloud);
}

function maskWater(img) {
  var scl = img.select('SCL');
  var water_mask = scl.neq(6); // Water is class 6
  return img.updateMask(water_mask);
}


// The masks for the 10m bands sometimes do not exclude bad data at
// scene edges, so we apply masks from the 20m and 60m bands as well.
function maskEdges(s2_img) {
  return s2_img.updateMask(
      s2_img.select('B8A').mask().updateMask(s2_img.select('B9').mask()));
}

// Function to mask clouds from the pixel quality band of Landsat 8 SR data.
function maskL8sr(image) {
  // Bits 3 and 4 are cloud shadow and snow, respectively. (eq(0))
  // Bit 6 is for clear conditions, indicating non-cloudy pixels (neq(0))
  var cloudShadowBitMask = 1 << 4;
  var snowBitMask = 1 << 5;
  var clearBitMask = 1 << 6;
  // Get the pixel QA band.
  var qa = image.select('QA_PIXEL');
  // All flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
      .and(qa.bitwiseAnd(snowBitMask).eq(0))
      .and(qa.bitwiseAnd(clearBitMask).neq(0));
  // Return the masked image, scaled to TOA reflectance, without the QA bands.
  return image.updateMask(mask)
      .select("SR_B.")
      .copyProperties(image, ["system:time_start"]);
}

// Apply platform-specific cloud mask
if (platform == 'S2' | platform == 's2') {
  // Join S2 SR with cloud probability dataset to add cloud mask.
  var prefires2SrWithCloudMask = ee.Join.saveFirst('cloud_mask').apply({
    primary: prefireImCol,
    secondary: s2Clouds,
    condition:
        ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'})
  });
  var postfires2SrWithCloudMask = ee.Join.saveFirst('cloud_mask').apply({
    primary: postfireImCol,
    secondary: s2Clouds,
    condition:
        ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'})
  });
  var prefire_CM_ImCol = ee.ImageCollection(prefires2SrWithCloudMask).map(maskClouds).map(maskWater);
  var postfire_CM_ImCol = ee.ImageCollection(postfires2SrWithCloudMask).map(maskClouds).map(maskWater);
  // var prefire_CM_ImCol = prefireImCol.map(maskS2sr);
  // var postfire_CM_ImCol = postfireImCol.map(maskS2sr);
} else {
  var prefire_CM_ImCol = prefireImCol.map(maskL8sr);
  var postfire_CM_ImCol = postfireImCol.map(maskL8sr);
}

//----------------------- Mosaic and clip images to study area -----------------------------

// This is especially important, if the collections created above contain more than one image
// (if it is only one, the mosaic() does not affect the imagery).

var pre_mos = prefireImCol.mosaic().clip(area);
var post_mos = postfireImCol.mosaic().clip(area);

var pre_cm_mos = prefire_CM_ImCol.mosaic().clip(area);
var post_cm_mos = postfire_CM_ImCol.mosaic().clip(area);

// Add the clipped images to the console on the right
print("Pre-fire True Color Image: ", pre_mos); 
print("Post-fire True Color Image: ", post_mos);

//------------------ Calculate NBR for pre- and post-fire images ---------------------------

// Apply platform-specific NBR = (NIR-SWIR2) / (NIR+SWIR2)
if (platform == 'S2' | platform == 's2') {
  var preNBR = pre_cm_mos.normalizedDifference(['B8', 'B12']);
  var postNBR = post_cm_mos.normalizedDifference(['B8', 'B12']);
} else {
  var preNBR = pre_cm_mos.normalizedDifference(['SR_B5', 'SR_B7']);
  var postNBR = post_cm_mos.normalizedDifference(['SR_B5', 'SR_B7']);
}


// Add the NBR images to the console on the right
//print("Pre-fire Normalized Burn Ratio: ", preNBR); 
//print("Post-fire Normalized Burn Ratio: ", postNBR);

//------------------ Calculate difference between pre- and post-fire images ----------------

// The result is called delta NBR or dNBR
var dNBR_unscaled = preNBR.subtract(postNBR);

// Scale product to USGS standards
var dNBR = dNBR_unscaled.multiply(1000);

// Add the difference image to the console on the right
print("Difference Normalized Burn Ratio: ", dNBR);

//==========================================================================================
//                                    ADD LAYERS TO MAP

// Add boundary.
Map.addLayer(area.draw({color: 'ffffff', strokeWidth: 5}), {},'Study Area');

//---------------------------------- True Color Imagery ------------------------------------

// Apply platform-specific visualization parameters for true color images
if (platform == 'S2' | platform == 's2') {
  var vis = {bands: ['B4', 'B3', 'B2'], max: 2000, gamma: 1.5};
} else {
  var vis = {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 0, max: 1, gamma: 2};
}

// Add the true color images to the map.
Map.addLayer(pre_mos, vis,'Pre-fire image');
Map.addLayer(post_mos, vis,'Post-fire image');

// Add the true color images to the map.
Map.addLayer(pre_cm_mos, vis,'Pre-fire True Color Image - Clouds masked');
Map.addLayer(post_cm_mos, vis,'Post-fire True Color Image - Clouds masked');

//--------------------------- Burn Ratio Product - Greyscale -------------------------------

var grey = ['white', 'black'];

// Remove comment-symbols (//) below to display pre- and post-fire NBR seperately
//Map.addLayer(preNBR, {min: -1, max: 1, palette: grey}, 'Prefire Normalized Burn Ratio');
//Map.addLayer(postNBR, {min: -1, max: 1, palette: grey}, 'Postfire Normalized Burn Ratio');

Map.addLayer(dNBR, {min: -1000, max: 1000, palette: grey}, 'dNBR greyscale');

//------------------------- Burn Ratio Product - Classification ----------------------------

// Define an SLD style of discrete intervals to apply to the image.
var sld_intervals =
  '<RasterSymbolizer>' +
    '<ColorMap type="intervals" extended="false" >' +
      '<ColorMapEntry color="#ffffff" quantity="-500" label="-500"/>' +
      '<ColorMapEntry color="#7a8737" quantity="-250" label="-250" />' +
      '<ColorMapEntry color="#acbe4d" quantity="-100" label="-100" />' +
      '<ColorMapEntry color="#0ae042" quantity="100" label="100" />' +
      '<ColorMapEntry color="#fff70b" quantity="270" label="270" />' +
      '<ColorMapEntry color="#ffaf38" quantity="440" label="440" />' +
      '<ColorMapEntry color="#ff641b" quantity="660" label="660" />' +
      '<ColorMapEntry color="#a41fd6" quantity="2000" label="2000" />' +
    '</ColorMap>' +
  '</RasterSymbolizer>';

// Add the image to the map using both the color ramp and interval schemes.
Map.addLayer(dNBR.sldStyle(sld_intervals), {}, 'dNBR classified');

// Seperate result into 8 burn severity classes
var thresholds = ee.Image([-1000, -251, -101, 99, 269, 439, 659, 2000]);
var classified = dNBR.lt(thresholds).reduce('sum').toInt();

Map.addLayer(classified, {}, 'Classified dNBR')

//==========================================================================================
//                              ADD BURNED AREA STATISTICS

// count number of pixels in entire layer
var allpix =  classified.updateMask(classified);  // mask the entire layer
var pixstats = allpix.reduceRegion({
  reducer: ee.Reducer.count(),               // count pixels in a single class
  geometry: area,
  scale: 30
  });
var allpixels = ee.Number(pixstats.get('sum')); // extract pixel count as a number


// create an empty list to store area values in
var arealist = [];

// create a function to derive extent of one burn severity class
// arguments are class number and class name
var areacount = function(cnr, name) {
 var singleMask =  classified.updateMask(classified.eq(cnr));  // mask a single class
 var stats = singleMask.reduceRegion({
  reducer: ee.Reducer.count(),               // count pixels in a single class
  geometry: area,
  scale: 30
  });
var pix =  ee.Number(stats.get('sum'));
var hect = pix.multiply(900).divide(10000);                // Landsat pixel = 30m x 30m --> 900 sqm
var perc = pix.divide(allpixels).multiply(10000).round().divide(100);   // get area percent by class and round to 2 decimals
arealist.push({Class: name, Pixels: pix, Hectares: hect, Percentage: perc});
};

// severity classes in different order
var names2 = ['NA', 'High Severity', 'Moderate-high Severity',
'Moderate-low Severity', 'Low Severity','Unburned', 'Enhanced Regrowth, Low', 'Enhanced Regrowth, High'];

// execute function for each class
for (var i = 0; i < 8; i++) {
  areacount(i, names2[i]);
  }

print('Burned Area by Severity Class', arealist, '--> click list objects for individual classes');

//==========================================================================================
//                                    ADD A LEGEND

// set position of panel
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }});
 
// Create legend title
var legendTitle = ui.Label({
  value: 'dNBR Classes',
  style: {fontWeight: 'bold',
    fontSize: '18px',
    margin: '0 0 4px 0',
    padding: '0'
    }});
 
// Add the title to the panel
legend.add(legendTitle);
 
// Creates and styles 1 row of the legend.
var makeRow = function(color, name) {
 
      // Create the label that is actually the colored box.
      var colorBox = ui.Label({
        style: {
          backgroundColor: '#' + color,
          // Use padding to give the box height and width.
          padding: '8px',
          margin: '0 0 4px 0'
        }});
 
      // Create the label filled with the description text.
      var description = ui.Label({
        value: name,
        style: {margin: '0 0 4px 6px'}
      });
 
      // return the panel
      return ui.Panel({
        widgets: [colorBox, description],
        layout: ui.Panel.Layout.Flow('horizontal')
      })};
 
//  Palette with the colors
var palette =['7a8737', 'acbe4d', '0ae042', 'fff70b', 'ffaf38', 'ff641b', 'a41fd6', 'ffffff'];
 
// name of the legend
var names = ['Enhanced Regrowth, High','Enhanced Regrowth, Low','Unburned', 'Low Severity',
'Moderate-low Severity', 'Moderate-high Severity', 'High Severity', 'NA'];
 
// Add color and and names
for (var i = 0; i < 8; i++) {
  legend.add(makeRow(palette[i], names[i]));
  }  
 
// add legend to map (alternatively you can also print the legend to the console)
Map.add(legend);

// Fire Perimeters from NIFC 
var perimeters = ee.FeatureCollection('projects/localsolve/assets/los_angeles_fires/LA_CA_Perimeters_NIFC_FIRIS_public_view')
.filterBounds(geometry)

Map.addLayer(perimeters, {}, 'Raw Perimeters')

// Define the start and end of the year 2025 in milliseconds
var startDate = ee.Date.fromYMD(2025, 1, 1).millis();
var endDate = ee.Date.fromYMD(2026, 1, 1).millis();

// Filter the FeatureCollection to include only features from 2025
var perimeters_2025 = perimeters.filter(ee.Filter.gte('CreationDa', startDate))
                   .filter(ee.Filter.lt('CreationDa', endDate));

var mergedGeometry = perimeters_2025.geometry().dissolve();

// Extract individual merged polygons
var mergedPolygons = mergedGeometry.geometries();

// Function to assign properties from an overlapping feature
// var assignProperties = function(geom) {
//     var polygon = ee.Geometry(geom);
    
//     // Find features that intersect this merged polygon
//     var intersectingFeatures = perimeters_2025.filterBounds(polygon);
    
//     // Select one of the overlapping features (e.g., first one)
//     var representativeFeature = intersectingFeatures.first();
    
//     // Assign properties from the representative feature to the merged polygon
//     return ee.Feature(polygon).set(representativeFeature.toDictionary());
// };

// Function to assign properties from an overlapping feature
var assignProperties = function(geom) {
    var polygon = ee.Geometry(geom);
    
    // Find features that intersect this merged polygon
    var intersectingFeatures = perimeters_2025.filterBounds(polygon);
    
    // Select one of the overlapping features (e.g., first one)
    var representativeFeature = ee.Feature(intersectingFeatures.first());
    
    // Remove 'area_acres' property if it exists
    var properties = representativeFeature.toDictionary()
        .remove(['area_acres']);  // Remove the old area property
    
    // Calculate the new area in acres (1 acre = 4046.86 m²)
    var areaSqMeters = polygon.area();
    var areaAcres = areaSqMeters.divide(4046.86);
    
    // Assign properties and add the new 'area_acres'
    return ee.Feature(polygon).set(properties).set('area_acres', areaAcres);
};

// Convert merged polygons into a FeatureCollection with properties
var merged_perimeters_2025 = ee.FeatureCollection(mergedPolygons.map(assignProperties));

Map.addLayer(merged_perimeters_2025, {}, 'Merged Perimeters')

// Santa Monica Species
var santa_monica_species = ee.FeatureCollection('projects/localsolve/assets/los_angeles_fires/Santa_Monica_Vegetation_Map')
santa_monica_species = santa_monica_species.filterBounds(geometry)

Map.addLayer(santa_monica_species)

//Invasive species 

var calveg = ee.FeatureCollection('projects/localsolve/assets/los_angeles_fires/LA_Current_InvasivePlants')
Map.addLayer(calveg, {}, 'Invasive Species')

//==========================================================================================
//                                  PREPARE FILE EXPORT

var id = dNBR.id().getInfo();
      
Export.image.toDrive({image: dNBR, scale: 10, description: id, fileNamePrefix: 'dNBR Greyscale',
  region: area, maxPixels: 1e13});
  
Export.image.toDrive({image: classified, scale: 10, description: id, fileNamePrefix: 'dNBR Classified',
  region: area, maxPixels: 1e13});

Export.image.toAsset({
  image: dNBR,
  description: '_dNBR_Greyscale',
  assetId: 'projects/localsolve/assets/los_angeles_fires/dNBR_Greyscale_Jan_2025',
  scale: 10,
  region: area,
  maxPixels: 1e13
});

Export.image.toAsset({
  image: classified,
  description: '_dNBR_Classified',
  assetId: 'projects/localsolve/assets/los_angeles_fires/dNBR_Classified_Jan_2025',
  scale: 10,
  region: area,
  maxPixels: 1e13
});

// Export the FeatureCollection as an EE Asset
Export.table.toAsset({
  collection: merged_perimeters_2025,
  description: 'merged_perimeters_2025',
  assetId: 'projects/localsolve/assets/los_angeles_fires/merged_perimeters_Jan_2025'
});


// Export updated perimeters

// TESTING EXPORTS with original
// Map.addLayer(ee.FeatureCollection('projects/localsolve/assets/los_angeles_fires/merged_perimeters_Jan_2025'))

// var dnbr_grey = ee.Image('projects/localsolve/assets/los_angeles_fires/dNBR_Greyscale_Jan_2025')
// var dnbr_classified = ee.Image('projects/localsolve/assets/los_angeles_fires/dNBR_Classified_Jan_2025')

// Map.addLayer(dnbr_grey)
// Map.addLayer(dnbr_classified)
// Downloads will be available in the 'Tasks'-tab on the right.'

var post_mos_rgb = post_mos
  .select(['B4', 'B3', 'B2'])
  .visualize({min: 0, max: 2000,gamma:1.5})

var pre_mos_rgb = pre_mos
  .select(['B4', 'B3', 'B2'])
  .visualize({min: 0, max: 2000,gamma:1.5})
  
Map.addLayer(post_mos_rgb, {}, 'S2_Post');

// Set up Export task.
Export.map.toCloudStorage({
  image: post_mos_rgb,
  description: 'S2_LA_Burned_Area',
  bucket: 'localsolve_assets',  // replace with your GCS bucket name
  fileFormat: 'png',
  maxZoom: 14,
  region: geometry,
  writePublicTiles: true
});

// Set up Export task.
Export.map.toCloudStorage({
  image: pre_mos_rgb,
  description: 'S2_LA_Pre_Burn',
  bucket: 'localsolve_assets',  // replace with your GCS bucket name
  fileFormat: 'png',
  maxZoom: 14,
  region: geometry,
  writePublicTiles: true
});
