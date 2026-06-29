import { useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { datasetsApi } from '../api/client'
import { useAppStore } from '../store/appStore'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Canvas, useFrame } from '@react-three/fiber'
import { Sphere, MeshDistortMaterial } from '@react-three/drei'
import {
  Database, Radio, ShieldCheck, Orbit,
  TrendingUp, ArrowRight, Satellite, Star, Activity
} from 'lucide-react'
import logo from '../logo.png'
import clsx from 'clsx'

const AnimatedPlanet = () => {
  const sphereRef = useRef();
  
  useFrame((state, delta) => {
    if (sphereRef.current) {
      sphereRef.current.rotation.y += delta * 0.2;
      sphereRef.current.rotation.x += delta * 0.05;
    }
  });

  return (
    <Sphere ref={sphereRef} args={[1, 64, 64]} scale={1.5}>
      <MeshDistortMaterial
        color="#06B6D4"
        attach="material"
        distort={0.4}
        speed={1.5}
        roughness={0.2}
        metalness={0.8}
        emissive="#000000"
        wireframe={true}
      />
    </Sphere>
  );
};

const StatCard = ({ icon: Icon, label, value, color, sub, delay = 0 }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5 }}
    className="stat-card group hover:-translate-y-2 transition-transform duration-500"
  >
    <div className="flex items-start justify-between mb-4">
      <div className={clsx('w-12 h-12 rounded-xl flex items-center justify-center bg-white/5 border', color)}>
        <Icon size={24} className="text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]" />
      </div>
      <TrendingUp size={16} className="text-white/30" />
    </div>
    <div className="stat-value">{value}</div>
    <div className="stat-label mt-2">{label}</div>
    {sub && <div className="text-xs text-gray-500 mt-1 font-sans">{sub}</div>}
  </motion.div>
)

const PipelineStep = ({ step, title, desc, to, done, active, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay, duration: 0.5 }}
  >
    <Link to={to} className="group flex items-center gap-5 p-4 rounded-xl border border-white/5 bg-white/5 hover:border-cosmic-cyan/50 hover:bg-cosmic-cyan/10 transition-all duration-300">
      <div className={clsx(
        'step-dot',
        done ? 'step-dot-done' : active ? 'step-dot-active' : 'step-dot-pending'
      )}>
        {done ? '✓' : step}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-display font-semibold text-white text-sm tracking-wide group-hover:text-cosmic-cyan transition-colors">{title}</div>
        <div className="text-xs text-gray-400 font-sans truncate mt-0.5">{desc}</div>
      </div>
      <ArrowRight size={16} className="text-white/20 group-hover:text-cosmic-cyan transition-colors" />
    </Link>
  </motion.div>
)

