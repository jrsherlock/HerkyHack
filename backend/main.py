from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from urllib.parse import quote
import re
import csv
import os
from datetime import datetime
from typing import Optional, List

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    first_name: str
    last_name: str
    hometown: Optional[str] = None
    state: str
    county: Optional[str] = None
    show_debug: bool = False

class SearchResult(BaseModel):
    first_name: str
    last_name: str
    hometown: str
    hit_found: bool
    mp4_link: Optional[str] = None
    mp4_accessible: bool
    details: str
    timestamp: str
    debug_info: Optional[str] = None
    hometown_used: Optional[str] = None
    city_found: Optional[str] = None
    cities_tried: Optional[int] = None
    total_cities: Optional[int] = None

def generate_mp4_url(first_name: str, last_name: str, hometown: str, state: str):
    """Generate the expected MP4 URL based on the naming pattern."""
    first_clean = first_name.lower().replace(' ', '-')
    last_clean = last_name.lower().replace(' ', '-')
    hometown_clean = hometown.lower().replace(' ', '-').replace(',', '')
    state_clean = state.lower()

    filename = f"{first_clean}-{last_clean}-{hometown_clean}-{state_clean}.mp4"
    mp4_url = f"https://d3mqiwdgu1iop6.cloudfront.net/videos/{filename}"

    return mp4_url, filename

def check_mp4_accessibility(mp4_url: str):
    """Check if the MP4 file is accessible."""
    try:
        response = requests.head(mp4_url, timeout=10, allow_redirects=True)

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'video/mp4' in content_type or 'application/octet-stream' in content_type:
                return True, ""

        # Try GET with range if HEAD fails
        headers = {'Range': 'bytes=0-1'}
        response = requests.get(mp4_url, headers=headers, timeout=10, stream=True)
        accessible = response.status_code in [200, 206]
        return accessible, ""

    except requests.exceptions.RequestException as e:
        return False, str(e)

def generate_hometown_permutations(hometown: str):
    """Generate multiple formatting permutations of the hometown."""
    permutations = []

    # Original format
    permutations.append(hometown)

    # Capitalize first character
    if hometown and hometown[0].islower():
        first_capitalized = hometown[0].upper() + hometown[1:]
        if first_capitalized != hometown:
            permutations.append(first_capitalized)

    # Fix common typo: "lowa" -> "Iowa"
    if hometown and hometown.lower().startswith('lowa'):
        iowa_fixed = re.sub(r'^[Ll]owa\b', 'Iowa', hometown)
        if iowa_fixed != hometown and iowa_fixed not in permutations:
            permutations.append(iowa_fixed)

    # Title case
    title_case = hometown.title()
    if title_case != hometown and title_case not in permutations:
        permutations.append(title_case)

    # Normalize spaces
    normalized = ' '.join(hometown.split())
    if normalized != hometown and normalized not in permutations:
        permutations.append(normalized)

    # Remove all spaces
    no_spaces = hometown.replace(' ', '')
    if no_spaces != hometown:
        permutations.append(no_spaces)

    # Insert spaces before capital letters
    spaced_capitals = re.sub(r'([a-z])([A-Z])', r'\1 \2', hometown)
    if spaced_capitals != hometown and spaced_capitals not in permutations:
        permutations.append(spaced_capitals)

    # Remove duplicates while preserving order
    seen = set()
    unique_permutations = []
    for perm in permutations:
        if perm not in seen:
            seen.add(perm)
            unique_permutations.append(perm)

    return unique_permutations

def fast_check_cache_hit(url: str, timeout=5):
    """Fast check for cache hit using X-Cache header."""
    try:
        response = requests.get(url, timeout=timeout)
        cache_header = response.headers.get('X-Cache', '').lower()
        is_hit = 'hit' in cache_header
        return is_hit, response
    except requests.exceptions.RequestException:
        return False, None

