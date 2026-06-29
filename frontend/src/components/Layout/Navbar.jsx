import { useLocation } from 'react-router-dom'
import { Bell, HelpCircle, Moon, Sun } from 'lucide-react'
import { useState } from 'react'

const PAGE_TITLES = {
  '/': { title: 'Mission Control', subtitle: 'Overview of all exoplanet detections' },
  '/datasets': { title: 'Dataset Management', subtitle: 'Search, download and upload TESS observations' },
  '/preprocessing': { title: 'Preprocessing Studio', subtitle: 'Clean and detrend light curves' },
  '/detection': { title: 'Transit Detection', subtitle: 'TLS & BLS periodic signal search' },
  '/validation': { title: 'Candidate Validation', subtitle: 'ML + statistical false-positive analysis' },
  '/characterization': { title: 'Planet Characterization', subtitle: 'Estimate orbital and physical parameters' },
  '/visualization': { title: 'Visualization Dashboard', subtitle: 'Interactive scientific plots' },
  '/reports': { title: 'Report Generator', subtitle: 'Export PDF & CSV scientific reports' },
}

export default function Navbar() {
  const { pathname } = useLocation()
  const key = Object.keys(PAGE_TITLES).find((k) => (k === '/' ? pathname === '/' : pathname.startsWith(k))) || '/'
  const { title, subtitle } = PAGE_TITLES[key]
  const [dark, setDark] = useState(false)

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-gray-100 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Page title */}
        <div>
          <h1 className="text-lg font-bold text-navy-900">{title}</h1>
          <p className="text-xs text-gray-400">{subtitle}</p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost text-xs px-3 py-1.5"
          >
            <HelpCircle size={14} />
            API Docs
          </a>

          {/* TESS badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-navy-50 border border-navy-100">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-medium text-navy-700">TESS MAST Live</span>
          </div>
        </div>
      </div>
    </header>
  )
}
