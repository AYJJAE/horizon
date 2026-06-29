import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';

import FloatingNav from './components/Layout/FloatingNav';
import SpaceBackground from './components/Layout/SpaceBackground';
import CustomCursor from './components/Layout/CustomCursor';

import Dashboard from './pages/Dashboard';
import Datasets from './pages/Datasets';
import Preprocessing from './pages/Preprocessing';
import Detection from './pages/Detection';
import Validation from './pages/Validation';
import Characterization from './pages/Characterization';
import Visualization from './pages/Visualization';
import Reports from './pages/Reports';

// Wrapper component to handle routing animations
function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<PageWrapper><Dashboard /></PageWrapper>} />
        <Route path="/datasets" element={<PageWrapper><Datasets /></PageWrapper>} />
        <Route path="/preprocessing" element={<PageWrapper><Preprocessing /></PageWrapper>} />
        <Route path="/detection" element={<PageWrapper><Detection /></PageWrapper>} />
        <Route path="/validation" element={<PageWrapper><Validation /></PageWrapper>} />
        <Route path="/characterization" element={<PageWrapper><Characterization /></PageWrapper>} />
        <Route path="/visualization" element={<PageWrapper><Visualization /></PageWrapper>} />
        <Route path="/reports" element={<PageWrapper><Reports /></PageWrapper>} />
      </Routes>
    </AnimatePresence>
  );
}

function PageWrapper({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 1.02 }}
      transition={{ type: "spring", stiffness: 260, damping: 20 }}
      className="w-full h-full pb-20"
    >
      {children}
    </motion.div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      {/* 3D Space Background */}
      <SpaceBackground />
      
      {/* Custom Glowing Cursor */}
      <CustomCursor />
      
      <div className="flex flex-col min-h-screen relative z-10">
        <FloatingNav />
        <main className="flex-1 w-full max-w-7xl mx-auto pt-28 px-4 sm:px-6 lg:px-8">
          <AnimatedRoutes />
        </main>
      </div>
    </BrowserRouter>
  );
}
