import requests
from urllib.parse import quote
import re
import time
import csv
import os
from datetime import datetime
import argparse

def debug_http_request(method, url, params=None, headers=None):
    """Print HTTP request details for debugging"""
    print(f"🔧 [HTTP DEBUG] Making {method} request:")
    print(f"   URL: {url}")
    if params:
        print(f"   Parameters: {params}")
    if headers:
        print(f"   Headers: {headers}")

def debug_http_response(response):
    """Print HTTP response details for debugging"""
    print(f"🔧 [HTTP DEBUG] Response received:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response URL: {response.url}")
    print(f"   Headers: {dict(response.headers)}")

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
    
    print(f"🔧 [DEBUG] Generated MP4 URL: {mp4_url}")
    return mp4_url

def check_admissions_hit(first_name, last_name, hometown, state):
    """
    Check if a name and hometown combination results in a hit
    on the University of Iowa admissions portal and extract the MP4 link.
    
    Args:
        first_name (str): First name
        last_name (str): Last name  
        hometown (str): Hometown/city
        state (str): State abbreviation (e.g., 'IA', 'IL')
    
    Returns:
        dict: Results including status code, hit status, MP4 link, and details
    """
    
    # Build the URL manually to match the exact format that works
    encoded_hometown = quote(hometown)  # This encodes spaces as %20
    home_param = f"{encoded_hometown},{state}"
    
    # Build the complete URL manually
    url = f"https://your.admissions.uiowa.edu/?first={first_name.lower()}&last={last_name.lower()}&home={home_param}"
    
    try:
        # Debug: Print the request being made
        debug_http_request("GET", url)
        
        # Make the GET request with a timeout - use the manually built URL without params
        response = requests.get(url, timeout=10)
        
        # Debug: Print the response details
        debug_http_response(response)
        
        # Generate the expected MP4 URL based on naming pattern
        expected_mp4_url = generate_mp4_url(first_name, last_name, hometown, state)
        
        # Check if the generated MP4 URL is accessible
        mp4_accessible = check_mp4_accessibility(expected_mp4_url)
        
        # Analyze the response
        result = {
            'first_name': first_name,
            'last_name': last_name,
            'hometown': f"{hometown}, {state}",
            'url_used': response.url,
            'status_code': response.status_code,
            'hit_found': mp4_accessible,  # Hit found if MP4 is accessible
            'mp4_link': expected_mp4_url if mp4_accessible else None,
            'mp4_accessible': mp4_accessible,
            'details': '',
            'timestamp': datetime.now().isoformat()
        }
        
        # Set details based on MP4 accessibility
        if mp4_accessible:
            result['details'] = 'MP4 file found and accessible'
        else:
            result['details'] = 'MP4 file not accessible (may not exist)'
            
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"🔧 [HTTP DEBUG] Request exception: {str(e)}")
        return {
            'first_name': first_name,
            'last_name': last_name, 
            'hometown': f"{hometown}, {state}",
            'status_code': None,
            'hit_found': False,
            'mp4_link': None,
            'mp4_accessible': False,
            'details': f'Request failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def check_mp4_accessibility(mp4_url):
    """
    Check if the MP4 file is accessible and downloadable.
    """
    print(f"🔧 [DEBUG] Checking MP4 accessibility: {mp4_url}")
    try:
        # Make a HEAD request to check accessibility without downloading the entire file
        debug_http_request("HEAD", mp4_url)
        response = requests.head(mp4_url, timeout=10, allow_redirects=True)
        debug_http_response(response)
        
        # Check if the request was successful and content type is video/mp4
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            print(f"🔧 [DEBUG] Content-Type: {content_type}")
            if 'video/mp4' in content_type or 'application/octet-stream' in content_type:
                print("🔧 [DEBUG] MP4 is accessible via HEAD request")
                return True
        
        # If HEAD request fails or gives unexpected response, try a GET with range
        headers = {'Range': 'bytes=0-1'}  # Just request first 2 bytes to check accessibility
        debug_http_request("GET", mp4_url, headers=headers)
        response = requests.get(mp4_url, headers=headers, timeout=10, stream=True)
        debug_http_response(response)
        
        accessible = response.status_code in [200, 206]
        print(f"🔧 [DEBUG] MP4 accessible via range request: {accessible}")
        return accessible
        
    except requests.exceptions.RequestException as e:
        print(f"🔧 [DEBUG] MP4 accessibility check failed: {str(e)}")
        return False

def download_mp4(mp4_url, filename=None, download_dir="downloads"):
    """
    Download the MP4 file if accessible.
    """
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    if not filename:
        # Extract filename from URL
        filename = mp4_url.split('/')[-1] or f"video_{int(time.time())}.mp4"
    
    filepath = os.path.join(download_dir, filename)
    
    print(f"🔧 [DEBUG] Starting MP4 download: {mp4_url} -> {filepath}")
    
    try:
        debug_http_request("GET", mp4_url)
        response = requests.get(mp4_url, stream=True, timeout=30)
        debug_http_response(response)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            print(f"🔧 [DEBUG] Download size: {total_size} bytes")
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"🔧 [DEBUG] Download completed: {filepath}")
            return True, filepath
        else:
            print(f"🔧 [DEBUG] Download failed with status: {response.status_code}")
            return False, f"Failed to download: HTTP {response.status_code}"
    except Exception as e:
        print(f"🔧 [DEBUG] Download error: {str(e)}")
        return False, f"Download error: {str(e)}"

