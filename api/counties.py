from http.server import BaseHTTPRequestHandler
import json
import csv
import os
import re

def load_iowa_counties_and_cities(csv_path="city-county-mapping.csv"):
    """Parse the Iowa cities CSV and extract counties with their cities."""
    county_cities = {}

    # Try multiple paths for the CSV file
    possible_paths = [
        csv_path,
        f"../{csv_path}",
        f"../../{csv_path}",
        os.path.join(os.path.dirname(__file__), "..", csv_path)
    ]

    csv_file = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_file = path
            break

    if not csv_file:
        return {}, []

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                city = row.get('City', '').strip()
                county = row.get('County', '').strip()

                if not city or not county:
                    continue

                city = re.sub(r'\s+', ' ', city)
                county = re.sub(r'\s+', ' ', county)

                if county not in county_cities:
                    county_cities[county] = []

                if city not in county_cities[county]:
                    county_cities[county].append(city)

        for county in county_cities:
            county_cities[county].sort()

        counties = sorted(county_cities.keys())

        return county_cities, counties

    except Exception as e:
        return {}, []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            county_cities_dict, counties_list = load_iowa_counties_and_cities()
            
            result = {
                "counties": [
                    {"name": county, "city_count": len(county_cities_dict[county])}
                    for county in counties_list
                ]
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': {'code': '500', 'message': str(e)}
            }).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

