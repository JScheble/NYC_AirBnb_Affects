import geopandas as gpd
import pandas as pd

def process_and_merge_spatial_data(listings_df, geo_map):
    """
    Converts listings to geo-points, performs spatial join with zip codes,
    and returns a density map.
    """
    # 1. Create GeoDataFrame from Lat/Long
    airbnb_gdf = gpd.GeoDataFrame(
        listings_df, 
        geometry=gpd.points_from_xy(listings_df.longitude, listings_df.latitude),
        crs="EPSG:4326"
    )
    
    # 2. Match CRS
    airbnb_gdf = airbnb_gdf.to_crs(geo_map.crs)
    
    # 3. Spatial Join
    joined_data = gpd.sjoin(airbnb_gdf, geo_map, how="left", predicate="within")
    
    # 4. Clean up the 'zip' column (String manipulation)
    joined_data['zip'] = joined_data['zip'].astype(str).str.split(',').str[0].str.strip()
    
    # 5. Aggregate counts
    zip_counts = joined_data['zip'].value_counts().reset_index()
    zip_counts.columns = ['zip', 'count'] # Rename for clarity
    
    # 6. Merge back to map
    density_map = geo_map.merge(zip_counts, on='zip', how='left')
    density_map['count'] = density_map['count'].fillna(0)
    
    return density_map



def perform_spatial_join(listings_df, geo_map):
    """
    Converts Airbnb lat/long to geometry points, projects them to the 
    NYC map's coordinate system, and performs a spatial join to 
    assign zip codes to listings.
    """
    # 1. Create GeoDataFrame from Lat/Long
    # Note: Ensure you have geopandas installed
    airbnb_gdf = gpd.GeoDataFrame(
        listings_df, 
        geometry=gpd.points_from_xy(listings_df.longitude, listings_df.latitude),
        crs="EPSG:4326"
    )
    
    # 2. Match Coordinate Reference Systems
    airbnb_gdf = airbnb_gdf.to_crs(geo_map.crs)
    
    # 3. Perform Spatial Join
    # 'predicate="within"' checks which zip code polygon the point falls inside
    joined_data = gpd.sjoin(airbnb_gdf, geo_map, how="left", predicate="within")
    
    # 4. Clean up the 'zip' column (some have multiple zips separated by commas)
    joined_data['zip'] = joined_data['zip'].astype(str).str.split(',').str[0].str.strip()
    
    return joined_data