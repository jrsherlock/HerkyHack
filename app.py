import streamlit as st  # type: ignore
import requests
from urllib.parse import quote
import os
from datetime import datetime
import re
import csv

try:
    import pyperclip  # type: ignore
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="UIowa Admissions Video Finder",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #000000;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .debug-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def debug_http_request(method, url, params=None, headers=None):
    """Print HTTP request details for debugging"""
    debug_info = f"🔧 Making {method} request:\n"
    debug_info += f"   URL: {url}\n"
    if params:
        debug_info += f"   Parameters: {params}\n"
    if headers:
        debug_info += f"   Headers: {headers}\n"
    return debug_info

def debug_http_response(response):
    """Print HTTP response details for debugging"""
    debug_info = f"🔧 Response received:\n"
    debug_info += f"   Status Code: {response.status_code}\n"
    debug_info += f"   Response URL: {response.url}\n"
    debug_info += f"   Headers: {dict(response.headers)}\n"
    return debug_info

def display_debug_info(container, debug_info, height=400):
    """
    Display debug information with a copy to clipboard button.
    Uses st.code() which has built-in copy functionality in newer Streamlit versions.
    
    Args:
        container: Streamlit container to display in (from st.empty())
        debug_info: Debug information string to display
        height: Height of the display area
    """
    if container is None:
        return
    
    # Create a unique key based on debug info hash to avoid duplicate widget IDs
    debug_hash = hash(debug_info) % 100000
    unique_key = f"debug_{debug_hash}"
    copy_key = f"copy_btn_{debug_hash}"
    success_key = f"copy_success_{debug_hash}"
    
    # Store debug info in session state so it persists across reruns
    st.session_state['current_debug_info'] = debug_info
    
    with container.container():
        # Use st.code() which has built-in copy button in Streamlit 1.28+
        # This avoids the rerun issue with regular buttons
        st.code(debug_info, language=None)
        
        # Also provide a manual copy button as fallback
        if CLIPBOARD_AVAILABLE:
            col1, col2 = st.columns([1, 0.2])
            with col1:
                st.caption("💡 Click the copy icon above the code block, or use the button below")
            with col2:
                if st.button("📋 Copy", key=copy_key, use_container_width=True):
                    try:
                        pyperclip.copy(debug_info)
                        st.session_state[success_key] = True
                    except Exception as e:
                        st.error(f"Copy failed: {str(e)}")
            
            if st.session_state.get(success_key, False):
                st.success("Copied to clipboard!")
                st.session_state[success_key] = False
        else:
            st.caption("💡 Install pyperclip for manual copy: `pip install pyperclip`")

def generate_mp4_url(first_name, last_name, hometown, state):
    """
    Generate the expected MP4 URL based on the observed naming pattern.
    Pattern: https://d3mqiwdgu1iop6.cloudfront.net/videos/first-last-hometown-state.mp4
    """
    # Clean and format the components for the filename
    first_clean = first_name.lower().replace(' ', '-')
    last_clean = last_name.lower().replace(' ', '-')
    hometown_clean = hometown.lower().replace(' ', '-').replace(',', '')
    state_clean = state.lower()
    
    # Generate the filename and URL
    filename = f"{first_clean}-{last_clean}-{hometown_clean}-{state_clean}.mp4"
    mp4_url = f"https://d3mqiwdgu1iop6.cloudfront.net/videos/{filename}"
    
    return mp4_url, filename

