from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
import os
from datetime import datetime
from ml_engine import MLEngine
from dsa_engine import DSAEngine

app = Flask(__name__)
app.secret_key = 'landsphere_secret_key'

# Initialize Engines
ml_engine = MLEngine()
dsa_engine = DSAEngine()

DATA_DIR = 'data'
USERS_CSV = os.path.join(DATA_DIR, 'Users.csv')
TRANSACTIONS_CSV = os.path.join(DATA_DIR, 'Transactions.csv')
LISTINGS_CSV = os.path.join(DATA_DIR, 'Listings.csv')

def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_csv(USERS_CSV)
        user = users[(users['Username'] == username) & (users['Password'] == password)]
        if not user.empty:
            session['user_id'] = int(user.iloc[0]['UserID'])
            session['username'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        users = load_csv(USERS_CSV)
        if username in users['Username'].values:
            return render_template('register.html', error="Username already exists")
        
        new_id = users['UserID'].max() + 1 if not users.empty else 1
        new_user = pd.DataFrame([[new_id, username, password, email, 10000000, fullname, phone, address]], 
                                columns=['UserID', 'Username', 'Password', 'Email', 'Balance', 'FullName', 'Phone', 'Address'])
        users = pd.concat([users, new_user], ignore_index=True)
        save_csv(users, USERS_CSV)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_id = session['user_id']
    trans = load_csv(TRANSACTIONS_CSV)
    
    # Admin View: User ID 1 sees everything
    if user_id == 1:
        transactions = trans
    else:
        transactions = trans[trans['UserID'] == user_id]
    
    users = load_csv(USERS_CSV)
    balance = users[users['UserID'] == user_id]['Balance'].values[0]
    
    # Get Owned Properties
    listings = load_csv(LISTINGS_CSV)
    owned = listings[listings['OwnerID'] == user_id]
    props = dsa_engine.df
    my_properties = pd.merge(owned, props, left_on='PropertyID', right_on='Property_ID').to_dict('records')
    
    return render_template('dashboard.html', username=session['username'], balance=balance, 
                         transactions=transactions.to_dict('records'), my_properties=my_properties, is_admin=(user_id == 1))

@app.route('/api/nearby_cities')
def nearby_cities():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City is required'}), 400
    
    # Query the DSA engine's BFS implementation
    nearby = dsa_engine.bfs_nearby_cities(city)
    return jsonify({'nearby': nearby})

@app.route('/marketplace')
def marketplace():
    listings = load_csv(LISTINGS_CSV)
    available = listings[listings['Status'] == 'Available']
    props = dsa_engine.df
    users = load_csv(USERS_CSV)
    
    # Merge available listings with properties
    market_data = pd.merge(available, props, left_on='PropertyID', right_on='Property_ID')
    # Merge with users to get owner details
    user_cols = ['UserID', 'Username', 'FullName', 'Phone', 'Email', 'Address']
    market_data = pd.merge(market_data, users[user_cols], left_on='OwnerID', right_on='UserID', how='left')
    market_data['OwnerName'] = market_data['FullName'].fillna(market_data['Username'].fillna('Platform'))
    
    region_filter = request.args.get('region')
    state_filter = request.args.get('state')
    city_filter = request.args.get('city')
    search_query = request.args.get('search')
    if search_query:
        search_query = search_query.strip().lower()
        # Search Cities first
        city_match = props[props['City'].str.lower() == search_query]
        if not city_match.empty:
            row = city_match.iloc[0]
            return redirect(url_for('marketplace', region=row['Region'], state=row['State'], city=row['City']))
        
        # Search States
        state_match = props[props['State'].str.lower() == search_query]
        if not state_match.empty:
            row = state_match.iloc[0]
            return redirect(url_for('marketplace', region=row['Region'], state=row['State']))

    if city_filter:
        # Step 4: Detailed Listings for City
        city_market = market_data[market_data['City'].str.lower() == city_filter.lower()]
        
        # Infer context if missing (e.g. from direct URL)
        if not state_filter and not city_market.empty:
            state_filter = city_market.iloc[0]['State']
        if not region_filter and not city_market.empty:
            region_filter = city_market.iloc[0]['Region']
            
        # DSA Logic: Sort/Search
        budget = request.args.get('budget', type=int)
        if budget:
            city_market = city_market[city_market['Price'] <= budget]
        
        sort_by = request.args.get('sort')
        if sort_by == 'price_asc':
            city_market = city_market.sort_values('Price')
        elif sort_by == 'price_desc':
            city_market = city_market.sort_values('Price', ascending=False)
            
        return render_template('marketplace.html', properties=city_market.to_dict('records'), 
                             selected_city=city_filter, selected_state=state_filter, selected_region=region_filter)
    
    elif state_filter:
        # Step 3: City Overview within State
        state_market = market_data[market_data['State'].str.lower() == state_filter.lower()]
        if state_market.empty:
            return redirect('/marketplace')
            
        if not region_filter:
            region_filter = state_market.iloc[0]['Region']
            
        city_counts = state_market.groupby('City').size().reset_index(name='count')
        return render_template('marketplace.html', city_summary=city_counts.to_dict('records'), 
                             selected_state=state_filter, selected_region=region_filter)
    
    elif region_filter:
        # Step 2: State Overview within Region
        region_market = market_data[market_data['Region'].str.lower() == region_filter.lower()]
        if region_market.empty:
            return redirect('/marketplace')
            
        state_counts = region_market.groupby('State').size().reset_index(name='count')
        return render_template('marketplace.html', state_summary=state_counts.to_dict('records'), 
                             selected_region=region_filter)
    
    else:
        # Step 1: Region Overview (India)
        region_counts = market_data.groupby('Region').size().reset_index(name='count')
        return render_template('marketplace.html', region_summary=region_counts.to_dict('records'))

@app.route('/buy/<int:property_id>', methods=['POST'])
def buy_land(property_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    buyer_id = session['user_id']
    
    listings = load_csv(LISTINGS_CSV)
    listing_match = listings[listings['PropertyID'] == property_id]
    
    if listing_match.empty or listing_match.iloc[0]['Status'] != 'Available':
        return jsonify({'error': 'Not available'}), 400
    
    listing_idx = listing_match.index[0]
    price = listing_match.at[listing_idx, 'Price']
    seller_id = int(listing_match.at[listing_idx, 'OwnerID'])
    
    if buyer_id == seller_id:
        return jsonify({'error': 'You already own this land'}), 400

    users = load_csv(USERS_CSV)
    buyer_idx = users[users['UserID'] == buyer_id].index[0]
    
    # Balance Restriction Removed per User Request
    # if users.at[buyer_idx, 'Balance'] < price:
    #     return jsonify({'error': 'Insufficient balance'}), 400
    
    # 1. Update Buyer Balance
    users.at[buyer_idx, 'Balance'] -= price
    
    # 2. Update Seller Balance (if not platform)
    if seller_id != 0:
        seller_row_idx = users[users['UserID'] == seller_id].index
        if not seller_row_idx.empty:
            users.at[seller_row_idx[0], 'Balance'] += price
            
    save_csv(users, USERS_CSV)
    
    # 3. Update Listing
    listings.at[listing_idx, 'Status'] = 'Sold'
    listings.at[listing_idx, 'OwnerID'] = buyer_id
    save_csv(listings, LISTINGS_CSV)
    
    # 4. Record Transaction for Buyer
    trans = load_csv(TRANSACTIONS_CSV)
    new_trans_id = trans['TransactionID'].max() + 1 if not trans.empty else 1
    new_record = pd.DataFrame([[new_trans_id, buyer_id, property_id, datetime.now().strftime('%Y-%m-%d'), price, 'Buy']], 
                               columns=['TransactionID', 'UserID', 'PropertyID', 'Date', 'Price', 'Type'])
    trans = pd.concat([trans, new_record], ignore_index=True)
    
    # Optional: Record Transaction for Seller
    if seller_id != 0:
        new_trans_id += 1
        sell_record = pd.DataFrame([[new_trans_id, seller_id, property_id, datetime.now().strftime('%Y-%m-%d'), price, 'Sell']], 
                                    columns=['TransactionID', 'UserID', 'PropertyID', 'Date', 'Price', 'Type'])
        trans = pd.concat([trans, sell_record], ignore_index=True)
        
    save_csv(trans, TRANSACTIONS_CSV)
    
    return jsonify({'success': True})

@app.route('/sell/<int:property_id>', methods=['POST'])
def sell_land(property_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    price = request.json.get('price')
    
    if not price or price <= 0:
        return jsonify({'error': 'Invalid price'}), 400
        
    listings = load_csv(LISTINGS_CSV)
    listing_match = listings[(listings['PropertyID'] == property_id) & (listings['OwnerID'] == user_id)]
    
    if listing_match.empty:
        return jsonify({'error': 'Property not found or not owned by you'}), 400
        
    idx = listing_match.index[0]
    listings.at[idx, 'Status'] = 'Available'
    listings.at[idx, 'Price'] = price
    save_csv(listings, LISTINGS_CSV)
    
    return jsonify({'success': True})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    area = data.get('area', 1000)
    year_buying = data.get('year_buying', 2024)
    horizon = data.get('years', 5)
    
    # Sensible defaults for parameters removed from UI
    growth_rate = 0.1  # 10% annual growth
    risk_score = 5    # Neutral risk
    
    # Initial prediction (Current Price approx.)
    # Note: Using year_buying as year_built for ML input consistency
    res = ml_engine.predict(
        area=area,
        year_built=year_buying,
        growth_rate=growth_rate,
        risk_score=risk_score,
        years_ahead=horizon
    )
    
    # Generate Time Series for Interactive Graph
    series = []
    base_price = res['current_price_est']
    for y in range(horizon + 1):
        price = base_price * ((1 + growth_rate) ** y)
        series.append({
            'year': year_buying + y,
            'price': round(price, 2)
        })
    
    res['time_series'] = series
    return jsonify(res)

@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html', metrics=ml_engine.metrics)

@app.route('/compare')
def compare():
    cities = dsa_engine.df['City'].unique()
    return render_template('compare.html', cities=cities)

@app.route('/api/city/<city_name>')
def city_api(city_name):
    data = dsa_engine.get_city_data(city_name)
    return jsonify(data)

@app.route('/api/compare')
def compare_api():
    cities = request.args.get('cities', '').split(',')
    cities = [c.strip() for c in cities if c.strip()]
    if not cities:
        return jsonify({})
    data = dsa_engine.get_multi_city_data(cities)
    return jsonify(data)

@app.route('/api/search_nearby')
def search_nearby_api():
    state = request.args.get('state', '')
    city = request.args.get('city', '')
    prop_type = request.args.get('type', '')
    target_price = request.args.get('price', type=float)
    margin = request.args.get('margin', type=float)
    
    if not state or not prop_type or target_price is None:
        return jsonify({'error': 'State, type, and target price are required'}), 400
        
    results = dsa_engine.search_nearby(state, city, prop_type, target_price, margin)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