export default function Dashboard() {
  const { activeDataset } = useAppStore()
  const { data: datasets } = useQuery({ queryKey: ['datasets'], queryFn: () => datasetsApi.list().then(r => r.data) })

  const totalDatasets = datasets?.length || 0

  return (
    <div className="space-y-8 pb-10">

      {/* Hero Banner */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="rounded-3xl overflow-hidden relative min-h-[400px] flex items-center border border-white/10 shadow-glow-blue"
        style={{ background: 'linear-gradient(135deg, rgba(10,22,40,0.9) 0%, rgba(6,14,28,0.95) 100%)' }}
      >
        {/* 3D Planet Background */}
        <div className="absolute right-0 top-0 bottom-0 w-1/2 opacity-60 pointer-events-none">
          <Canvas camera={{ position: [0, 0, 4] }}>
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1.5} />
            <AnimatedPlanet />
          </Canvas>
        </div>

        <div className="relative p-10 lg:p-16 flex-1 z-10 flex flex-col md:flex-row items-start md:items-center gap-8">
          <div className="flex-shrink-0 w-24 h-24 rounded-2xl overflow-hidden border border-white/10 shadow-glow-cyan bg-black/40 p-1 backdrop-blur-sm">
            <img src={logo} alt="Horizon Labs" className="w-full h-full object-contain rounded-xl p-1" />
          </div>
          <div className="flex-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cosmic-cyan/10 border border-cosmic-cyan/30 text-cosmic-cyan text-xs font-display font-bold uppercase tracking-widest mb-4">
              <span className="w-2 h-2 rounded-full bg-cosmic-cyan animate-pulse"></span>
              System Online
            </div>
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-white mb-4 tracking-wider leading-tight">
              Horizon Labs <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-cosmic-cyan to-cosmic-purple">Exoplanet Platform</span>
            </h2>
            <p className="text-gray-400 font-sans text-sm lg:text-base mt-2 max-w-xl leading-relaxed">
              Automated TESS light curve analysis using TLS/BLS transit detection and AI-powered candidate validation. Explore the universe with unprecedented precision.
            </p>
            <div className="flex gap-4 mt-8">
              <Link to="/datasets" className="btn-primary">
                <Satellite size={16} />
                Acquire Data
              </Link>
              <Link to="/visualization" className="btn-outline">
                <Activity size={16} />
                Open Observatory
              </Link>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={Database} label="Datasets Loaded" value={totalDatasets} color="border-cosmic-cyan/30 text-cosmic-cyan" sub="TESS + custom uploads" delay={0.1} />
        <StatCard icon={Radio} label="Transit Candidates" value="—" color="border-cosmic-purple/30 text-cosmic-purple" sub="Run detection" delay={0.2} />
        <StatCard icon={ShieldCheck} label="Validated Signals" value="—" color="border-cosmic-green/30 text-cosmic-green" sub="ML + statistical checks" delay={0.3} />
        <StatCard icon={Orbit} label="Confirmed Planets" value="—" color="border-cosmic-gold/30 text-cosmic-gold" sub="Composite score ≥ 0.5" delay={0.4} />
      </div>

      {/* Pipeline + Active Target */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Pipeline Steps */}
        <div className="card">
          <h3 className="section-title flex items-center gap-3"><Star size={20} className="text-cosmic-gold" />Analysis Protocol</h3>
          <p className="section-subtitle">Complete end-to-end exoplanet detection workflow sequence</p>
          <div className="space-y-3 relative">
            {/* Connecting line */}
            <div className="absolute left-[26px] top-4 bottom-4 w-px bg-white/10 z-0"></div>
            
            <PipelineStep step="1" title="Data Acquisition" desc="Search TESS targets or upload custom FITS/CSV" to="/datasets" done={totalDatasets > 0} active={totalDatasets === 0} delay={0.1} />
            <PipelineStep step="2" title="Signal Cleaning" desc="Remove outliers, detrend, normalize" to="/preprocessing" active={totalDatasets > 0} delay={0.2} />
            <PipelineStep step="3" title="Transit Detection" desc="TLS + BLS periodic signal search" to="/detection" delay={0.3} />
            <PipelineStep step="4" title="Candidate Validation" desc="CNN + statistical false-positive analysis" to="/validation" delay={0.4} />
            <PipelineStep step="5" title="Characterization" desc="Calculate radius, semi-major axis, temperature" to="/characterization" delay={0.5} />
            <PipelineStep step="6" title="Final Reports" desc="Export PDF + CSV scientific data" to="/reports" delay={0.6} />
          </div>
        </div>

        {/* Active Dataset Card */}
        <div className="card flex flex-col">
          <h3 className="section-title flex items-center gap-3"><Satellite size={20} className="text-cosmic-cyan" />Current Target</h3>
          <p className="section-subtitle">The astronomical object currently loaded in memory</p>
          
          {activeDataset ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex-1 flex flex-col justify-between space-y-6"
            >
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 shadow-[inset_0_0_20px_rgba(255,255,255,0.02)] relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-cosmic-cyan/10 blur-3xl rounded-full pointer-events-none"></div>
                <div className="font-display font-bold text-xl text-white tracking-wide">{activeDataset.name}</div>
                {activeDataset.tic_id && <div className="text-sm text-cosmic-cyan font-mono mt-1">TIC {activeDataset.tic_id}</div>}
                
                <div className="grid grid-cols-2 gap-4 mt-6 text-sm">
                  {[
                    ['Source', activeDataset.source?.toUpperCase()],
                    ['Sector', activeDataset.sector || '—'],
                    ['Data Points', activeDataset.num_points?.toLocaleString() || '—'],
                    ['Time Span', activeDataset.time_start ? `${((activeDataset.time_end - activeDataset.time_start)).toFixed(1)} d` : '—'],
                  ].map(([k, v]) => (
                    <div key={k} className="flex flex-col gap-1 border-l-2 border-white/10 pl-3">
                      <span className="text-gray-500 font-sans text-xs uppercase tracking-widest">{k}</span>
                      <span className="font-display font-medium text-gray-200">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex gap-4">
                <Link to="/preprocessing" className="btn-primary flex-1">Initialize Preprocessing</Link>
                <Link to="/detection" className="btn-outline flex-1">Scan for Transits</Link>
              </div>
            </motion.div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center py-16 text-center border-2 border-dashed border-white/10 rounded-2xl mt-2 bg-white/5">
              <div className="w-16 h-16 rounded-xl overflow-hidden border border-white/10 shadow-glow-cyan mb-4 relative opacity-60">
                <img src={logo} alt="Horizon Labs" className="w-full h-full object-cover" />
              </div>
              <p className="text-gray-400 font-sans mb-6 max-w-[200px]">No active target selected in the mainframe.</p>
              <Link to="/datasets" className="btn-accent">
                <Database size={16} />
                Access Archive
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Recent Datasets */}
      {datasets && datasets.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="section-title mb-0">Recent Archives</h3>
            <Link to="/datasets" className="text-xs font-display text-cosmic-cyan hover:text-white uppercase tracking-widest flex items-center gap-2 transition-colors">
              View Database <ArrowRight size={14} />
            </Link>
          </div>
          <div className="overflow-x-auto rounded-xl border border-white/5">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Target Name</th><th>Identifier</th><th>Source Array</th><th>Data Points</th><th>Acquired On</th>
                </tr>
              </thead>
              <tbody>
                {datasets.slice(0, 5).map(d => (
                  <tr key={d.id} className="cursor-pointer group">
                    <td className="font-display font-medium text-white group-hover:text-cosmic-cyan transition-colors">{d.name}</td>
                    <td className="font-mono text-gray-400">{d.tic_id || '—'}</td>
                    <td><span className={clsx('badge', d.source === 'mast' ? 'badge-tls' : 'badge-bls')}>{d.source}</span></td>
                    <td className="font-mono text-gray-400">{d.num_points?.toLocaleString() || '—'}</td>
                    <td className="text-gray-500 font-sans">{new Date(d.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  )
}
