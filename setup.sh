#!/bin/bash

echo "🚀 Setting up UIowa Admissions Video Finder..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application, run: ./start.sh"
echo "Or start backend and frontend separately:"
echo "  Backend:  cd backend && python main.py"
echo "  Frontend: cd frontend && npm run dev"
