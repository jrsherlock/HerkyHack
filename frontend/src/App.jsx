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
      setError('Missing required identity information — please provide name and state')
      return
    }

    if (searchMethod === 'direct' && !hometown) {
      setError('Location data required — please specify your hometown')
      return
    }

    if (searchMethod === 'county' && !selectedCounty) {
      setError('County selection required to scan database')
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
            Have I Been Admitted?
          </h1>
          <p className="text-iowa-gold text-lg sm:text-xl opacity-90">
            Check if your identity appears in the admissions database
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
                <h3 className="font-semibold mb-2">How the database lookup works:</h3>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>Enter your identifying information (name and location)</li>
                  <li>Select your search method:
                    <ul className="list-disc list-inside ml-6 mt-1">
                      <li>Direct: Provide exact city for faster lookup</li>
                      <li>County: Scan entire county database</li>
                    </ul>
                  </li>
                  <li>Click "pwn — I mean, check — admissions" to query the database</li>
                  <li>If your identity is found: Oh no! You've been admitted!</li>
                </ol>
              </div>

              <div className="p-3 bg-blue-50 rounded-lg text-sm">
                <p className="font-semibold mb-2">⚠️ Warning: If your name appears in the database, your identity may have been compromised... with an acceptance letter.</p>
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
                  placeholder="Your first name"
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
                  placeholder="Your last name"
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
                  placeholder="Your state (e.g., IA, IL)"
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
                    Your Hometown *
                  </label>
                  <input
                    type="text"
                    value={hometown}
                    onChange={(e) => setHometown(e.target.value)}
                    placeholder="Your hometown"
                    className="input-field"
                    required={searchMethod === 'direct'}
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Your County *
                  </label>
                  <select
                    value={selectedCounty}
                    onChange={(e) => setSelectedCounty(e.target.value)}
                    className="input-field"
                    required={searchMethod === 'county'}
                  >
                    <option value="">Select your county...</option>
                    {counties.map((county) => (
                      <option key={county.name} value={county.name}>
                        {county.name} ({county.city_count} cities)
                      </option>
                    ))}
                  </select>
                  {selectedCounty && (
                    <p className="mt-2 text-sm text-blue-600">
                      📍 We'll search all cities in {selectedCounty} County for you
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
                  Scanning database...
                </span>
              ) : (
                '🔍 pwned?'
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
              {result.hit_found ? '⚠️ Oh no — been admitted!' : '✓ Good news — no admission found'}
            </h2>

            <div className="space-y-3">
              {result.hit_found && (
                <div className="p-4 bg-orange-50 border-l-4 border-orange-500 mb-4">
                  <p className="text-gray-800 font-semibold">
                    Identity Compromised: <strong>{result.first_name} {result.last_name}</strong>
                  </p>
                  <p className="text-gray-700 text-sm mt-1">
                    Your identity has been found in the Iowa's Premium Institute of Higher Learning admissions database.
                    An acceptance letter may have been generated with your information.
                  </p>
                </div>
              )}

              <p className="text-gray-800">
                <strong>Identity:</strong> {result.first_name} {result.last_name}
              </p>
              <p className="text-gray-800">
                <strong>Location Data:</strong> {result.hometown}
              </p>

              {result.county_searched && (
                <div className="info-box">
                  <p className="text-blue-800">
                    🔍 Database scan: <strong>{result.county_searched} County</strong>
                  </p>
                </div>
              )}

              {result.city_found && (
                <div className="info-box">
                  <p className="text-blue-800">
                    📍 Located in database: <strong>{result.city_found}</strong> (scanned {result.cities_tried} of {result.total_cities} records)
                  </p>
                </div>
              )}

              {result.hometown_used && result.hometown_original && result.hometown_used !== result.hometown_original && (
                <div className="info-box">
                  <p className="text-blue-800">
                    💾 Matched variation: <strong>'{result.hometown_used}'</strong>
                  </p>
                </div>
              )}

              {result.hit_found && result.mp4_link && (
                <>
                  <div className="mt-4 p-4 bg-red-50 border-2 border-red-300 rounded-xl">
                    <p className="text-gray-800 font-semibold mb-2">⚠️ Compromised Data Preview</p>
                    <p className="text-gray-600 text-sm">A personalized admissions video was found associated with your identity. View the compromised content below:</p>
                  </div>

                  {/* Video Player */}
                  <div className="mt-4 rounded-xl overflow-hidden shadow-lg border-2 border-gray-300">
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
                    💾 Download Evidence
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
          <p>Have I Been Admitted?</p>
          <p className="mt-1">Check if your identity appears in the admissions database</p>
          <p className="mt-2 text-xs">A tongue-in-cheek tribute to Have I Been Pwned</p>
        </div>
      </div>
    </div>
  )
}

export default App
