import pandas as pd
import os
import json

def test_marketplace():
    LISTINGS_CSV = 'data/Listings.csv'
    DATA_CSV = 'data/LandSphere_India_Dataset_5000_Rows.csv'
    
    listings = pd.read_csv(LISTINGS_CSV)
    props = pd.read_csv(DATA_CSV)
    
    available = listings[listings['Status'] == 'Available']
    market_data = pd.merge(available, props, left_on='PropertyID', right_on='Property_ID')
    
    print(f"Total Available: {len(available)}")
    print(f"Total Matched: {len(market_data)}")
    
    if len(market_data) > 0:
        state_counts = market_data.groupby('State').size().reset_index(name='count')
        print("State Summary:")
        print(state_counts)
        
        first_state = state_counts.iloc[0]['State']
        city_market = market_data[market_data['State'].str.lower() == first_state.lower()]
        city_counts = city_market.groupby('City').size().reset_index(name='count')
        print(f"\nCity Summary for {first_state}:")
        print(city_counts)
    else:
        print("Merge failed or no available properties.")

if __name__ == "__main__":
    test_marketplace()
