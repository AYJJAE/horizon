import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useAppStore } from '../../store/appStore'
import {
  LayoutDashboard, Database, Sliders, Radio, ShieldCheck,
  Orbit, BarChart3, FileDown, ChevronLeft, ChevronRight,
  Telescope, Satellite
} from 'lucide-react'
import clsx from 'clsx'

const navLinks = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/datasets', icon: Database, label: 'Datasets' },
  { to: '/preprocessing', icon: Sliders, label: 'Preprocessing' },
  { to: '/detection', icon: Radio, label: 'Transit Detection' },
  { to: '/validation', icon: ShieldCheck, label: 'Validation' },
  { to: '/characterization', icon: Orbit, label: 'Characterization' },
  { to: '/visualization', icon: BarChart3, label: 'Visualization' },
  { to: '/reports', icon: FileDown, label: 'Reports' },
]

export default function Sidebar() {
  const { sidebarCollapsed, toggleSidebar, activeDataset } = useAppStore()
  const location = useLocation()

  return (
    <aside
      className={clsx(
        'flex flex-col h-screen sticky top-0 transition-all duration-300 ease-out z-40',
        'bg-hero-gradient select-none',
        sidebarCollapsed ? 'w-16' : 'w-60'
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/10">
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center shadow-glow-orange">
          <Telescope size={16} className="text-white" />
        </div>
        {!sidebarCollapsed && (
          <div className="animate-fade-in">
            <div className="text-white font-bold text-sm leading-tight">HORIZON</div>
            <div className="text-navy-300 text-xs">Exoplanet Platform</div>
          </div>
        )}
      </div>

      {/* Active dataset indicator */}
      {!sidebarCollapsed && activeDataset && (
        <div className="mx-3 mt-3 px-3 py-2 rounded-lg bg-white/10 border border-white/15 animate-fade-in">
          <div className="flex items-center gap-2">
            <Satellite size={12} className="text-orange-400 flex-shrink-0" />
            <span className="text-white/90 text-xs font-medium truncate">{activeDataset.name}</span>
          </div>
          {activeDataset.tic_id && (
            <div className="text-navy-300 text-xs mt-0.5 pl-5">TIC {activeDataset.tic_id}</div>
          )}
        </div>
      )}

      {/* Nav Links */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto no-scrollbar">
        {navLinks.map(({ to, icon: Icon, label }) => {
          const isActive = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
          return (
            <NavLink
              key={to}
              to={to}
              title={sidebarCollapsed ? label : undefined}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-white text-navy-900 shadow-sm'
                  : 'text-navy-200 hover:bg-white/10 hover:text-white'
              )}
            >
              <Icon size={17} className={clsx('flex-shrink-0', isActive ? 'text-navy-900' : '')} />
              {!sidebarCollapsed && <span className="truncate">{label}</span>}
              {!sidebarCollapsed && isActive && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-orange-500" />
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="flex items-center justify-center h-10 mx-3 mb-4 rounded-xl bg-white/10 hover:bg-white/20
                   text-navy-200 hover:text-white transition-all duration-200"
        title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {sidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        {!sidebarCollapsed && <span className="text-xs ml-1">Collapse</span>}
      </button>
    </aside>
  )
}
