'use client'

import { useState } from 'react'
import Link from 'next/link'
import { FaPlane, FaHotel, FaCloud, FaRobot, FaArrowRight } from 'react-icons/fa'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-2">
              <FaPlane className="text-blue-600 text-2xl" />
              <span className="text-xl font-bold text-gray-900">AI Travel Agent</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-gray-700 hover:text-blue-600">
                Login
              </Link>
              <Link
                href="/register"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Your AI-Powered Travel Companion
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Plan your perfect trip with our intelligent travel assistant. Search flights,
            find hotels, check weather, and get personalized recommendations - all in one place.
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              href="/chat"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 flex items-center space-x-2"
            >
              <FaRobot />
              <span>Start Planning</span>
              <FaArrowRight />
            </Link>
            <Link
              href="/search"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold border-2 border-blue-600 hover:bg-blue-50"
            >
              Quick Search
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Everything You Need for Travel Planning
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Feature 1 */}
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <FaRobot className="text-blue-600 text-2xl" />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Chat Assistant</h3>
            <p className="text-gray-600">
              Chat with our AI to plan your trip. Get personalized recommendations based on
              your preferences and budget.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <FaPlane className="text-green-600 text-2xl" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Flight Search</h3>
            <p className="text-gray-600">
              Search and compare flights from hundreds of airlines. Find the best deals for
              your travel dates.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <FaHotel className="text-purple-600 text-2xl" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Hotel Booking</h3>
            <p className="text-gray-600">
              Discover the perfect accommodation. Filter by rating, price, amenities, and
              location.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <FaCloud className="text-orange-600 text-2xl" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Weather Forecast</h3>
            <p className="text-gray-600">
              Check weather conditions for your destination. Plan your activities with
              5-day forecasts.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 text-white py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Your Journey?</h2>
          <p className="text-xl mb-8">
            Create a free account and let our AI assistant help you plan your next adventure.
          </p>
          <Link
            href="/register"
            className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-100 inline-block"
          >
            Get Started for Free
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2024 AI Travel Agent. All rights reserved.</p>
          <p className="text-gray-400 mt-2">Powered by OpenAI, Amadeus, and OpenWeatherMap</p>
        </div>
      </footer>
    </main>
  )
}
