import pandas as pd
import random
import os

def generate_dataset():
    state_city_map = {
        'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Varanasi', 'Agra', 'Prayagraj', 'Ghaziabad', 'Noida', 'Meerut', 'Gorakhpur', 'Jhansi', 'Bareilly'],
        'Haryana': ['Faridabad', 'Gurugram', 'Panipat', 'Ambala', 'Karnal', 'Hisar', 'Rohtak', 'Sonipat', 'Yamunanagar', 'Panchkula', 'Kurukshetra', 'Rewari', 'Palwal', 'Bhiwani', 'Jind', 'Kaithal', 'Sirsa', 'Bahadurgarh', 'Mahendragarh', 'Narnaul', 'Tohana', 'Dabwali', 'Pehowa', 'Assandh', 'Gohana', 'Fatehabad', 'Hansi', 'Charkhi Dadri', 'Narwana', 'Shahbad', 'Ratia', 'Sohna', 'Pundri', 'Kosli'],
        'Punjab': ['Amritsar', 'Ludhiana', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Pathankot', 'Hoshiarpur', 'Moga', 'Firozpur', 'Barnala', 'Sangrur', 'Kapurthala', 'Faridkot', 'Malerkotla', 'Phagwara', 'Abohar', 'Tarn Taran'],
        'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Bikaner', 'Ajmer', 'Alwar', 'Bharatpur', 'Sikar', 'Pali', 'Barmer', 'Chittorgarh', 'Bhilwara', 'Nagaur', 'Bundi', 'Hanumangarh', 'Dausa', 'Tonk', 'Jaisalmer', 'Sawai Madhopur', 'Sri Ganganagar', 'Jhunjhunu'],
        'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Junagadh', 'Gandhinagar', 'Bharuch', 'Anand', 'Morbi', 'Vapi', 'Navsari', 'Porbandar', 'Mehsana', 'Palanpur', 'Godhra'],
        'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Thane', 'Aurangabad', 'Solapur', 'Kolhapur', 'Amravati', 'Nanded', 'Jalgaon', 'Akola', 'Latur', 'Dhule', 'Ahmednagar', 'Chandrapur', 'Parbhani', 'Satara', 'Beed', 'Ratnagiri', 'Wardha', 'Yavatmal', 'Sangli', 'Bhiwandi', 'Panvel'],
        'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain', 'Sagar', 'Rewa', 'Satna', 'Dewas', 'Ratlam', 'Morena', 'Khandwa', 'Burhanpur', 'Shivpuri', 'Vidisha', 'Chhindwara', 'Mandsaur', 'Sehore', 'Neemuch'],
        'Bihar': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Darbhanga', 'Purnia', 'Ara', 'Begusarai', 'Katihar', 'Munger', 'Chapra', 'Sasaram', 'Siwan', 'Motihari'],
        'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Darjeeling', 'Malda', 'Kharagpur', 'Haldia', 'Bardhaman', 'Jalpaiguri', 'Raiganj', 'Cooch Behar', 'Chandannagar', 'Midnapore', 'Bankura'],
        'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Puri', 'Sambalpur', 'Berhampur', 'Balasore', 'Bhadrak', 'Jharsuguda', 'Koraput', 'Baripada', 'Jeypore'],
        'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Chaibasa', 'Dumka'],
        'Chhattisgarh': ['Raipur', 'Bilaspur', 'Durg', 'Korba', 'Rajnandgaon', 'Jagdalpur', 'Raigarh', 'Ambikapur', 'Dhamtari'],
        'Himachal Pradesh': ['Shimla', 'Manali', 'Dharamshala', 'Solan', 'Mandi', 'Kullu', 'Chamba', 'Una'],
        'Uttarakhand': ['Dehradun', 'Haridwar', 'Rishikesh', 'Haldwani', 'Roorkee', 'Nainital', 'Almora', 'Pithoragarh', 'Rudrapur'],
        'Goa': ['Panaji', 'Margao', 'Vasco da Gama', 'Mapusa', 'Ponda', 'Bicholim'],
        'Karnataka': ['Bengaluru', 'Mysuru', 'Mangaluru', 'Hubballi', 'Belagavi', 'Davanagere', 'Ballari', 'Tumakuru', 'Shivamogga', 'Udupi', 'Hassan', 'Bidar', 'Raichur', 'Kolar', 'Chitradurga', 'Mandya', 'Gadag', 'Haveri', 'Karwar', 'Bagalkot'],
        'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Alappuzha', 'Kannur', 'Palakkad', 'Malappuram', 'Kottayam', 'Pathanamthitta', 'Idukki', 'Kasaragod'],
        'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tiruchirappalli', 'Tirunelveli', 'Erode', 'Vellore', 'Thanjavur', 'Dindigul', 'Kanchipuram', 'Cuddalore', 'Thoothukudi', 'Karur', 'Namakkal', 'Nagercoil', 'Sivakasi', 'Pudukkottai', 'Tiruppur', 'Villupuram', 'Hosur'],
        'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Tirupati', 'Kurnool', 'Rajahmundry', 'Kadapa', 'Anantapur', 'Eluru', 'Ongole', 'Srikakulam', 'Vizianagaram', 'Machilipatnam', 'Tenali'],
        'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam', 'Ramagundam', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Suryapet', 'Siddipet'],
        'Assam': ['Guwahati', 'Dibrugarh', 'Silchar', 'Jorhat', 'Tinsukia', 'Tezpur', 'Nagaon', 'Karimganj', 'Sivasagar', 'Bongaigaon'],
        'Arunachal Pradesh': ['Itanagar', 'Tawang', 'Pasighat', 'Ziro', 'Bomdila', 'Naharlagun'],
        'Manipur': ['Imphal', 'Thoubal', 'Bishnupur', 'Churachandpur', 'Ukhrul', 'Kakching'],
        'Meghalaya': ['Shillong', 'Tura', 'Nongpoh', 'Jowai', 'Baghmara', 'Williamnagar'],
        'Mizoram': ['Aizawl', 'Lunglei', 'Champhai', 'Serchhip', 'Kolasib'],
        'Nagaland': ['Kohima', 'Dimapur', 'Mokokchung', 'Wokha', 'Tuensang'],
        'Tripura': ['Agartala', 'Udaipur', 'Dharmanagar', 'Kailashahar', 'Belonia'],
        'Sikkim': ['Gangtok', 'Namchi', 'Gyalshing', 'Mangan', 'Rangpo'],
        'Delhi': ['New Delhi', 'Dwarka', 'Rohini', 'Saket', 'Karol Bagh', 'Lajpat Nagar', 'Pitampura', 'Janakpuri', 'Shahdara', 'Narela', 'Vasant Kunj', 'Najafgarh']
    }
    
    cities = []
    for state_cities in state_city_map.values():
        cities.extend(state_cities)
        
    property_types = ['Residential', 'Commercial', 'Agricultural', 'Industrial']
    
    data = []
    # Tier-based pricing approximations
    def get_city_base_price(city, state):
        tier_1 = ['Mumbai', 'Delhi', 'New Delhi', 'Bengaluru', 'Chennai', 'Hyderabad', 'Kolkata', 'Ahmedabad', 'Pune', 'Gurugram', 'Noida']
        tier_2 = ['Lucknow', 'Kanpur', 'Jaipur', 'Indore', 'Thane', 'Nagpur', 'Visakhapatnam', 'Bhopal', 'Patna', 'Vadodara', 'Ludhiana', 'Nashik']
        
        if city in tier_1: return random.randint(8000, 25000)
        if city in tier_2: return random.randint(4000, 8000)
        return random.randint(1500, 4000)

    region_map = {
        'North': ['Uttar Pradesh', 'Haryana', 'Punjab', 'Himachal Pradesh', 'Uttarakhand', 'Delhi'],
        'West': ['Rajasthan', 'Gujarat', 'Maharashtra', 'Goa', 'Madhya Pradesh'],
        'East': ['Bihar', 'West Bengal', 'Odisha', 'Jharkhand', 'Chhattisgarh'],
        'South': ['Karnataka', 'Kerala', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana'],
        'North-East': ['Assam', 'Arunachal Pradesh', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Tripura', 'Sikkim']
    }
    
    # Invert for lookup
    state_to_region = {}
    for region, states in region_map.items():
        for state in states:
            state_to_region[state] = region

    for i in range(1, 5001):
        state = random.choice(list(state_city_map.keys()))
        city = random.choice(state_city_map[state])
        region = state_to_region.get(state, 'Other')
        prop_type = random.choice(property_types)
        area = random.randint(500, 10000)
        
        price_per_sqft = get_city_base_price(city, state) * random.uniform(0.8, 1.5)
        if prop_type == 'Commercial': price_per_sqft *= 1.5
        elif prop_type == 'Agricultural': price_per_sqft *= 0.3
        
        current_price = int(price_per_sqft * area)
        growth_rate = random.uniform(0.05, 0.15)
        year = random.randint(2018, 2023)
        
        data.append({
            'Property_ID': i,
            'Region': region,
            'State': state,
            'City': city,
            'Property_Type': prop_type,
            'Area_SqFt': area,
            'Price_Per_SqFt': int(price_per_sqft),
            'Current_Price': current_price,
            'Year_Built': year,
            'Growth_Rate': round(growth_rate, 4),
            'Risk_Score': random.randint(1, 10)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('data/LandSphere_India_Dataset_5000_Rows.csv', index=False)
    print("Dataset generated successfully.")

def initialize_empty_csvs():
    # Keep existing Users.csv if not exists
    if not os.path.exists('data/Users.csv'):
        pd.DataFrame(columns=['UserID', 'Username', 'Password', 'Email', 'Balance']).to_csv('data/Users.csv', index=False)
    
    # Initialize Transactions
    pd.DataFrame(columns=['TransactionID', 'UserID', 'PropertyID', 'Date', 'Price', 'Type']).to_csv('data/Transactions.csv', index=False)
    
    # Seed Listings
    df = pd.read_csv('data/LandSphere_India_Dataset_5000_Rows.csv')
    listings = df[['Property_ID', 'Current_Price']].copy()
    listings.columns = ['PropertyID', 'Price']
    listings['OwnerID'] = 0
    listings['Status'] = 'Available'
    listings.to_csv('data/Listings.csv', index=False)
    print("CSVs initialized.")

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    generate_dataset()
    initialize_empty_csvs()
