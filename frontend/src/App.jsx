import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [state, setState] = useState('IA')
  const [searchMethod, setSearchMethod] = useState('direct')
  const [hometown, setHometown] = useState('')
  const [selectedCounty, setSelectedCounty] = useState('')
  const [counties, setCounties] = useState([])
  const [showDebug, setShowDebug] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [showInstructions, setShowInstructions] = useState(false)

  // Fetch counties on mount
  useEffect(() => {
    fetchCounties()
  }, [])

  const fetchCounties = async () => {
    try {
      const response = await axios.get('/api/counties')
      setCounties(response.data.counties)
    } catch (err) {
      console.error('Error fetching counties:', err)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)

    if (!firstName || !lastName || !state) {
      setError('Please fill in first name, last name, and state')
      return
    }

    if (searchMethod === 'direct' && !hometown) {
      setError('Please enter a hometown')
      return
    }

    if (searchMethod === 'county' && !selectedCounty) {
      setError('Please select a county')
      return
    }

    setLoading(true)

    try {
      const response = await axios.post('/api/search', {
        first_name: firstName,
        last_name: lastName,
        state: state,
        hometown: searchMethod === 'direct' ? hometown : null,
        county: searchMethod === 'county' ? selectedCounty : null,
        show_debug: showDebug
      })

      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during search')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!result?.mp4_link) return

    try {
      const link = document.createElement('a')
      link.href = result.mp4_link
      link.download = result.mp4_link.split('/').pop()
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      setError('Error downloading video')
    }
  }

  const copyDebugInfo = () => {
    if (result?.debug_info) {
      navigator.clipboard.writeText(result.debug_info)
      alert('Debug info copied to clipboard!')
    }
  }

  return (
    <div className="min-h-screen py-4 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 mt-4">
          <h1 className="text-4xl sm:text-5xl font-bold text-iowa-gold mb-3 drop-shadow-lg">
            🎓 Admissions Video Finder
          </h1>
          <p className="text-iowa-gold text-lg sm:text-xl opacity-90">
            Find Iowa's Premium Institute of Higher Learning admissions videos
          </p>
        </div>

        {/* Instructions Toggle */}
        <div className="card mb-6">
          <button
            onClick={() => setShowInstructions(!showInstructions)}
            className="w-full flex items-center justify-between text-left font-semibold text-lg"
          >
            <span>📖 Instructions</span>
            <span className="text-2xl">{showInstructions ? '−' : '+'}</span>
          </button>

          {showInstructions && (
            <div className="mt-4 space-y-3 text-gray-700">
              <div className="p-3 bg-gray-50 rounded-lg">
                <h3 className="font-semibold mb-2">How to use:</h3>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>Enter student's first and last name</li>
                  <li>Choose search method:
                    <ul className="list-disc list-inside ml-6 mt-1">
                      <li>Direct: Enter hometown directly</li>
                      <li>County: Select a county to search all cities</li>
                    </ul>
                  </li>
                  <li>Click "Search for Video"</li>
                  <li>View and download the video if found</li>
                </ol>
              </div>

              <div className="p-3 bg-blue-50 rounded-lg text-sm">
                <h3 className="font-semibold mb-2">Example:</h3>
                <p><strong>Direct Method:</strong></p>
                <p className="ml-3">First: jack, Last: edwards</p>
                <p className="ml-3">Hometown: Iowa City, State: IA</p>
                <p className="mt-2"><strong>County Method:</strong></p>
                <p className="ml-3">First: seth, Last: weibel</p>
                <p className="ml-3">County: Polk County, State: IA</p>
              </div>
            </div>
          )}
        </div>

        {/* Main Search Card */}
        <div className="card mb-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="Enter first name"
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Enter last name"
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  State *
                </label>
                <input
                  type="text"
                  value={state}
                  onChange={(e) => setState(e.target.value.toUpperCase())}
                  placeholder="Enter state (e.g., IA, IL)"
                  className="input-field"
                  maxLength="2"
                  required
                />
              </div>
            </div>

            {/* Search Method Toggle */}
            <div className="border-t-2 border-gray-100 pt-4">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Search Method *
              </label>
              <div className="grid grid-cols-2 gap-3 mb-4">
                <button
                  type="button"
                  onClick={() => setSearchMethod('direct')}
                  className={`py-3 px-4 rounded-xl font-semibold transition-all duration-200 ${
                    searchMethod === 'direct'
                      ? 'bg-iowa-gold text-iowa-black shadow-lg scale-105'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Direct Hometown
                </button>
                <button
                  type="button"
                  onClick={() => setSearchMethod('county')}
                  className={`py-3 px-4 rounded-xl font-semibold transition-all duration-200 ${
                    searchMethod === 'county'
                      ? 'bg-iowa-gold text-iowa-black shadow-lg scale-105'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Search by County
                </button>
              </div>

              {searchMethod === 'direct' ? (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Hometown *
                  </label>
                  <input
                    type="text"
                    value={hometown}
                    onChange={(e) => setHometown(e.target.value)}
                    placeholder="Enter hometown"
                    className="input-field"
                    required={searchMethod === 'direct'}
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    County *
                  </label>
                  <select
                    value={selectedCounty}
                    onChange={(e) => setSelectedCounty(e.target.value)}
                    className="input-field"
                    required={searchMethod === 'county'}
                  >
                    <option value="">Select a county...</option>
                    {counties.map((county) => (
                      <option key={county.name} value={county.name}>
                        {county.name} ({county.city_count} cities)
                      </option>
                    ))}
                  </select>
                  {selectedCounty && (
                    <p className="mt-2 text-sm text-blue-600">
                      📍 Will search through all cities in {selectedCounty} County
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Advanced Options */}
            <div className="border-t-2 border-gray-100 pt-4">
              <details className="cursor-pointer">
                <summary className="text-sm font-semibold text-gray-700">
                  Advanced Options
                </summary>
                <div className="mt-3">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showDebug}
                      onChange={(e) => setShowDebug(e.target.checked)}
                      className="w-5 h-5 text-iowa-gold focus:ring-iowa-gold rounded"
                    />
                    <span className="text-sm text-gray-700">Show debug information</span>
                  </label>
                </div>
              </details>
            </div>

            {/* Search Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-iowa-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                '🎯 Search for Video'
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-box">
            <p className="text-red-800 font-semibold">❌ {error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className={result.hit_found ? 'success-box' : 'error-box'}>
            <h2 className={`text-2xl font-bold mb-4 ${result.hit_found ? 'text-green-800' : 'text-red-800'}`}>
              {result.hit_found ? '✅ Video Found!' : '❌ No Video Found'}
            </h2>

            <div className="space-y-3">
              <p className="text-gray-800">
                <strong>Student:</strong> {result.first_name} {result.last_name}
              </p>
              <p className="text-gray-800">
                <strong>Hometown:</strong> {result.hometown}
              </p>

              {result.county_searched && (
                <div className="info-box">
                  <p className="text-blue-800">
                    🏛️ Searched in <strong>{result.county_searched} County</strong>
                  </p>
                </div>
              )}

              {result.city_found && (
                <div className="info-box">
                  <p className="text-blue-800">
                    📍 Found city: <strong>{result.city_found}</strong> (tried {result.cities_tried} of {result.total_cities} cities)
                  </p>
                </div>
              )}

              {result.hometown_used && result.hometown_original && result.hometown_used !== result.hometown_original && (
                <div className="info-box">
                  <p className="text-blue-800">
                    💡 Used hometown format: <strong>'{result.hometown_used}'</strong> (original: '{result.hometown_original}')
                  </p>
                </div>
              )}

              {result.hit_found && result.mp4_link && (
                <>
                  <p className="text-gray-800 break-all">
                    <strong>MP4 Link:</strong>{' '}
                    <a href={result.mp4_link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      {result.mp4_link}
                    </a>
                  </p>

                  {/* Video Player */}
                  <div className="mt-4 rounded-xl overflow-hidden shadow-lg">
                    <video controls className="w-full" preload="metadata">
                      <source src={result.mp4_link} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>

                  {/* Download Button */}
                  <button
                    onClick={handleDownload}
                    className="btn-secondary mt-4"
                  >
                    💾 Download Video
                  </button>
                </>
              )}

              {!result.hit_found && (
                <p className="text-gray-800">
                  <strong>Details:</strong> {result.details}
                </p>
              )}
            </div>

            {/* Debug Info */}
            {showDebug && result.debug_info && (
              <div className="mt-6 border-t-2 border-gray-200 pt-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-800">Debug Information</h3>
                  <button
                    onClick={copyDebugInfo}
                    className="px-4 py-2 bg-gray-600 text-white text-sm rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    📋 Copy
                  </button>
                </div>
                <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-xs font-mono">
                  {result.debug_info}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-iowa-gold text-sm mt-8 opacity-75">
          <p>Iowa's Premium Institute of Higher Learning Admissions Video Finder</p>
          <p className="mt-1">For educational and research purposes</p>
        </div>
      </div>
    </div>
  )
}

export default App
