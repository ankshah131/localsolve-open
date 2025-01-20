// Charger les données des limites administratives des comtés des États-Unis
var counties = ee.FeatureCollection('TIGER/2018/Counties');

// Filtrer pour le comté de Los Angeles
var losAngelesCounty = counties.filter(ee.Filter.eq('NAME', 'Los Angeles')).geometry();

// Visualiser le comté de Los Angeles sur la carte
Map.centerObject(losAngelesCounty, 9);
Map.addLayer(losAngelesCounty, {color: 'blue'}, 'Los Angeles County Boundary');

// Charger les données de vent NOAA GFS
var uv = ee.ImageCollection('NOAA/GFS0P25')
  .select(['u_component_of_wind_10m_above_ground', 'v_component_of_wind_10m_above_ground'])
  .filterDate('2025-01-01', Date.now()); // Période d'analyse des vents

// Sélectionner la première image et renommer les bandes pour simplifier
var uv0 = uv.first().rename(['u', 'v']);

// Définir les paramètres d'échantillonnage
var scale = 5000; // Résolution de 5 km par pixel
var numPixels = 200; // Limiter à 200 points pour éviter une surcharge

// Échantillonner les données de vent dans la région de Los Angeles
var samples = uv0.sample({
  region: losAngelesCounty, // Région : comté de Los Angeles
  scale: scale,             // Résolution d'échantillonnage
  numPixels: numPixels,     // Nombre maximal de points échantillonnés
  geometries: true          // Inclure les coordonnées géographiques
});

// Fonction pour créer des vecteurs de vent (flèches)
var createArrows = function(feature) {
  var u = feature.get('u'); // Composante est-ouest du vent
  var v = feature.get('v'); // Composante nord-sud du vent
  var coords = ee.Geometry(feature.geometry()).coordinates(); // Coordonnées du point

  // Normaliser la longueur des flèches
  var scaleFactor = 0.1; // Ajuster le facteur d'échelle pour la longueur
  var arrowEnd = [
    ee.Number(coords.get(0)).add(ee.Number(u).multiply(scaleFactor)),
    ee.Number(coords.get(1)).add(ee.Number(v).multiply(scaleFactor))
  ];

  // Créer une ligne représentant la flèche
  return ee.Feature(ee.Geometry.LineString([coords, arrowEnd]), feature.toDictionary());
};

// Appliquer la fonction pour créer les vecteurs (flèches)
var arrows = samples.map(createArrows);

// Ajouter les vecteurs de vent (flèches) à la carte
Map.addLayer(arrows, {color: 'blue'}, 'Wind Vectors (Arrows)');
