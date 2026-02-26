import pandas as pd
import subprocess
import json
import os

class DSAEngine:
    def __init__(self, data_path='data/LandSphere_India_Dataset_5000_Rows.csv'):
        self.data_path = data_path
        # Keep DF for pandas-specific tasks in other parts of the app
        self.df = pd.read_csv(data_path)
        self.java_cmd = ['java', 'DSAEngine', self.data_path]

    def _run_java(self, command, *args):
        try:
            cmd = self.java_cmd + [command] + list(map(str, args))
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Java Engine Error: {e}")
            return None

    def linear_search(self, budget_max):
        """Filter properties by budget - Delegated to Java"""
        return self._run_java('filter', budget_max)

    def binary_search(self, price_target):
        """Search for a specific price - Delegated to Java"""
        return self._run_java('search', price_target)

    def merge_sort(self, props_placeholder=None):
        """Sort properties by price - Delegated to Java"""
        # In the original, this modified the list in place. 
        # Here we return the sorted list from Java.
        return self._run_java('sort')

    def bfs_nearby_cities(self, start_city):
        """Find nearby cities - Delegated to Java"""
        res = self._run_java('city_data', start_city)
        return res.get('nearby', []) if res else []

    def get_city_data(self, city_name):
        """City analytics - Delegated to Java"""
        return self._run_java('city_data', city_name)

    def get_multi_city_data(self, cities):
        """Batch city analytics - Delegated to Java"""
        return self._run_java('multi_city_data', ",".join(cities))

    def search_nearby(self, state, city, property_type, target_price, margin=None):
        """Find properties nearby with specific type and target price - Delegated to Java"""
        args = [state, city, property_type, target_price]
        if margin is not None:
            args.append(margin)
        return self._run_java('search_nearby', *args)


if __name__ == "__main__":
    dsa = DSAEngine()
    print("Nearby Mumbai (Java):", dsa.bfs_nearby_cities('Mumbai'))
    city_data = dsa.get_city_data('Delhi')
    print("Delhi Analytics (Java):", city_data.get('avg_price') if city_data else 'Error')

