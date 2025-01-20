import datetime
import logging
import os
import time
from tempfile import mkdtemp
from typing import List, Tuple
import geopandas as gpd
import pandas as pd
import urllib

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class Settings:
    """Class for storing config and global variables for this ingest script."""
    temp_dir: str = mkdtemp()
    output_shp_filename = 'VIIRS_Merged_URT_Custom_BBOX_24h.shp'
    satellites: List[str] = ['snpp', 'noaa20']
    firms_wfs_url_prefix: str = 'https://firms.modaps.eosdis.nasa.gov/mapserver/wfs'
    firms_wfs_url_suffix: str = '?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAME=ms:fires_<satellite>_24hrs&' + \
                                'STARTINDEX=0&COUNT=100000&SRSNAME=urn:ogc:def:crs:EPSG::4326&' + \
                                'BBOX=<bbox>&outputformat=csv'
    firms_wfs_request_sleep_secs: int = 5
    firms_api_map_keys: List[str] = [  # Need two since this ingest exceeds the 500 point transaction limit
  #Use the API MAP key
    ]


config = Settings()


def ingest(bbox: Tuple[float, float, float, float]):
    """Main function to get new active wildfire data and save it as a shapefile."""
    logger.info("Processing new FIRMS VIIRS Merged Ultra Real Time wildfire data for the last 24 hours")
    get_new_data(bbox)
    logger.info("Done!")
    return


def get_new_data(bbox: Tuple[float, float, float, float]):
    """Download the latest VIIRS active URT 24-hour fire data for the specified bounding box."""
    logger.info("Collecting newest VIIRS detections from the FIRMS WFS")
    bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"  # Format: minLon,minLat,maxLon,maxLat
    region_sat_df_list = []

    for satellite, map_key in zip(config.satellites, config.firms_api_map_keys):
        logger.info(f"Downloading the last 24 hours of detections for bounding box {bbox_str} from {satellite}")
        for i in range(1, 6):  # Retry mechanism
            try:
                url = f"{config.firms_wfs_url_prefix}/{map_key}/{config.firms_wfs_url_suffix.replace('<satellite>', satellite).replace('<bbox>', bbox_str)}"
                region_sat_df = pd.read_csv(url)
                break
            except (urllib.error.HTTPError, urllib.error.URLError, ConnectionError) as e:
                if i == 5:
                    logger.exception("Unable to retrieve newest data from the FIRMS API")
                    raise e
                else:
                    logger.warning(f"Retrying {i}/5 after failure to retrieve data from FIRMS API")
                    time.sleep(30)
        region_sat_df_list.append(region_sat_df)
        time.sleep(config.firms_wfs_request_sleep_secs)

    new_fires_df = pd.concat(region_sat_df_list, ignore_index=True)
    logger.info(f"Number of detections pre-deduplication: {len(new_fires_df)}")
    new_fires_df.drop_duplicates(inplace=True, ignore_index=True)
    logger.info(f"Number of detections post-deduplication: {len(new_fires_df)}")

    logger.info("Processing WFS data and writing to shapefile")
    new_fires_df.columns = map(str.upper, new_fires_df.columns)
    new_fires_df['ACQ_TIME'] = new_fires_df['ACQ_TIME'].astype(int).astype(str).str.zfill(4)
    new_fires_df['ACQ_DATE'] = new_fires_df['ACQ_DATE'].astype(str)
    confidence_value_map_dict = {
        'h': 'high',
        'n': 'nominal',
        'l': 'low'
    }
    new_fires_df['CONFIDENCE'] = new_fires_df['CONFIDENCE'].map(confidence_value_map_dict)
    new_fires_df['ACQ_DATETIME'] = new_fires_df['ACQ_DATETIME'].apply(str)
    new_fires_df.ACQ_DATETIME = new_fires_df.ACQ_DATETIME.str.replace("\\+00", 'Z', regex=True)
    new_fires_df.ACQ_DATETIME = new_fires_df.ACQ_DATETIME.str.replace(' ', 'T')
    new_fires_df.ACQ_DATETIME = new_fires_df.ACQ_DATETIME.str.replace('/', '-')
    new_fires_df.rename(columns={'ACQ_DATETIME': 'ACQ_DT',
                                 'BRIGHTNESS_2': 'BRIGHT_2'},
                        inplace=True)
    if 'UNNAMED: 1' in new_fires_df.columns:
        columns_to_drop = ['UNNAMED: 1', 'WKT']
    else:
        columns_to_drop = ['WKT']
    new_fires_df.drop(columns=columns_to_drop, inplace=True)
    new_fires_gdf = gpd.GeoDataFrame(new_fires_df,
                                     geometry=gpd.points_from_xy(new_fires_df.LONGITUDE, new_fires_df.LATITUDE))
    new_fires_gdf.crs = 'EPSG:4326'
    output_file_path = os.path.join(config.temp_dir, config.output_shp_filename)
    new_fires_gdf.to_file(filename=output_file_path)
    logger.info(f"Shapefile written to: {output_file_path}")

    return


if __name__ == '__main__':
    # User-provided bounding box (example: -90, -180, 90, 180)
    user_bbox = (-125.0, 25.0, -65.0, 49.0)  # Example for the contiguous USA
    ingest(user_bbox)
