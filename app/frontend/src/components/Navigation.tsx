import React from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut, Menu, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navigation() {
  const [isOpen, setIsOpen] = React.useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 text-primary"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar Navigation */}
      <nav
        className={`${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 fixed md:static w-48 h-screen bg-white border-r border-cream-200 transition-transform duration-300 z-40 flex flex-col p-6`}
      >
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-2xl font-serif font-bold text-primary">WW</h1>
          <p className="text-xs text-secondary">Wellbeing</p>
        </div>

        {/* User Info */}
        {user && (
          <div className="pb-6 border-b border-cream-200 mb-6">
            <p className="text-sm font-medium text-primary">{user.name}</p>
            <p className="text-xs text-secondary capitalize mt-1">{user.role}</p>
          </div>
        )}

        {/* Navigation */}
        <div className="flex-1">
          <p className="text-xs text-secondary uppercase tracking-wide mb-3 font-medium">Menu</p>
          <a
            href="/"
            onClick={() => setIsOpen(false)}
            className="block px-3 py-2 text-sm text-primary hover:bg-cream-100 rounded transition"
          >
            Dashboard
          </a>
        </div>

        {/* Logout Button */}
        <div className="border-t border-cream-200 pt-4">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 text-sm text-primary hover:bg-cream-100 rounded transition"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </nav>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black bg-opacity-20 z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  )
}
