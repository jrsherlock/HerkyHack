# University of Iowa Admissions Video Finder

A Streamlit web application that helps you find and download student video profiles from the University of Iowa admissions portal.

## Features

- **Direct Hometown Search**: Enter a student's name and hometown directly to find their video
- **County-Based Search**: Select an Iowa county to automatically search through all cities in that county
- **Smart Permutation Handling**: Automatically tries multiple formatting variations of hometown names to handle encoding and formatting differences
- **Debug Information**: Detailed debug output showing all search attempts, HTTP requests, and responses
- **Copy to Clipboard**: Easy copy functionality for debug information
- **Video Download**: Download found videos directly from the application

## Requirements

- Python 3.10+
- Streamlit >= 1.28.0
- requests >= 2.31.0
- pyperclip >= 1.8.2

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd HerkyHack
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser to the URL shown (typically http://localhost:8501)

3. Enter student information:
   - First Name
   - Last Name
   - State (typically "IA" for Iowa)
   - Choose search method:
     - **Direct**: Enter hometown directly
     - **County Search**: Select a county from the dropdown to search all cities in that county

4. Click "Search for Video" to find the student's video

5. If found, you can view the video and download it using the download button

## How It Works

The application searches the University of Iowa admissions portal by constructing URLs with the student's information. It:

1. Generates multiple permutations of the hometown name to handle formatting variations
2. Checks for cache hits using HTTP headers for faster detection
3. Verifies MP4 file accessibility
4. Displays results with detailed debug information

## Data Sources

- `city-county-mapping.csv`: Contains mapping of Iowa cities to their counties
- Used for county-based search functionality

## License

This project is for educational and research purposes.

