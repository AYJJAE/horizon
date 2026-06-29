import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useWindowScroll } from 'react-use';
import { useAppStore } from '../../store/appStore';
import {
  LayoutDashboard, Database, Sliders, Radio, ShieldCheck,
  Orbit, BarChart3, FileDown, Telescope, Satellite, Menu, X
} from 'lucide-react';
import logo from '../../logo.png';
import clsx from 'clsx';

const navLinks = [
  { to: '/', icon: LayoutDashboard, label: 'Mission Control' },
  { to: '/datasets', icon: Database, label: 'Archive' },
  { to: '/preprocessing', icon: Sliders, label: 'Signal Noise' },
  { to: '/detection', icon: Radio, label: 'Transit Scan' },
  { to: '/validation', icon: ShieldCheck, label: 'Validation' },
  { to: '/characterization', icon: Orbit, label: 'Characterization' },
  { to: '/visualization', icon: BarChart3, label: 'Observatory' },
  { to: '/reports', icon: FileDown, label: 'Comms' },
];

export default function FloatingNav() {
  const { y } = useWindowScroll();
  const [hidden, setHidden] = useState(false);
  const [lastY, setLastY] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { activeDataset } = useAppStore();

  useEffect(() => {
    if (y > lastY && y > 100) {
      setHidden(true);
    } else {
      setHidden(false);
    }
    setLastY(y);
  }, [y, lastY]);

  const navVariants = {
    visible: { y: 0, opacity: 1, transition: { type: 'spring', stiffness: 300, damping: 30 } },
    hidden: { y: '-150%', opacity: 0, transition: { type: 'spring', stiffness: 300, damping: 30 } }
  };

  return (
    <>
      <motion.nav
        variants={navVariants}
        initial="visible"
        animate={hidden ? "hidden" : "visible"}
        className="fixed top-4 left-0 right-0 mx-auto w-[96%] max-w-[1440px] z-50 rounded-2xl bg-space-800/60 backdrop-blur-xl border border-white/10 shadow-card flex items-center justify-between px-8 py-4 select-none"
      >
        {/* Brand */}
        <div className="flex items-center gap-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-xl overflow-hidden shadow-glow-cyan border border-white/10 relative">
            <img src={logo} alt="Horizon Labs" className="w-full h-full object-contain p-1" />
          </div>
          <div className="hidden md:block">
            <div className="text-white font-display font-bold text-xl leading-tight tracking-widest uppercase">Horizon Labs</div>
            <div className="text-cosmic-cyan/80 font-sans text-xs tracking-widest uppercase">Deep Space Terminal</div>
          </div>
        </div>

        {/* Desktop Links */}
        <div className="hidden xl:flex items-center gap-2">
          {navLinks.map(({ to, icon: Icon, label }) => {
            const isActive = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to);
            return (
              <NavLink
                key={to}
                to={to}
                className={clsx(
                  'relative px-4 py-3 rounded-xl text-xs font-display uppercase tracking-wider transition-all duration-300 overflow-hidden group flex items-center gap-2.5 whitespace-nowrap',
                  isActive ? 'text-white font-bold' : 'text-gray-400 hover:text-white'
                )}
              >
                <Icon size={16} className={isActive ? 'text-cosmic-cyan' : 'group-hover:text-cosmic-cyan transition-colors'} />
                <span>{label}</span>
                {isActive && (
                  <motion.div
                    layoutId="nav-pill"
                    className="absolute inset-0 bg-white/10 rounded-xl border border-white/20 -z-10"
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  />
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Active Dataset & Mobile Toggle */}
        <div className="flex items-center gap-4">
          {activeDataset && (
            <div className="hidden md:flex items-center gap-3 px-4 py-2 rounded-xl bg-cosmic-cyan/10 border border-cosmic-cyan/20">
              <Satellite size={16} className="text-cosmic-cyan animate-pulse-slow" />
              <div className="text-right">
                <div className="text-white/90 text-sm font-semibold font-display uppercase truncate max-w-[140px]">{activeDataset.name}</div>
              </div>
            </div>
          )}
          
          <button 
            className="xl:hidden text-white p-3 bg-white/5 rounded-xl border border-white/10"
            onClick={() => setMobileMenuOpen(true)}
          >
            <Menu size={20} />
          </button>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
            animate={{ opacity: 1, backdropFilter: "blur(16px)" }}
            exit={{ opacity: 0, backdropFilter: "blur(0px)" }}
            className="fixed inset-0 z-[60] bg-space-900/80 flex flex-col items-center justify-center"
          >
            <button 
              className="absolute top-6 right-6 text-white p-3 bg-white/10 rounded-full"
              onClick={() => setMobileMenuOpen(false)}
            >
              <X size={24} />
            </button>
            <div className="flex flex-col items-center gap-6">
              {navLinks.map(({ to, icon: Icon, label }) => {
                const isActive = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to);
                return (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileMenuOpen(false)}
                    className={clsx(
                      'flex items-center gap-4 text-xl font-display uppercase tracking-widest',
                      isActive ? 'text-cosmic-cyan' : 'text-gray-400'
                    )}
                  >
                    <Icon size={24} />
                    {label}
                  </NavLink>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
