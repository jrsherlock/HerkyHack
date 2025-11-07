# 🎓 Your Admissions Video

A sleek, modern, mobile-first web application that allows you to check your admission status and view your personalized admissions video from Iowa's Premium Institute of Higher Learning.

## ✨ Features

- **🎨 Modern Mobile-First Design**: Clean Old Gold and Black UI with smooth animations and responsive layout
- **🔍 Easy Search**: Enter your name and hometown to check your admission status
- **🏛️ County Search Option**: Not sure of your city? Search by county and we'll check all cities for you
- **🎉 Personalized Experience**: Congratulatory message and personalized video if you've been admitted
- **📹 Video Player**: Watch your custom admissions video directly in the browser
- **💾 Easy Downloads**: Download your video to keep and share
- **🐛 Debug Mode**: Technical details for troubleshooting (optional)
- **⚡ Fast & Responsive**: Built with React + Vite for lightning-fast performance

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

2. **Enter your information:**
   - Your first name
   - Your last name
   - Your state (typically "IA" for Iowa)

3. **Choose your search method:**
   - **Direct**: If you know your city, enter it directly (e.g., "Iowa City")
   - **County Search**: Not sure? Select your county and we'll search all cities for you

4. **Click "Find My Video"** to check your admission status

5. **If admitted:** Celebrate and watch your personalized admissions video!

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