def check_mp4_accessibility(mp4_url, debug_container=None):
    """
    Check if the MP4 file is accessible and downloadable.
    """
    debug_info = ""
    debug_info += f"🔧 Checking MP4 accessibility: {mp4_url}\n"
    
    try:
        # Make a HEAD request to check accessibility without downloading the entire file
        debug_info += debug_http_request("HEAD", mp4_url)
        response = requests.head(mp4_url, timeout=10, allow_redirects=True)
        debug_info += debug_http_response(response)
        
        # Check if the request was successful and content type is video/mp4
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            debug_info += f"🔧 Content-Type: {content_type}\n"
            if 'video/mp4' in content_type or 'application/octet-stream' in content_type:
                debug_info += "🔧 MP4 is accessible via HEAD request\n"
                if debug_container:
                    display_debug_info(debug_container, debug_info, height=300)
                return True, debug_info
        
        # If HEAD request fails or gives unexpected response, try a GET with range
        headers = {'Range': 'bytes=0-1'}  # Just request first 2 bytes to check accessibility
        debug_info += debug_http_request("GET", mp4_url, headers=headers)
        response = requests.get(mp4_url, headers=headers, timeout=10, stream=True)
        debug_info += debug_http_response(response)
        
        accessible = response.status_code in [200, 206]
        debug_info += f"🔧 MP4 accessible via range request: {accessible}\n"
        
        if debug_container:
            display_debug_info(debug_container, debug_info, height=300)
        return accessible, debug_info
        
    except requests.exceptions.RequestException as e:
        debug_info += f"🔧 MP4 accessibility check failed: {str(e)}\n"
        if debug_container:
            display_debug_info(debug_container, debug_info, height=300)
        return False, debug_info