# ... (rest of the functions remain similar but updated to use the new approach)

def process_csv_bulk_validation(csv_file_path, output_file=None, download_videos=False, delay=2):
    """
    Process a CSV file for bulk validation of name/hometown combinations.
    """
    # Validate CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"❌ Error: CSV file '{csv_file_path}' not found.")
        return []
    
    # Read CSV file
    records = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Map common column names
            fieldnames = [f.lower() for f in reader.fieldnames]
            first_name_col = None
            last_name_col = None
            hometown_col = None
            state_col = None
            
            # Find appropriate columns
            for field in reader.fieldnames:
                lower_field = field.lower()
                if 'first' in lower_field or 'name' in lower_field and 'last' not in lower_field:
                    first_name_col = field
                elif 'last' in lower_field:
                    last_name_col = field
                elif 'home' in lower_field or 'city' in lower_field or 'town' in lower_field:
                    hometown_col = field
                elif 'state' in lower_field:
                    state_col = field
            
            if not first_name_col or not last_name_col:
                print("❌ Error: CSV must contain first name and last name columns.")
                return []
            
            for row in reader:
                records.append({
                    'first_name': row[first_name_col].strip(),
                    'last_name': row[last_name_col].strip(),
                    'hometown': row.get(hometown_col, '').strip() if hometown_col else '',
                    'state': row.get(state_col, 'IA').strip().upper() if state_col else 'IA'
                })
                
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return []
    
    print(f"📊 Processing {len(records)} records from '{csv_file_path}'")
    print("⏳ This may take a while...")
    
    results = []
    download_dir = "bulk_downloads"
    
    for i, record in enumerate(records, 1):
        print(f"🔍 Processing {i}/{len(records)}: {record['first_name']} {record['last_name']}...")
        
        result = check_admissions_hit(
            record['first_name'], 
            record['last_name'], 
            record['hometown'], 
            record['state']
        )
        
        # Download MP4 if requested and accessible
        if download_videos and result['mp4_accessible'] and result['mp4_link']:
            filename = result['mp4_link'].split('/')[-1]
            success, download_path = download_mp4(result['mp4_link'], filename, download_dir)
            result['downloaded'] = success
            result['download_path'] = download_path if success else ''
        else:
            result['downloaded'] = False
            result['download_path'] = ''
        
        results.append(result)
        
        # Progress update
        status_icon = '✅' if result['hit_found'] else '❌'
        print(f"   {status_icon} {result['details']}")
        
        # Respectful delay
        if i < len(records):
            time.sleep(delay)
    
    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"bulk_validation_results_{timestamp}.csv"
    
    # Write results to CSV
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'first_name', 'last_name', 'hometown', 'status_code', 
                'hit_found', 'mp4_link', 'mp4_accessible', 'downloaded',
                'download_path', 'details', 'timestamp'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow({k: result.get(k, '') for k in fieldnames})
        
        print(f"💾 Results saved to: {output_file}")
        
        # Summary statistics
        hits = sum(1 for r in results if r['hit_found'])
        accessible = sum(1 for r in results if r['mp4_accessible'])
        downloaded = sum(1 for r in results if r.get('downloaded', False))
        
        print(f"\n📈 Summary:")
        print(f"   Total records processed: {len(results)}")
        print(f"   Hits found: {hits}")
        print(f"   Accessible MP4s: {accessible}")
        print(f"   Downloaded: {downloaded}")
        
    except Exception as e:
        print(f"❌ Error writing results CSV: {e}")
    
    return results

