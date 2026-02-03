'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FaPlane, FaSignOutAlt } from 'react-icons/fa'
import { useAuthStore } from '@/store/auth'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="flex items-center space-x-2">
            <FaPlane className="text-blue-600 text-2xl" />
            <span className="text-xl font-bold text-gray-900">AI Travel Agent</span>
          </Link>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link href="/chat" className="text-gray-700 hover:text-blue-600">
                  Chat
                </Link>
                <Link href="/search" className="text-gray-700 hover:text-blue-600">
                  Search
                </Link>
                <span className="text-gray-500 text-sm hidden sm:inline">
                  {user.full_name}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-red-600 flex items-center space-x-1"
                >
                  <FaSignOutAlt />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-gray-700 hover:text-blue-600">
                  Login
                </Link>
                <Link
                  href="/register"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