def download_mp4(mp4_url, filename=None, download_dir="downloads"):
    """
    Download the MP4 file if accessible.
    """
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    if not filename:
        # Extract filename from URL
        filename = mp4_url.split('/')[-1] or f"video_{int(datetime.now().timestamp())}.mp4"
    
    filepath = os.path.join(download_dir, filename)
    
    try:
        response = requests.get(mp4_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True, filepath
        else:
            return False, f"Failed to download: HTTP {response.status_code}"
    except Exception as e:
        return False, f"Download error: {str(e)}"

@st.cache_data
def load_iowa_counties_and_cities(csv_path="city-county-mapping.csv"):
    """
    Parse the Iowa cities CSV and extract counties with their cities.
    Returns a dictionary mapping county names to lists of city names.
    Also returns a list of all counties sorted alphabetically.
    """
    county_cities = {}
    
    if not os.path.exists(csv_path):
        st.error(f"CSV file not found: {csv_path}")
        return {}, []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Process each row in the CSV
            for row in csv_reader:
                city = row.get('City', '').strip()
                county = row.get('County', '').strip()
                
                # Skip empty rows
                if not city or not county:
                    continue
                
                # Normalize whitespace
                city = re.sub(r'\s+', ' ', city)
                county = re.sub(r'\s+', ' ', county)
                
                # Initialize county if not seen before
                if county not in county_cities:
                    county_cities[county] = []
                
                # Add city to county if not already present
                if city not in county_cities[county]:
                    county_cities[county].append(city)
        
        # Sort cities within each county and counties themselves
        for county in county_cities:
            county_cities[county].sort()
        
        counties = sorted(county_cities.keys())
        
        return county_cities, counties
        
    except Exception as e:
        st.error(f"Error parsing CSV: {str(e)}")
        return {}, []

@st.cache_data
def load_iowa_cities(csv_path="city-county-mapping.csv"):
    """
    Parse the Iowa cities CSV and extract city names.
    Returns a list of city names (for backward compatibility).
    """
    county_cities, counties = load_iowa_counties_and_cities(csv_path)
    
    # Flatten all cities from all counties
    all_cities = []
    for cities in county_cities.values():
        all_cities.extend(cities)
    
    # Remove duplicates and sort
    all_cities = sorted(list(set(all_cities)))
    return all_cities

def generate_hometown_permutations(hometown):
    """
    Generate multiple formatting permutations of the hometown to try.
    This helps handle variations in spacing and formatting.
    """
    permutations = []
    
    # 1. Original format (as entered)
    permutations.append(hometown)
    
    # 2. Try capitalizing just the first character (handles "lowa City" -> "Lowa City")
    if hometown and hometown[0].islower():
        first_capitalized = hometown[0].upper() + hometown[1:]
        if first_capitalized != hometown:
            permutations.append(first_capitalized)
    
    # 2b. Fix common typo: "lowa" -> "Iowa" (handles CSV data issue)
    if hometown and hometown.lower().startswith('lowa'):
        # Replace "lowa" or "Lowa" at the start with "Iowa"
        iowa_fixed = re.sub(r'^[Ll]owa\b', 'Iowa', hometown)
        if iowa_fixed != hometown and iowa_fixed not in permutations:
            permutations.append(iowa_fixed)
    
    # 3. Try title case (capitalize first letter of each word)
    # This handles cases like "west des moines" -> "West Des Moines"
    title_case = hometown.title()
    if title_case != hometown and title_case not in permutations:
        permutations.append(title_case)
    
    # 4. Normalize spaces (ensure single spaces between words)
    normalized = ' '.join(hometown.split())
    if normalized != hometown and normalized not in permutations:
        permutations.append(normalized)
    
    # 5. Remove all spaces
    no_spaces = hometown.replace(' ', '')
    if no_spaces != hometown:
        permutations.append(no_spaces)
    
    # 6. Insert spaces before capital letters (e.g., "DesMoines" -> "Des Moines")
    # This handles cases where words are concatenated without spaces
    spaced_capitals = re.sub(r'([a-z])([A-Z])', r'\1 \2', hometown)
    if spaced_capitals != hometown and spaced_capitals not in permutations:
        permutations.append(spaced_capitals)
    
    # 7. Try inserting spaces before capital letters in the no-spaces version
    if no_spaces != hometown:
        spaced_from_no_spaces = re.sub(r'([a-z])([A-Z])', r'\1 \2', no_spaces)
        if spaced_from_no_spaces != no_spaces and spaced_from_no_spaces not in permutations:
            permutations.append(spaced_from_no_spaces)
    
    # 8. Try common multi-word patterns (e.g., "WestDesMoines" -> "West Des Moines")
    # Split on capital letters and join with spaces
    if re.search(r'[a-z][A-Z]', hometown):
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', hometown)
        if len(words) > 1:
            reconstructed = ' '.join(words)
            if reconstructed not in permutations:
                permutations.append(reconstructed)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_permutations = []
    for perm in permutations:
        if perm not in seen:
            seen.add(perm)
            unique_permutations.append(perm)
    
    return unique_permutations

def fast_check_cache_hit(url, timeout=5):
    """
    Fast check for cache hit using X-Cache header.
    Returns (is_hit, response) where is_hit is True if X-Cache contains 'Hit'.
    This is much faster than checking MP4 accessibility.
    """
    try:
        response = requests.get(url, timeout=timeout)
        cache_header = response.headers.get('X-Cache', '').lower()
        is_hit = 'hit' in cache_header
        return is_hit, response
    except requests.exceptions.RequestException:
        return False, None

def check_admissions_hit(first_name, last_name, hometown, state, debug_container=None, progress_callback=None):
    """
    Check if a name and hometown combination results in a hit
    on the University of Iowa admissions portal and extract the MP4 link.
    Tries multiple hometown formatting permutations to handle variations.
    
    Args:
        first_name: Student's first name
        last_name: Student's last name
        hometown: Hometown (can be None for city iteration)
        state: State code
        debug_container: Streamlit container for debug output
        progress_callback: Optional callback function(current, total, current_city) for progress updates
    """
    debug_info = ""
    
    # Generate hometown permutations to try
    hometown_permutations = generate_hometown_permutations(hometown)
    debug_info += f"🔧 Generated {len(hometown_permutations)} hometown permutations to try:\n"
    for i, perm in enumerate(hometown_permutations, 1):
        debug_info += f"   {i}. '{perm}'\n"
    debug_info += "\n"
    
    # Try each permutation until we find a hit
    for perm_index, hometown_perm in enumerate(hometown_permutations, 1):
        if progress_callback:
            progress_callback(perm_index, len(hometown_permutations), hometown_perm)
        
        debug_info += f"🔧 Trying permutation {perm_index}/{len(hometown_permutations)}: '{hometown_perm}'\n"
        
        # Build the URL manually to match the exact format that works
        encoded_hometown = quote(hometown_perm)  # This encodes spaces as %20
        home_param = f"{encoded_hometown},{state}"
        
        # Build the complete URL manually
        url = f"https://your.admissions.uiowa.edu/?first={first_name.lower()}&last={last_name.lower()}&home={home_param}"
        
        try:
            # Check cache header first to quickly determine if this is a hit
            is_cache_hit, response = fast_check_cache_hit(url, timeout=5)
            
            if not response:
                debug_info += f"❌ Request failed for '{hometown_perm}', trying next...\n\n"
                continue
            
            # Debug: Print the request being made
            debug_info += debug_http_request("GET", url)
            debug_info += debug_http_response(response)
            
            # If cache shows miss, skip expensive MP4 check
            if not is_cache_hit:
                debug_info += f"❌ Cache miss for '{hometown_perm}', skipping MP4 check...\n\n"
                continue
            
            # Only check MP4 if we have a cache hit
            expected_mp4_url, expected_filename = generate_mp4_url(first_name, last_name, hometown_perm, state)
            debug_info += f"🔧 Generated MP4 URL: {expected_mp4_url}\n"
            
            # Check if the generated MP4 URL is accessible
            mp4_accessible, mp4_debug = check_mp4_accessibility(expected_mp4_url, None)
            debug_info += mp4_debug
            
            # If we found a hit, return immediately
            if mp4_accessible:
                debug_info += f"✅ Hit found with permutation '{hometown_perm}'!\n"
                
                # Analyze the response
                result = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'hometown': f"{hometown_perm}, {state}",
                    'hometown_original': hometown,
                    'hometown_used': hometown_perm,
                    'url_used': response.url,
                    'status_code': response.status_code,
                    'hit_found': True,
                    'mp4_link': expected_mp4_url,
                    'mp4_accessible': True,
                    'details': f'MP4 file found and accessible (used permutation: "{hometown_perm}")',
                    'permutation_index': perm_index,
                    'total_permutations': len(hometown_permutations),
                    'timestamp': datetime.now().isoformat(),
                    'debug_info': debug_info
                }
                
                if debug_container:
                    display_debug_info(debug_container, debug_info, height=400)
                    
                return result
            else:
                debug_info += f"❌ No hit with permutation '{hometown_perm}', trying next...\n\n"
                
        except requests.exceptions.RequestException as e:
            debug_info += f"🔧 Request exception with permutation '{hometown_perm}': {str(e)}\n"
            debug_info += f"   Trying next permutation...\n\n"
            continue
    
    # If we get here, none of the permutations worked
    debug_info += f"❌ No hit found with any of the {len(hometown_permutations)} permutations tried.\n"
    
    # Return failure result with the last attempted permutation
    result = {
        'first_name': first_name,
        'last_name': last_name,
        'hometown': f"{hometown}, {state}" if hometown else f"Unknown, {state}",
        'hometown_original': hometown,
        'hometown_used': hometown_permutations[-1] if hometown_permutations else hometown,
        'url_used': None,
        'status_code': None,
        'hit_found': False,
        'mp4_link': None,
        'mp4_accessible': False,
        'details': f'MP4 file not accessible after trying {len(hometown_permutations)} permutations',
        'permutation_index': len(hometown_permutations),
        'total_permutations': len(hometown_permutations),
        'timestamp': datetime.now().isoformat(),
        'debug_info': debug_info
    }
    
    if debug_container:
        display_debug_info(debug_container, debug_info, height=400)
        
    return result