def create_sample_csv():
    """Create a sample CSV file for users to understand the format."""
    sample_data = [
        ['first_name', 'last_name', 'hometown', 'state'],
        ['jack', 'edwards', 'Iowa City', 'IA'],
        ['seth', 'weibel', 'West Des Moines', 'IA'],
        ['kaitlyn', 'fields', 'Iowa City', 'IA'],
        ['jameson', 'sherlock', 'Iowa City', 'IA'],
    ]
    
    filename = "sample_bulk_validation.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sample_data)
    
    print(f"📝 Sample CSV created: {filename}")
    print("   You can use this as a template for your bulk validation.")
    return filename

def main():
    """Main function to run the admissions checker."""
    
    print("University of Iowa Admissions Bulk Validator")
    print("=" * 55)
    
    # Choose mode
    print("\nChoose mode:")
    print("1. Single check")
    print("2. Batch check (test multiple combinations)")
    print("3. Bulk CSV validation")
    print("4. Create sample CSV template")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "2":
        batch_check()
    elif choice == "3":
        csv_path = input("Enter path to CSV file: ").strip()
        download_choice = input("Download accessible MP4 files? (y/n): ").strip().lower()
        download_videos = download_choice in ['y', 'yes']
        
        delay = input("Delay between requests in seconds (default: 2): ").strip()
        try:
            delay = int(delay) if delay else 2
        except ValueError:
            delay = 2
        
        output_file = input("Output results file (optional, press enter for auto-name): ").strip()
        if not output_file:
            output_file = None
        
        process_csv_bulk_validation(csv_path, output_file, download_videos, delay)
    
    elif choice == "4":
        create_sample_csv()
    
    else:
        # Single check mode
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip() 
        hometown = input("Enter hometown: ").strip()
        state = input("Enter state (e.g., IA, IL): ").strip().upper()
        
        print(f"\nChecking for: {first_name} {last_name} from {hometown}, {state}")
        print("Please wait...")
        
        result = check_admissions_hit(first_name, last_name, hometown, state)
        
        print_results(result)

def print_results(result):
    """Print formatted results."""
    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"Name: {result['first_name']} {result['last_name']}")
    print(f"Hometown: {result['hometown']}")
    print(f"Status Code: {result['status_code']}")
    print(f"Hit Found: {'✅ YES' if result['hit_found'] else '❌ NO'}")
    
    if result['hit_found'] and result['mp4_link']:
        print(f"MP4 Link: {result['mp4_link']}")
        print(f"MP4 Accessible: {'✅ YES' if result['mp4_accessible'] else '❌ NO'}")
        
        # Offer to download the MP4
        if result['mp4_accessible']:
            download_choice = input("\nWould you like to download this MP4? (y/n): ").strip().lower()
            if download_choice in ['y', 'yes']:
                success, message = download_mp4(result['mp4_link'])
                if success:
                    print(f"✅ Download successful: {message}")
                else:
                    print(f"❌ Download failed: {message}")
    
    print(f"\nDetails: {result['details']}")

def batch_check():
    """Function to check multiple combinations at once."""
    test_combinations = [
        ('jack', 'edwards', 'Iowa City', 'IA'),
        ('seth', 'weibel', 'West Des Moines', 'IA'),
        ('kaitlyn', 'fields', 'Iowa City', 'IA'),
        ('jameson', 'sherlock', 'Iowa City', 'IA'),
    ]
    
    print("Batch Checking Multiple Combinations")
    print("=" * 60)
    
    for first, last, town, state in test_combinations:
        print(f"\nChecking: {first} {last} from {town}, {state}")
        result = check_admissions_hit(first, last, town, state)
        
        status_icon = '✅' if result['hit_found'] else '❌'
        accessible_icon = '✅' if result['mp4_accessible'] else '❌'
        
        print(f"  Status: {result['status_code']} - Hit: {status_icon}")
        if result['mp4_link']:
            print(f"  MP4 Link: {result['mp4_link']}")
            print(f"  Accessible: {accessible_icon}")
        print(f"  Details: {result['details']}")
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("The 'requests' package is required. Install it with:")
        print("pip install requests")
        exit(1)
    
    main()