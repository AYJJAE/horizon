import { useState, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { characterizationApi } from '../api/client'
import { useAppStore } from '../store/appStore'
import toast from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import { Canvas, useFrame } from '@react-three/fiber'
import { Sphere, MeshDistortMaterial } from '@react-three/drei'
import { Orbit, Play, Loader2, AlertCircle, Thermometer, Globe, Ruler, Scale } from 'lucide-react'
import clsx from 'clsx'

const HZ_COLORS = {
  frozen: { bg: 'bg-blue-500/20 border-blue-500/30', text: 'text-blue-400', label: 'FROZEN ZONE', hex: '#60A5FA' },
  cold_edge: { bg: 'bg-cyan-500/20 border-cyan-500/30', text: 'text-cyan-400', label: 'COLD EDGE OF HZ', hex: '#22D3EE' },
  habitable_zone: { bg: 'bg-cosmic-green/20 border-cosmic-green/30 shadow-glow-green', text: 'text-cosmic-green', label: 'HABITABLE ZONE (GOLDILOCKS)', hex: '#10B981' },
  warm_edge: { bg: 'bg-amber-500/20 border-amber-500/30', text: 'text-amber-400', label: 'WARM EDGE OF HZ', hex: '#FBBF24' },
  hot_zone: { bg: 'bg-cosmic-red/20 border-cosmic-red/30 shadow-glow-red', text: 'text-cosmic-red', label: 'HOT ZONE (TIDALLY LOCKED)', hex: '#EF4444' },
}

const PlanetVisualizer = ({ colorHex }) => {
  const sphereRef = useRef();
  
  useFrame((state, delta) => {
    if (sphereRef.current) {
      sphereRef.current.rotation.y += delta * 0.1;
      sphereRef.current.rotation.x += delta * 0.05;
    }
  });

  return (
    <Canvas camera={{ position: [0, 0, 4] }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1.5} />
      <Sphere ref={sphereRef} args={[1, 64, 64]} scale={1.8}>
        <MeshDistortMaterial
          color={colorHex || "#6B7280"}
          attach="material"
          distort={0.2}
          speed={1.5}
          roughness={0.5}
          metalness={0.3}
          wireframe={true}
        />
      </Sphere>
    </Canvas>
  );
};

const ParamCard = ({ icon: Icon, label, value, unit, colorClass, delay = 0 }) => (
  <motion.div 
    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
    className="card flex flex-col gap-3 group border border-white/5 bg-white/5 hover:border-white/20 transition-all overflow-hidden relative"
  >
    <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
    <div className={clsx('w-10 h-10 rounded-xl flex items-center justify-center border border-white/10 bg-white/5 relative z-10', colorClass)}>
      <Icon size={20} className="drop-shadow-glow" />
    </div>
    <div className="relative z-10">
      <div className="flex items-baseline gap-1">
        <div className="text-3xl font-display font-bold text-white">{value ?? '—'}</div>
        {unit && <div className="text-xs text-gray-500 font-sans tracking-widest uppercase">{unit}</div>}
      </div>
      <div className="text-[10px] text-gray-400 font-sans tracking-widest uppercase mt-1">{label}</div>
    </div>
  </motion.div>
)

export default function Characterization() {
  const { activeCandidateId, detectionResult, characterizationResults, setCharacterizationResult } = useAppStore()
  const [selectedId, setSelectedId] = useState(activeCandidateId)

  const mutation = useMutation({
    mutationFn: (cid) => characterizationApi.run(cid),
    onSuccess: (res, cid) => { setCharacterizationResult(cid, res.data); toast.success('Astrophysical characterization complete.') },
    onError: () => toast.error('Characterization sequence failed'),
  })

  const candidates = detectionResult?.candidates || []
  const activeId = selectedId || candidates[0]?.id
  const charResult = characterizationResults[activeId]
  const cand = candidates.find(c => c.id === activeId)

  if (!candidates.length) return (
    <div className="card flex flex-col items-center py-24 text-center animate-fade-in border-dashed border-2">
      <AlertCircle size={48} className="text-cosmic-gold mb-4 drop-shadow-glow-cyan" />
      <h2 className="text-xl font-display font-bold text-white tracking-widest uppercase">No Targets Available</h2>
      <p className="text-sm text-gray-400 mt-2 max-w-sm">Transit candidates must be detected before astrophysical properties can be estimated.</p>
    </div>
  )

  const hz = charResult?.details?.habitable_zone
  const hzCfg = hz ? HZ_COLORS[hz] : null

  return (
    <div className="space-y-8 pb-10">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Candidate selector */}
        <div className="card lg:col-span-4 flex flex-col h-full">
          <h3 className="section-title flex items-center gap-3"><Globe size={20} className="text-cosmic-cyan" />Target Selection</h3>
          <p className="section-subtitle text-xs mb-6">Select an anomaly to estimate physical and orbital properties</p>
          
          <div className="space-y-3 flex-1 overflow-y-auto pr-2 no-scrollbar">
            {candidates.map((c, i) => (
              <motion.div 
                initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                key={c.id} onClick={() => setSelectedId(c.id)}
                className={clsx(
                  'flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all relative overflow-hidden group',
                  activeId === c.id ? 'border-cosmic-cyan/50 bg-cosmic-cyan/10 shadow-glow-cyan' : 'border-white/10 bg-white/5 hover:border-cosmic-cyan/30 hover:bg-white/10'
                )}>
                
                {activeId === c.id && <div className="absolute inset-0 bg-gradient-to-r from-cosmic-cyan/5 to-transparent pointer-events-none"></div>}
                
                <div className={clsx("w-8 h-8 rounded-lg flex items-center justify-center font-display font-bold transition-colors z-10", activeId === c.id ? "bg-cosmic-cyan/20 text-cosmic-cyan border border-cosmic-cyan/30" : "bg-white/5 text-gray-400 border border-white/10")}>
                  {i + 1}
                </div>
                
                <div className="flex-1 text-xs relative z-10">
                  <div className="font-display font-semibold text-white tracking-wide">{c.method} Anomaly</div>
                  <div className="text-gray-400 font-mono mt-0.5 tracking-wider text-[10px]">P: {c.period?.toFixed(3)} d</div>
                </div>
              </motion.div>
            ))}
          </div>
          
          <button onClick={() => mutation.mutate(activeId)} disabled={mutation.isPending || !activeId} className="btn-primary w-full justify-center h-14 text-base mt-6">
            {mutation.isPending ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
            {mutation.isPending ? 'ESTIMATING...' : 'ESTIMATE PROPERTIES'}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-8 space-y-6">
          <AnimatePresence mode="wait">
            {mutation.isPending && (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="card flex flex-col items-center py-32 border border-cosmic-cyan/30 bg-cosmic-cyan/5 relative overflow-hidden h-full"
              >
                <div className="absolute inset-0 bg-cosmic-cyan/10 animate-pulse pointer-events-none"></div>
                <Loader2 size={56} className="text-cosmic-cyan animate-spin mb-6 drop-shadow-glow-cyan relative z-10" />
                <p className="text-lg font-display uppercase tracking-widest text-cosmic-cyan font-bold relative z-10">Calculating Parameters...</p>
                <p className="text-xs text-cosmic-cyan/60 mt-2 font-mono uppercase tracking-widest relative z-10">Applying Kepler's Third Law & Transit Geometry</p>
              </motion.div>
            )}

            {!charResult && !mutation.isPending && (
              <motion.div 
                key="empty"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="card flex flex-col items-center justify-center h-full py-32 text-center border-dashed border-2 border-white/5 bg-white/5"
              >
                <Globe size={48} className="text-white/10 mb-4" />
                <p className="text-sm font-sans tracking-wide text-gray-400 max-w-sm">Select an anomaly and initiate sequence to estimate planetary characteristics.</p>
              </motion.div>
            )}

            {charResult && !mutation.isPending && (
              <motion.div 
                key="results"
                initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                className="space-y-6"
              >
                {/* Classification + HZ Banner */}
                <div className="card relative overflow-hidden flex flex-col sm:flex-row items-center justify-between border border-white/10 bg-gradient-to-r from-space-900 to-space-800 p-8 min-h-[200px]">
                  {/* 3D Planet Render */}
                  <div className="absolute right-0 top-0 bottom-0 w-64 opacity-80 pointer-events-none">
                    <PlanetVisualizer colorHex={hzCfg?.hex} />
                  </div>
                  
                  <div className="relative z-10 w-full">
                    <div className="text-[10px] text-gray-400 font-sans tracking-widest uppercase mb-2">Estimated Classification</div>
                    <div className="text-4xl sm:text-5xl font-display font-bold text-white tracking-widest uppercase drop-shadow-[0_0_20px_rgba(255,255,255,0.3)]">
                      {charResult.classification || 'Unknown'}
                    </div>
                    {hzCfg && (
                      <div className={clsx('mt-4 inline-flex items-center px-4 py-1.5 rounded-full border font-sans text-xs uppercase tracking-widest font-bold', hzCfg.bg, hzCfg.text)}>
                        {hzCfg.label}
                      </div>
                    )}
                  </div>
                </div>

                {/* Planet params */}
                <div>
                  <h3 className="section-title text-base flex items-center gap-2 mb-4"><Orbit size={16} className="text-cosmic-cyan" />Planetary Geometry</h3>
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <ParamCard icon={Ruler} label="Radius (Earth)" value={charResult.planet_radius_rearth?.toFixed(2)} unit="R⊕" colorClass="text-cosmic-cyan" delay={0.1} />
                    <ParamCard icon={Ruler} label="Radius (Jupiter)" value={charResult.planet_radius_rjup?.toFixed(3)} unit="RJ" colorClass="text-cosmic-purple" delay={0.15} />
                    <ParamCard icon={Globe} label="Semi-Major Axis" value={charResult.semi_major_axis_au?.toFixed(4)} unit="AU" colorClass="text-cosmic-green" delay={0.2} />
                    <ParamCard icon={Thermometer} label="Surface Temp" value={charResult.equilibrium_temp_k?.toFixed(0)} unit="K" colorClass="text-cosmic-gold" delay={0.25} />
                  </div>
                </div>

                {/* Stellar params */}
                <div>
                  <h3 className="section-title text-base flex items-center gap-2 mb-4 mt-6"><Globe size={16} className="text-cosmic-gold" />Host Star Properties</h3>
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                    <ParamCard icon={Scale} label="Stellar Radius" value={charResult.stellar_radius_rsun?.toFixed(3)} unit="R☉" colorClass="text-yellow-400" delay={0.3} />
                    <ParamCard icon={Scale} label="Stellar Mass" value={charResult.stellar_mass_msun?.toFixed(3)} unit="M☉" colorClass="text-orange-400" delay={0.35} />
                    <ParamCard icon={Thermometer} label="Effective Temp" value={charResult.stellar_teff_k?.toFixed(0)} unit="K" colorClass="text-cosmic-red" delay={0.4} />
                  </div>
                </div>

                {/* Transit params */}
                {cand && (
                  <div>
                    <h3 className="section-title text-base flex items-center gap-2 mb-4 mt-6"><Activity size={16} className="text-gray-400" />Observed Metrics</h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                      <ParamCard icon={Orbit} label="Orbital Period" value={cand.period?.toFixed(6)} unit="d" colorClass="text-white" delay={0.45} />
                      <ParamCard icon={Orbit} label="Transit Depth" value={((cand.depth || 0) * 1e6).toFixed(1)} unit="ppm" colorClass="text-white" delay={0.5} />
                      <ParamCard icon={Orbit} label="Transit Duration" value={(cand.duration * 24 || 0).toFixed(2)} unit="hr" colorClass="text-white" delay={0.55} />
                      <ParamCard icon={Orbit} label="Observed Transits" value={cand.num_transits} unit="" colorClass="text-white" delay={0.6} />
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
