import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
import os

class MLEngine:
    def __init__(self, data_path='data/LandSphere_India_Dataset_5000_Rows.csv'):
        self.data_path = data_path
        self.models = {}
        self.metrics = {}
        self.poly_features = PolynomialFeatures(degree=2)
        self.load_and_train()

    def load_and_train(self):
        if not os.path.exists(self.data_path):
            print(f"Data file {self.data_path} not found.")
            return

        df = pd.read_csv(self.data_path)
        
        # Features: Area_SqFt, Year_Built, Growth_Rate, Risk_Score
        # Target: Current_Price
        X = df[['Area_SqFt', 'Year_Built', 'Growth_Rate', 'Risk_Score']]
        y = df['Current_Price']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 1. Linear Regression
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        self.models['lr'] = lr
        self.evaluate('lr', lr, X_test, y_test)

        # 2. Polynomial Regression
        X_train_poly = self.poly_features.fit_transform(X_train)
        X_test_poly = self.poly_features.transform(X_test)
        poly_model = LinearRegression()
        poly_model.fit(X_train_poly, y_train)
        self.models['poly'] = poly_model
        self.evaluate('poly', poly_model, X_test_poly, y_test)

        # 3. Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        self.models['rf'] = rf
        self.evaluate('rf', rf, X_test, y_test)

    def evaluate(self, name, model, X_test, y_test):
        y_pred = model.predict(X_test)
        self.metrics[name] = {
            'R2': round(r2_score(y_test, y_pred), 4),
            'MAE': round(mean_absolute_error(y_test, y_pred), 2),
            'MSE': round(mean_squared_error(y_test, y_pred), 2)
        }

    def predict(self, area, year_built, growth_rate, risk_score, years_ahead=1):
        # We predict the current price first, then apply growth
        input_data = pd.DataFrame([[area, year_built, growth_rate, risk_score]], 
                                   columns=['Area_SqFt', 'Year_Built', 'Growth_Rate', 'Risk_Score'])
        
        # Use RF for best accuracy usually
        base_price_pred = self.models['rf'].predict(input_data)[0]
        
        # Future price prediction based on growth rate
        future_price = base_price_pred * ((1 + growth_rate) ** years_ahead)
        roi = ((future_price - base_price_pred) / base_price_pred) * 100
        
        return {
            'current_price_est': round(base_price_pred, 2),
            'future_price': round(future_price, 2),
            'roi': round(roi, 2),
            'risk_score': risk_score,
            'investment_score': round((growth_rate * roi * 100) / risk_score, 2)
        }

if __name__ == "__main__":
    ml = MLEngine()
    print("Metrics:", ml.metrics)
    # Sample prediction
    res = ml.predict(2000, 2020, 0.1, 5, 5)
    print("Sample Prediction (5 years):", res)