def check_admissions_hit(first_name: str, last_name: str, hometown: str, state: str, debug: bool = False):
    """Check if a name and hometown combination results in a hit."""
    debug_info = ""

    hometown_permutations = generate_hometown_permutations(hometown)
    if debug:
        debug_info += f"Generated {len(hometown_permutations)} hometown permutations to try:\n"
        for i, perm in enumerate(hometown_permutations, 1):
            debug_info += f"  {i}. '{perm}'\n"
        debug_info += "\n"

    for perm_index, hometown_perm in enumerate(hometown_permutations, 1):
        if debug:
            debug_info += f"Trying permutation {perm_index}/{len(hometown_permutations)}: '{hometown_perm}'\n"

        encoded_hometown = quote(hometown_perm)
        home_param = f"{encoded_hometown},{state}"
        url = f"https://your.admissions.uiowa.edu/?first={first_name.lower()}&last={last_name.lower()}&home={home_param}"

        try:
            is_cache_hit, response = fast_check_cache_hit(url, timeout=5)

            if not response:
                if debug:
                    debug_info += f"Request failed for '{hometown_perm}', trying next...\n\n"
                continue

            if not is_cache_hit:
                if debug:
                    debug_info += f"Cache miss for '{hometown_perm}', skipping MP4 check...\n\n"
                continue

            expected_mp4_url, expected_filename = generate_mp4_url(first_name, last_name, hometown_perm, state)
            if debug:
                debug_info += f"Generated MP4 URL: {expected_mp4_url}\n"

            mp4_accessible, mp4_error = check_mp4_accessibility(expected_mp4_url)

            if mp4_accessible:
                if debug:
                    debug_info += f"Hit found with permutation '{hometown_perm}'!\n"

                return {
                    'first_name': first_name,
                    'last_name': last_name,
                    'hometown': f"{hometown_perm}, {state}",
                    'hometown_original': hometown,
                    'hometown_used': hometown_perm,
                    'hit_found': True,
                    'mp4_link': expected_mp4_url,
                    'mp4_accessible': True,
                    'details': f'MP4 file found and accessible (used permutation: "{hometown_perm}")',
                    'timestamp': datetime.now().isoformat(),
                    'debug_info': debug_info if debug else None
                }
            else:
                if debug:
                    debug_info += f"No hit with permutation '{hometown_perm}', trying next...\n\n"

        except requests.exceptions.RequestException as e:
            if debug:
                debug_info += f"Request exception with permutation '{hometown_perm}': {str(e)}\n"
            continue

    if debug:
        debug_info += f"No hit found with any of the {len(hometown_permutations)} permutations tried.\n"

    return {
        'first_name': first_name,
        'last_name': last_name,
        'hometown': f"{hometown}, {state}" if hometown else f"Unknown, {state}",
        'hometown_original': hometown,
        'hometown_used': hometown_permutations[-1] if hometown_permutations else hometown,
        'hit_found': False,
        'mp4_link': None,
        'mp4_accessible': False,
        'details': f'MP4 file not accessible after trying {len(hometown_permutations)} permutations',
        'timestamp': datetime.now().isoformat(),
        'debug_info': debug_info if debug else None
    }

def load_iowa_counties_and_cities(csv_path="../city-county-mapping.csv"):
    """Parse the Iowa cities CSV and extract counties with their cities."""
    county_cities = {}

    if not os.path.exists(csv_path):
        return {}, []

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
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

def search_with_city_iteration(first_name: str, last_name: str, state: str, cities: List[str], debug: bool = False):
    """Search for a student by iterating through a list of cities."""
    debug_info = f"Searching through {len(cities)} cities for {first_name} {last_name}...\n\n"

    for city_index, city in enumerate(cities, 1):
        if debug:
            debug_info += f"Trying city {city_index}/{len(cities)}: {city}\n"

        result = check_admissions_hit(first_name, last_name, city, state, debug=False)

        if result['hit_found']:
            if debug:
                debug_info += f"Found match with city: {city}\n"
            result['debug_info'] = debug_info if debug else None
            result['cities_tried'] = city_index
            result['total_cities'] = len(cities)
            result['city_found'] = city
            return result

        if debug:
            debug_info += f"  No match with {city}\n"

    if debug:
        debug_info += f"\nNo match found after trying {len(cities)} cities.\n"

    return {
        'first_name': first_name,
        'last_name': last_name,
        'hometown': f"Unknown, {state}",
        'hometown_original': None,
        'hometown_used': None,
        'hit_found': False,
        'mp4_link': None,
        'mp4_accessible': False,
        'details': f'No match found after trying {len(cities)} cities',
        'cities_tried': len(cities),
        'total_cities': len(cities),
        'city_found': None,
        'timestamp': datetime.now().isoformat(),
        'debug_info': debug_info if debug else None
    }

@app.get("/")
async def root():
    return {"message": "Admissions Video Finder API"}

@app.get("/api/counties")
async def get_counties():
    """Get list of all counties with city counts."""
    county_cities_dict, counties_list = load_iowa_counties_and_cities()
    return {
        "counties": [
            {"name": county, "city_count": len(county_cities_dict[county])}
            for county in counties_list
        ]
    }

@app.get("/api/counties/{county}/cities")
async def get_cities_in_county(county: str):
    """Get list of cities in a specific county."""
    county_cities_dict, _ = load_iowa_counties_and_cities()

    if county not in county_cities_dict:
        raise HTTPException(status_code=404, detail="County not found")

    return {"cities": county_cities_dict[county]}

@app.post("/api/search")
async def search_video(request: SearchRequest):
    """Search for a student's admissions video."""
    if not request.first_name or not request.last_name or not request.state:
        raise HTTPException(status_code=400, detail="First name, last name, and state are required")

    # County-based search
    if request.county:
        if request.state.upper() != "IA":
            raise HTTPException(status_code=400, detail="County search currently only supports Iowa (IA)")

        county_cities_dict, _ = load_iowa_counties_and_cities()
        cities_in_county = county_cities_dict.get(request.county, [])

        if not cities_in_county:
            raise HTTPException(status_code=404, detail=f"No cities found for {request.county} County")

        result = search_with_city_iteration(
            request.first_name,
            request.last_name,
            request.state,
            cities_in_county,
            debug=request.show_debug
        )
        result['county_searched'] = request.county
        return result

    # Direct hometown search
    elif request.hometown:
        result = check_admissions_hit(
            request.first_name,
            request.last_name,
            request.hometown,
            request.state,
            debug=request.show_debug
        )
        return result

    else:
        raise HTTPException(status_code=400, detail="Either hometown or county must be provided")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
