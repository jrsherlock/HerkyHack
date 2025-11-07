# 🔍 Have I Been Admitted?

A tongue-in-cheek web application inspired by Have I Been Pwned that lets you check if your identity appears in Iowa's Premium Institute of Higher Learning admissions database.

**⚠️ Oh no!** If your name is found, your identity may have been compromised... with an acceptance letter.

## ✨ Features

- **🎨 HaveIBeenPwned-Inspired Design**: Dramatic security-breach aesthetic with Old Gold and Black UI
- **🔍 Database Lookup**: Enter your identifying information to scan the admissions database
- **🏛️ County Database Scan**: Don't know your exact city? We'll scan the entire county database
- **⚠️ Breach Notifications**: Dramatic alerts if your identity is found (you've been admitted!)
- **📹 Evidence Preview**: View the "compromised data" (your personalized admissions video)
- **💾 Download Evidence**: Save proof of your identity breach (acceptance)
- **🐛 Debug Mode**: Technical details of the database lookup (optional)
- **⚡ Fast & Responsive**: Built with React + Vite for lightning-fast database queries

## 🏗️ Architecture

### Backend (FastAPI)
- RESTful API for video search
- County and city data management
- MP4 URL generation and accessibility checking
- Hometown permutation logic

### Frontend (React + Vite + Tailwind CSS)
- Modern, component-based UI
- Mobile-first responsive design
- Real-time search updates
- Integrated video player

## 📋 Requirements

- **Python 3.10+**
- **Node.js 18+**
- **npm or yarn**

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script to install all dependencies
./setup.sh

# Start both backend and frontend servers
./start.sh
```

Then open your browser to: **http://localhost:3000**

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run on: **http://localhost:8000**

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on: **http://localhost:3000**

## 📱 How to Use

1. **Open the app** in your browser at http://localhost:3000

2. **Enter your identifying information:**
   - First name
   - Last name
   - State (typically "IA" for Iowa)

3. **Choose database lookup method:**
   - **Direct**: Provide exact city for faster database query
   - **County Database Scan**: Select your county to scan all records in that region

4. **Click "🔍 pwned?"** to query the admissions database

5. **Check the results:**
   - ⚠️ **Oh no — been admitted!** Your identity was found. View the compromised data.
   - ✓ **Good news — no admission found** You're safe... for now.

## 💡 Example Searches

### Direct Method
- **First Name:** john
- **Last Name:** doe
- **Hometown:** Iowa City
- **State:** IA

### County Method
- **First Name:** jane
- **Last Name:** smith
- **County:** Polk County
- **State:** IA

## 🛠️ Development

### Project Structure

```
HerkyHack/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── main.jsx        # React entry point
│   │   └── index.css       # Tailwind CSS styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── tailwind.config.js  # Tailwind configuration
│   └── postcss.config.js   # PostCSS configuration
├── city-county-mapping.csv  # Iowa cities/counties data
├── setup.sh                 # Setup script
├── start.sh                 # Start script
└── README.md               # This file
```

### Building for Production

#### Backend
```bash
cd backend
# Use gunicorn or uvicorn for production
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
# Deploy the 'dist' folder to your hosting service
```

## 🎨 Design Highlights

- **Old Gold & Black Theme**: Classic Iowa colors for a professional look
- **Card-Based Layout**: Clean, organized content sections
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop
- **Iowa Branding**: Old Gold (#FFCD00) and Black (#000000) color scheme
- **Smooth Animations**: Subtle transitions and hover effects
- **Accessible**: Proper labels, semantic HTML, and keyboard navigation

## 🔧 API Endpoints

### GET `/api/counties`
Get list of all Iowa counties with city counts

### GET `/api/counties/{county}/cities`
Get list of cities in a specific county

### POST `/api/search`
Search for a student's video
```json
{
  "first_name": "string",
  "last_name": "string",
  "state": "string",
  "hometown": "string (optional)",
  "county": "string (optional)",
  "show_debug": "boolean"
}
```

## 🤝 How It Works

1. **URL Construction**: Generates URLs for the admissions portal
2. **Permutation Generation**: Creates multiple hometown format variations
3. **Cache Check**: Uses HTTP headers to quickly detect hits
4. **MP4 Verification**: Confirms video file accessibility
5. **Result Display**: Shows video player and download options

## 📊 Data Sources

- `city-county-mapping.csv`: Contains mapping of Iowa cities to their counties
- Used for county-based search functionality

## 📄 License

This project is for educational and research purposes.

## 🙏 Credits

Built with:
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Axios](https://axios-http.com/)

---

Made with ❤️ for Iowa's Premium Institute of Higher Learning community