def search_with_city_iteration(first_name, last_name, state, cities, debug_container=None, progress_bar=None):
    """
    Search for a student by iterating through a list of cities.
    Stops when a hit is found.
    
    Args:
        first_name: Student's first name
        last_name: Student's last name
        state: State code
        cities: List of city names to try
        debug_container: Streamlit container for debug output
        progress_bar: Streamlit progress bar component
    """
    debug_info = f"🔍 Searching through {len(cities)} cities for {first_name} {last_name}...\n\n"
    
    if progress_bar:
        progress_bar.progress(0)
    
    # Iterate through cities sequentially
    for city_index, city in enumerate(cities, 1):
        if progress_bar:
            progress_bar.progress(city_index / len(cities))
        
        debug_info += f"📍 Trying city {city_index}/{len(cities)}: {city}\n"
        
        # Try this city with all its permutations
        result = check_admissions_hit(
            first_name, 
            last_name, 
            city, 
            state, 
            debug_container=None,  # Don't show individual city debug, only final
            progress_callback=None
        )
        
        # If we found a hit, return immediately
        if result['hit_found']:
            debug_info += f"✅ Found match with city: {city}\n"
            debug_info += result['debug_info']
            result['debug_info'] = debug_info
            result['cities_tried'] = city_index
            result['total_cities'] = len(cities)
            result['city_found'] = city
            
            if debug_container:
                display_debug_info(debug_container, debug_info, height=400)
            
            if progress_bar:
                progress_bar.progress(1.0)
            
            return result
        
        # Include detailed debug info for failed cities if debug is enabled
        if debug_container:
            debug_info += result['debug_info']
            # Update debug output in real-time
            display_debug_info(debug_container, debug_info, height=400)
        else:
            debug_info += f"   ❌ No match with {city}\n"
    
    # If we get here, no city worked
    debug_info += f"\n❌ No match found after trying {len(cities)} cities.\n"
    
    if progress_bar:
        progress_bar.progress(1.0)
    
    result = {
        'first_name': first_name,
        'last_name': last_name,
        'hometown': f"Unknown, {state}",
        'hometown_original': None,
        'hometown_used': None,
        'url_used': None,
        'status_code': None,
        'hit_found': False,
        'mp4_link': None,
        'mp4_accessible': False,
        'details': f'No match found after trying {len(cities)} cities',
        'cities_tried': len(cities),
        'total_cities': len(cities),
        'city_found': None,
        'timestamp': datetime.now().isoformat(),
        'debug_info': debug_info
    }
    
    if debug_container:
        display_debug_info(debug_container, debug_info, height=400)
    
    return result

