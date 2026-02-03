'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import {
  FaPlane,
  FaHotel,
  FaSearch,
  FaExchangeAlt,
  FaClock,
  FaStar,
  FaMapMarkerAlt,
  FaWifi,
  FaSwimmingPool,
  FaParking,
  FaUtensils,
} from 'react-icons/fa'
import { api } from '@/lib/api'
import { useAuthGuard } from '@/hooks/useAuthGuard'
import Navbar from '@/components/Navbar'
import LoadingSpinner from '@/components/LoadingSpinner'
import { FlightOffer, HotelOffer } from '@/types'

type Tab = 'flights' | 'hotels'

interface AutocompleteOption {
  code: string
  name: string
  label: string
}

export default function SearchPage() {
  const { user, isLoading: authLoading } = useAuthGuard()
  const [activeTab, setActiveTab] = useState<Tab>('flights')

  // Flight state
  const [origin, setOrigin] = useState('')
  const [originCode, setOriginCode] = useState('')
  const [destination, setDestination] = useState('')
  const [destinationCode, setDestinationCode] = useState('')
  const [departureDate, setDepartureDate] = useState('')
  const [returnDate, setReturnDate] = useState('')
  const [passengers, setPassengers] = useState(1)
  const [flightClass, setFlightClass] = useState('economy')
  const [nonStop, setNonStop] = useState(false)
  const [flightResults, setFlightResults] = useState<FlightOffer[]>([])
  const [flightSearching, setFlightSearching] = useState(false)

  // Hotel state
  const [city, setCity] = useState('')
  const [cityCode, setCityCode] = useState('')
  const [checkIn, setCheckIn] = useState('')
  const [checkOut, setCheckOut] = useState('')
  const [guests, setGuests] = useState(1)
  const [rooms, setRooms] = useState(1)
  const [minRating, setMinRating] = useState(0)
  const [maxPrice, setMaxPrice] = useState(0)
  const [hotelResults, setHotelResults] = useState<HotelOffer[]>([])
  const [hotelSearching, setHotelSearching] = useState(false)

  // Autocomplete state
  const [originOptions, setOriginOptions] = useState<AutocompleteOption[]>([])
  const [destOptions, setDestOptions] = useState<AutocompleteOption[]>([])
  const [cityOptions, setCityOptions] = useState<AutocompleteOption[]>([])
  const [showOriginDropdown, setShowOriginDropdown] = useState(false)
  const [showDestDropdown, setShowDestDropdown] = useState(false)
  const [showCityDropdown, setShowCityDropdown] = useState(false)

  const [searchError, setSearchError] = useState('')

  const originRef = useRef<HTMLDivElement>(null)
  const destRef = useRef<HTMLDivElement>(null)
  const cityRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<NodeJS.Timeout>()

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (originRef.current && !originRef.current.contains(e.target as Node)) {
        setShowOriginDropdown(false)
      }
      if (destRef.current && !destRef.current.contains(e.target as Node)) {
        setShowDestDropdown(false)
      }
      if (cityRef.current && !cityRef.current.contains(e.target as Node)) {
        setShowCityDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const debounceSearch = useCallback(
    (query: string, type: 'origin' | 'destination' | 'city') => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
      if (query.length < 2) {
        if (type === 'origin') setOriginOptions([])
        else if (type === 'destination') setDestOptions([])
        else setCityOptions([])
        return
      }
      debounceRef.current = setTimeout(async () => {
        try {
          if (type === 'city') {
            const data = await api.searchCities(query)
            const options = (data.results || data || []).map((c: any) => ({
              code: c.city_code || c.code || c.iataCode,
              name: c.name || c.city_name,
              label: `${c.name || c.city_name} (${c.city_code || c.code || c.iataCode})`,
            }))
            setCityOptions(options)
            setShowCityDropdown(true)
          } else {
            const data = await api.searchAirports(query)
            const options = (data.results || data || []).map((a: any) => ({
              code: a.iata_code || a.code || a.iataCode,
              name: a.name || a.airport_name,
              label: `${a.name || a.airport_name} (${a.iata_code || a.code || a.iataCode})`,
            }))
            if (type === 'origin') {
              setOriginOptions(options)
              setShowOriginDropdown(true)
            } else {
              setDestOptions(options)
              setShowDestDropdown(true)
            }
          }
        } catch {
          // autocomplete failure is non-critical
        }
      }, 300)
    },
    []
  )

  const searchFlights = async (e: React.FormEvent) => {
    e.preventDefault()
    setSearchError('')
    if (!originCode || !destinationCode || !departureDate) {
      setSearchError('Please fill in origin, destination, and departure date')
      return
    }
    setFlightSearching(true)
    setFlightResults([])
    try {
      const data = await api.searchFlights({
        origin: originCode,
        destination: destinationCode,
        departure_date: departureDate,
        return_date: returnDate || undefined,
        passengers,
        flight_class: flightClass,
        non_stop: nonStop,
      })
      setFlightResults(data.results || [])
      if ((data.results || []).length === 0) {
        setSearchError('No flights found for your search criteria')
      }
    } catch (err: any) {
      setSearchError(err.response?.data?.detail || 'Failed to search flights')
    } finally {
      setFlightSearching(false)
    }
  }

  const searchHotels = async (e: React.FormEvent) => {
    e.preventDefault()
    setSearchError('')
    if (!cityCode || !checkIn || !checkOut) {
      setSearchError('Please fill in city, check-in, and check-out dates')
      return
    }
    setHotelSearching(true)
    setHotelResults([])
    try {
      const data = await api.searchHotels({
        city_code: cityCode,
        check_in: checkIn,
        check_out: checkOut,
        guests,
        rooms,
        min_rating: minRating || undefined,
        max_price: maxPrice || undefined,
      })
      setHotelResults(data.results || [])
      if ((data.results || []).length === 0) {
        setSearchError('No hotels found for your search criteria')
      }
    } catch (err: any) {
      setSearchError(err.response?.data?.detail || 'Failed to search hotels')
    } finally {
      setHotelSearching(false)
    }
  }

  if (authLoading) {
    return <LoadingSpinner message="Loading..." />
  }

  if (!user) return null

  const amenityIcon = (amenity: string) => {
    const lower = amenity.toLowerCase()
    if (lower.includes('wifi') || lower.includes('internet')) return <FaWifi />
    if (lower.includes('pool') || lower.includes('swim')) return <FaSwimmingPool />
    if (lower.includes('parking')) return <FaParking />
    if (lower.includes('restaurant') || lower.includes('breakfast') || lower.includes('dining'))
      return <FaUtensils />
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Search</h1>

        {/* Tabs */}
        <div className="flex mb-6 bg-white rounded-lg shadow-sm overflow-hidden">
          <button
            onClick={() => { setActiveTab('flights'); setSearchError('') }}
            className={`flex-1 flex items-center justify-center space-x-2 py-3 font-medium transition-colors ${
              activeTab === 'flights'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <FaPlane />
            <span>Flights</span>
          </button>
          <button
            onClick={() => { setActiveTab('hotels'); setSearchError('') }}
            className={`flex-1 flex items-center justify-center space-x-2 py-3 font-medium transition-colors ${
              activeTab === 'hotels'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <FaHotel />
            <span>Hotels</span>
          </button>
        </div>

        {searchError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {searchError}
          </div>
        )}

        {/* Flights form */}
        {activeTab === 'flights' && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <form onSubmit={searchFlights} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Origin */}
                <div ref={originRef} className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Origin</label>
                  <input
                    type="text"
                    value={origin}
                    onChange={(e) => {
                      setOrigin(e.target.value)
                      setOriginCode('')
                      debounceSearch(e.target.value, 'origin')
                    }}
                    onFocus={() => originOptions.length > 0 && setShowOriginDropdown(true)}
                    placeholder="City or airport"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                  {showOriginDropdown && originOptions.length > 0 && (
                    <ul className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg mt-1 shadow-lg max-h-48 overflow-y-auto">
                      {originOptions.map((opt) => (
                        <li
                          key={opt.code}
                          onClick={() => {
                            setOrigin(opt.label)
                            setOriginCode(opt.code)
                            setShowOriginDropdown(false)
                          }}
                          className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-sm text-gray-900"
                        >
                          {opt.label}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Destination */}
                <div ref={destRef} className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Destination</label>
                  <input
                    type="text"
                    value={destination}
                    onChange={(e) => {
                      setDestination(e.target.value)
                      setDestinationCode('')
                      debounceSearch(e.target.value, 'destination')
                    }}
                    onFocus={() => destOptions.length > 0 && setShowDestDropdown(true)}
                    placeholder="City or airport"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                  {showDestDropdown && destOptions.length > 0 && (
                    <ul className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg mt-1 shadow-lg max-h-48 overflow-y-auto">
                      {destOptions.map((opt) => (
                        <li
                          key={opt.code}
                          onClick={() => {
                            setDestination(opt.label)
                            setDestinationCode(opt.code)
                            setShowDestDropdown(false)
                          }}
                          className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-sm text-gray-900"
                        >
                          {opt.label}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Departure Date</label>
                  <input
                    type="date"
                    value={departureDate}
                    onChange={(e) => setDepartureDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Return Date <span className="text-gray-400">(optional)</span>
                  </label>
                  <input
                    type="date"
                    value={returnDate}
                    onChange={(e) => setReturnDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Passengers</label>
                  <input
                    type="number"
                    min={1}
                    max={9}
                    value={passengers}
                    onChange={(e) => setPassengers(Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Class</label>
                  <select
                    value={flightClass}
                    onChange={(e) => setFlightClass(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  >
                    <option value="economy">Economy</option>
                    <option value="premium_economy">Premium Economy</option>
                    <option value="business">Business</option>
                    <option value="first">First</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <label className="flex items-center space-x-2 cursor-pointer pb-2">
                    <input
                      type="checkbox"
                      checked={nonStop}
                      onChange={(e) => setNonStop(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Non-stop only</span>
                  </label>
                </div>
              </div>

              <button
                type="submit"
                disabled={flightSearching}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center space-x-2"
              >
                {flightSearching ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <FaSearch />
                    <span>Search Flights</span>
                  </>
                )}
              </button>
            </form>
          </div>
        )}

        {/* Hotels form */}
        {activeTab === 'hotels' && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <form onSubmit={searchHotels} className="space-y-4">
              <div ref={cityRef} className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => {
                    setCity(e.target.value)
                    setCityCode('')
                    debounceSearch(e.target.value, 'city')
                  }}
                  onFocus={() => cityOptions.length > 0 && setShowCityDropdown(true)}
                  placeholder="Search for a city"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                />
                {showCityDropdown && cityOptions.length > 0 && (
                  <ul className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg mt-1 shadow-lg max-h-48 overflow-y-auto">
                    {cityOptions.map((opt) => (
                      <li
                        key={opt.code}
                        onClick={() => {
                          setCity(opt.label)
                          setCityCode(opt.code)
                          setShowCityDropdown(false)
                        }}
                        className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-sm text-gray-900"
                      >
                        {opt.label}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Check-in</label>
                  <input
                    type="date"
                    value={checkIn}
                    onChange={(e) => setCheckIn(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Check-out</label>
                  <input
                    type="date"
                    value={checkOut}
                    onChange={(e) => setCheckOut(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Guests</label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={guests}
                    onChange={(e) => setGuests(Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rooms</label>
                  <input
                    type="number"
                    min={1}
                    max={5}
                    value={rooms}
                    onChange={(e) => setRooms(Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Min Rating</label>
                  <select
                    value={minRating}
                    onChange={(e) => setMinRating(Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  >
                    <option value={0}>Any</option>
                    <option value={3}>3+ Stars</option>
                    <option value={4}>4+ Stars</option>
                    <option value={5}>5 Stars</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Price</label>
                  <input
                    type="number"
                    min={0}
                    value={maxPrice}
                    onChange={(e) => setMaxPrice(Number(e.target.value))}
                    placeholder="No limit"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={hotelSearching}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center space-x-2"
              >
                {hotelSearching ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <FaSearch />
                    <span>Search Hotels</span>
                  </>
                )}
              </button>
            </form>
          </div>
        )}

        {/* Flight results */}
        {activeTab === 'flights' && flightResults.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {flightResults.length} Flight{flightResults.length !== 1 ? 's' : ''} Found
            </h2>
            {flightResults.map((flight) => (
              <div key={flight.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="font-semibold text-gray-900">
                        {flight.outbound_segments?.[0]?.departure_airport}
                      </span>
                      <FaExchangeAlt className="text-gray-400" />
                      <span className="font-semibold text-gray-900">
                        {flight.outbound_segments?.[flight.outbound_segments.length - 1]?.arrival_airport}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center space-x-1">
                        <FaClock />
                        <span>{flight.total_duration}</span>
                      </span>
                      <span>
                        {flight.stops === 0 ? 'Non-stop' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
                      </span>
                      {flight.outbound_segments?.[0]?.airline && (
                        <span>{flight.outbound_segments[0].airline}</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-blue-600">
                      {flight.currency || '$'}{flight.price}
                    </p>
                    <p className="text-sm text-gray-500">per person</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Hotel results */}
        {activeTab === 'hotels' && hotelResults.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {hotelResults.length} Hotel{hotelResults.length !== 1 ? 's' : ''} Found
            </h2>
            {hotelResults.map((hotel) => (
              <div key={hotel.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row md:justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{hotel.name}</h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
                      <FaMapMarkerAlt />
                      <span>{hotel.address}, {hotel.city}</span>
                    </div>
                    {hotel.rating && (
                      <div className="flex items-center space-x-1 mb-2">
                        {Array.from({ length: Math.round(hotel.rating) }).map((_, i) => (
                          <FaStar key={i} className="text-yellow-400 text-sm" />
                        ))}
                        <span className="text-sm text-gray-500 ml-1">{hotel.rating}</span>
                      </div>
                    )}
                    {hotel.amenities?.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {hotel.amenities.slice(0, 5).map((amenity, i) => (
                          <span
                            key={i}
                            className="flex items-center space-x-1 bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full"
                          >
                            {amenityIcon(amenity)}
                            <span>{amenity}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-2xl font-bold text-blue-600">
                      {hotel.currency || '$'}{hotel.price_per_night}
                    </p>
                    <p className="text-sm text-gray-500">per night</p>
                    <p className="text-sm text-gray-400 mt-1">
                      {hotel.currency || '$'}{hotel.total_price} total
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
