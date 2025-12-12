// User types
export interface User {
  id: number
  email: string
  full_name: string
  phone?: string
  role: 'user' | 'admin'
  is_active: boolean
  preferences?: TravelPreferences
  created_at: string
  updated_at: string
}

export interface TravelPreferences {
  preferred_class?: string
  preferred_airlines?: string[]
  preferred_hotel_rating?: number
  budget_range?: { min: number; max: number }
  dietary_restrictions?: string[]
  accessibility_needs?: string[]
  preferred_locations?: string[]
  travel_purpose?: string
}

// Chat types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
}

export interface ChatResponse {
  conversation_id: string
  message: string
  suggestions?: string[]
  action_required?: string
  action_params?: any
}

// Flight types
export interface FlightSearchParams {
  origin: string
  destination: string
  departure_date: string
  return_date?: string
  passengers?: number
  flight_class?: 'economy' | 'premium_economy' | 'business' | 'first'
  non_stop?: boolean
  max_results?: number
}

export interface FlightSegment {
  departure_airport: string
  arrival_airport: string
  departure_time: string
  arrival_time: string
  airline: string
  flight_number: string
  duration: string
  aircraft?: string
}

export interface FlightOffer {
  id: string
  price: number
  currency: string
  outbound_segments: FlightSegment[]
  return_segments?: FlightSegment[]
  total_duration: string
  stops: number
  booking_url?: string
}

export interface FlightSearchResponse {
  results: FlightOffer[]
  search_id: string
  total_results: number
}

// Hotel types
export interface HotelSearchParams {
  city_code: string
  check_in: string
  check_out: string
  guests?: number
  rooms?: number
  min_rating?: number
  max_price?: number
  amenities?: string[]
  max_results?: number
}

export interface HotelOffer {
  id: string
  name: string
  rating?: number
  price_per_night: number
  total_price: number
  currency: string
  address: string
  city: string
  country: string
  coordinates?: { latitude: number; longitude: number }
  amenities: string[]
  description?: string
  images?: string[]
  booking_url?: string
  distance_from_center?: number
}

export interface HotelSearchResponse {
  results: HotelOffer[]
  search_id: string
  total_results: number
}

// Weather types
export interface CurrentWeather {
  temperature: number
  feels_like: number
  humidity: number
  pressure: number
  condition: string
  description: string
  wind_speed: number
  clouds: number
  visibility?: number
}

export interface WeatherForecast {
  date: string
  temperature_min: number
  temperature_max: number
  condition: string
  description: string
  humidity: number
  wind_speed: number
  precipitation_probability?: number
}

export interface WeatherResponse {
  location: string
  coordinates: { latitude: number; longitude: number }
  current: CurrentWeather
  forecast: WeatherForecast[]
  timezone: string
}

// API Response types
export interface APIResponse<T = any> {
  success: boolean
  message: string
  data?: T
}