def main():
    # Header
    st.markdown('<div class="main-header">🎓 University of Iowa Admissions Video Finder</div>', unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.info("""
        This app helps you find and download student video profiles 
        from the University of Iowa admissions portal.
        
        Enter the student's information to search for their video.
        """)
        
        st.header("Instructions")
        st.write("""
        1. Enter the student's first and last name
        2. Choose search method:
           - Enter hometown directly, OR
           - Select a county to search all cities in that county
        3. Click 'Search for Video'
        4. Download the video if available
        """)
        
        st.header("Example")
        st.code("""
Method 1 - Direct:
First Name: jack
Last Name: edwards  
Hometown: Iowa City
State: IA

Method 2 - County Search:
First Name: seth
Last Name: weibel
County: Polk County
State: IA
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Student Information")
        first_name = st.text_input("First Name", value="jack", placeholder="Enter first name")
        last_name = st.text_input("Last Name", value="edwards", placeholder="Enter last name")
        state = st.text_input("State", value="IA", placeholder="Enter state (e.g., IA, IL)")
        
        # Load counties and cities data
        county_cities_dict, counties_list = load_iowa_counties_and_cities()
        
        # Hometown input with county search option
        st.markdown("**Search Method**")
        search_method = st.radio(
            "Choose search method:",
            ["Enter hometown directly", "Search by county"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        hometown = None
        selected_county = None
        
        if search_method == "Enter hometown directly":
            hometown = st.text_input("Hometown", value="Iowa City", placeholder="Enter hometown")
            if not hometown or hometown.strip() == "":
                hometown = None
        else:
            # County selection dropdown
            if counties_list:
                selected_county = st.selectbox(
                    "Select County",
                    [""] + counties_list,
                    format_func=lambda x: f"{x} ({len(county_cities_dict.get(x, []))} cities)" if x else "Select a county..."
                )
                if selected_county:
                    cities_in_county = county_cities_dict.get(selected_county, [])
                    if cities_in_county:
                        st.info(f"📍 Will search through {len(cities_in_county)} cities in {selected_county} County")
                    else:
                        st.warning(f"⚠️ No cities found for {selected_county} County")
            else:
                st.error("❌ Could not load counties from CSV. Please check that city-county-mapping.csv exists.")
        
        # Advanced options
        with st.expander("Advanced Options"):
            show_debug = st.checkbox("Show debug information", value=False)
            auto_download = st.checkbox("Auto-download when video found", value=False)
    
    with col2:
        st.subheader("Actions")
        
        # Store and retrieve search results from session state
        search_key = f"search_result_{first_name}_{last_name}_{state}_{selected_county or hometown}"
        
        # Check if we have a stored result
        stored_result = st.session_state.get('last_search_result')
        
        if st.button("🎯 Search for Video", type="primary", use_container_width=True):
            st.session_state['search_button_clicked'] = True
            if not first_name or not last_name or not state:
                st.error("Please fill in first name, last name, and state")
            else:
                # Clear previous result
                st.session_state['last_search_result'] = None
                
                # Create debug container and progress bar
                debug_container = st.empty()
                progress_bar = st.empty()
                
                # Determine search mode
                if selected_county:
                    # County-based search mode
                    if state.upper() != "IA":
                        st.warning("⚠️ County search currently only supports Iowa (IA)")
                    
                    cities_in_county = county_cities_dict.get(selected_county, [])
                    
                    if not cities_in_county:
                        st.error(f"❌ No cities found for {selected_county} County in CSV.")
                    else:
                        st.info(f"🔍 Searching through {len(cities_in_county)} cities in {selected_county} County...")
                        
                        result = search_with_city_iteration(
                            first_name, 
                            last_name, 
                            state, 
                            cities_in_county,
                            debug_container if show_debug else None,
                            progress_bar
                        )
                        
                        # Add county info to result (always, not just when found)
                        result['county_searched'] = selected_county
                elif hometown:
                    # Normal search mode with provided hometown
                    with st.spinner("Searching for video..."):
                        result = check_admissions_hit(
                            first_name, last_name, hometown, state, 
                            debug_container if show_debug else None
                        )
                else:
                    st.error("❌ Please either enter a hometown or select a county to search.")
                    result = None
                
                # Store result in session state so it persists across reruns
                if result:
                    st.session_state['last_search_result'] = result
                    st.session_state['last_search_debug'] = result.get('debug_info', '')
                
                # Display results
                if result and result.get('hit_found'):
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success(f"✅ **Video Found!**")
                    st.write(f"**Student:** {result['first_name']} {result['last_name']}")
                    st.write(f"**Hometown:** {result['hometown']}")
                    
                    # Show county info if applicable
                    if 'county_searched' in result:
                        st.info(f"🏛️ Searched in **{result['county_searched']} County**")
                    
                    # Show city iteration info if applicable
                    if 'city_found' in result and result['city_found']:
                        st.info(f"📍 Found city: **{result['city_found']}** (tried {result.get('cities_tried', 0)} of {result.get('total_cities', 0)} cities)")
                    
                    # Show permutation info if different from original
                    if 'hometown_original' in result and result['hometown_original'] and result['hometown_original'] != result.get('hometown_used', ''):
                        st.info(f"💡 Used hometown format: '{result['hometown_used']}' (original: '{result['hometown_original']}')")
                    if 'permutation_index' in result:
                        st.caption(f"Found on permutation {result['permutation_index']} of {result['total_permutations']}")
                    st.write(f"**MP4 Link:** {result['mp4_link']}")
                    
                    # Display video
                    st.video(result['mp4_link'])
                    
                    # Download button
                    if st.button("💾 Download Video", type="secondary", use_container_width=True):
                        with st.spinner("Downloading video..."):
                            success, message = download_mp4(result['mp4_link'])
                            if success:
                                st.success(f"✅ Download successful!")
                                st.info(f"File saved as: `{message}`")
                                
                                # Offer to show file location
                                if st.button("📁 Show in File Explorer"):
                                    os.system(f'open "{os.path.dirname(message)}"')
                            else:
                                st.error(f"❌ Download failed: {message}")
                    
                    # Auto-download if enabled
                    elif auto_download:
                        with st.spinner("Auto-downloading video..."):
                            success, message = download_mp4(result['mp4_link'])
                            if success:
                                st.success(f"✅ Auto-download successful!")
                                st.info(f"File saved as: `{message}`")
                            else:
                                st.error(f"❌ Auto-download failed: {message}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                elif result:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"❌ **No Video Found**")
                    st.write(f"**Student:** {result['first_name']} {result['last_name']}")
                    st.write(f"**Hometown:** {result['hometown']}")
                    
                    # Show county info if applicable
                    if 'county_searched' in result:
                        st.write(f"**County Searched:** {result['county_searched']} County")
                    
                    # Show city iteration info if applicable
                    if 'total_cities' in result:
                        st.write(f"**Cities Tried:** {result.get('cities_tried', 0)} of {result['total_cities']}")
                    if 'total_permutations' in result:
                        st.write(f"**Permutations Tried:** {result['total_permutations']}")
                    st.write(f"**Details:** {result['details']}")
                    
                    # Show generated URL for debugging (only if we have a hometown)
                    if hometown and hometown.strip():
                        expected_url, _ = generate_mp4_url(first_name, last_name, hometown, state)
                        st.write(f"**Expected URL:** {expected_url}")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Display stored results if they exist (for persistence across reruns)
        if stored_result and not st.session_state.get('search_button_clicked', False):
            result = stored_result
            debug_container = st.empty() if show_debug else None
            
            if result.get('hit_found'):
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"✅ **Video Found!**")
                st.write(f"**Student:** {result['first_name']} {result['last_name']}")
                st.write(f"**Hometown:** {result['hometown']}")
                
                if 'county_searched' in result:
                    st.info(f"🏛️ Searched in **{result['county_searched']} County**")
                
                if 'city_found' in result and result['city_found']:
                    st.info(f"📍 Found city: **{result['city_found']}** (tried {result.get('cities_tried', 0)} of {result.get('total_cities', 0)} cities)")
                
                if 'hometown_original' in result and result['hometown_original'] and result['hometown_original'] != result.get('hometown_used', ''):
                    st.info(f"💡 Used hometown format: '{result['hometown_used']}' (original: '{result['hometown_original']}')")
                if 'permutation_index' in result:
                    st.caption(f"Found on permutation {result['permutation_index']} of {result['total_permutations']}")
                st.write(f"**MP4 Link:** {result['mp4_link']}")
                
                st.video(result['mp4_link'])
                
                if st.button("💾 Download Video", type="secondary", use_container_width=True, key="download_stored"):
                    with st.spinner("Downloading video..."):
                        success, message = download_mp4(result['mp4_link'])
                        if success:
                            st.success(f"✅ Download successful!")
                            st.info(f"File saved as: `{message}`")
                        else:
                            st.error(f"❌ Download failed: {message}")
                
                if debug_container:
                    display_debug_info(debug_container, result.get('debug_info', ''), height=400)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ **No Video Found**")
                st.write(f"**Student:** {result['first_name']} {result['last_name']}")
                st.write(f"**Hometown:** {result['hometown']}")
                
                if 'county_searched' in result:
                    st.write(f"**County Searched:** {result['county_searched']} County")
                
                if 'total_cities' in result:
                    st.write(f"**Cities Tried:** {result.get('cities_tried', 0)} of {result['total_cities']}")
                if 'total_permutations' in result:
                    st.write(f"**Permutations Tried:** {result['total_permutations']}")
                st.write(f"**Details:** {result['details']}")
                
                if debug_container:
                    display_debug_info(debug_container, result.get('debug_info', ''), height=400)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset search button flag
        if st.session_state.get('search_button_clicked', False):
            st.session_state['search_button_clicked'] = False
    
    # Initialize session state for form fields
    if 'first_name' not in st.session_state:
        st.session_state.first_name = "jack"
    if 'last_name' not in st.session_state:
        st.session_state.last_name = "edwards"
    if 'hometown' not in st.session_state:
        st.session_state.hometown = "Iowa City"
    if 'state' not in st.session_state:
        st.session_state.state = "IA"

if __name__ == "__main__":
    # Check for required packages
    try:
        import requests
    except ImportError:
        st.error("The 'requests' package is required. Please install it with: `pip install requests`")
        st.stop()
    
    main()