import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { detectionApi } from '../api/client'
import { useAppStore } from '../store/appStore'
import PlotlyChart from '../components/charts/PlotlyChart'
import toast from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import { Radio, Play, Loader2, AlertCircle, TrendingUp, Radar } from 'lucide-react'
import clsx from 'clsx'

const METHODS = [
  { value: 'both', label: 'TLS + BLS (RECOMMENDED)', desc: 'Run both algorithms simultaneously' },
  { value: 'tls', label: 'TLS ONLY', desc: 'Transit Least Squares' },
  { value: 'bls', label: 'BLS ONLY', desc: 'Box Least Squares' },
]

export default function Detection() {
  const { activeDataset, detectionResult, setDetectionResult, setActiveCandidateId } = useAppStore()
  const [config, setConfig] = useState({ method: 'both', min_period: 0.5, max_period: 27.0, snr_threshold: 7.0 })
  const [selectedCand, setSelectedCand] = useState(null)

  const mutation = useMutation({
    mutationFn: () => detectionApi.run(activeDataset.id, config),
    onSuccess: (res) => {
      setDetectionResult(res.data)
      toast.success(`Scan complete. Found ${res.data.num_candidates} anomaly(s).`)
    },
    onError: () => toast.error('Detection scan failed to initialize'),
  })

  if (!activeDataset) return (
    <div className="card flex flex-col items-center py-20 text-center animate-fade-in border-dashed border-2">
      <AlertCircle size={48} className="text-cosmic-gold mb-4 drop-shadow-glow-cyan" />
      <h2 className="text-xl font-display font-bold text-white tracking-widest uppercase">No Active Target</h2>
      <p className="text-sm text-gray-400 mt-2 max-w-sm">Load a target from the archives before scanning for transits.</p>
    </div>
  )

  const r = detectionResult
  const cand = selectedCand || r?.candidates?.[0]

  return (
    <div className="space-y-8 pb-10">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Config */}
        <div className="card lg:col-span-4 flex flex-col h-full">
          <h3 className="section-title flex items-center gap-3"><Radar size={20} className="text-cosmic-purple" />Scanner Config</h3>
          <p className="section-subtitle text-xs mb-8">Set parameters for the periodic transit search algorithms</p>
          
          <div className="space-y-6 flex-1">
            <div className="space-y-3">
              <label className="text-[10px] font-sans uppercase tracking-widest text-cosmic-purple/80 block">Detection Algorithm</label>
              <div className="space-y-3">
                {METHODS.map(m => (
                  <label key={m.value} className={clsx(
                    'flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all relative overflow-hidden group',
                    config.method === m.value ? 'border-cosmic-purple/50 bg-cosmic-purple/10 shadow-glow-purple' : 'border-white/10 bg-white/5 hover:border-white/30'
                  )}>
                    {config.method === m.value && <div className="absolute inset-0 bg-cosmic-purple/5 pointer-events-none"></div>}
                    <div className={clsx('w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors', config.method === m.value ? 'border-cosmic-purple' : 'border-gray-500')}>
                      {config.method === m.value && <div className="w-2.5 h-2.5 bg-cosmic-purple rounded-full" />}
                    </div>
                    <input type="radio" name="method" value={m.value} checked={config.method === m.value}
                      onChange={e => setConfig(c => ({ ...c, method: e.target.value }))} className="hidden" />
                    <div className="relative z-10">
                      <div className={clsx("text-sm font-display font-semibold tracking-wide", config.method === m.value ? "text-white" : "text-gray-300 group-hover:text-white")}>{m.label}</div>
                      <div className="text-[10px] uppercase font-sans tracking-widest text-gray-500 mt-1">{m.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-[10px] font-sans uppercase tracking-widest text-cosmic-purple/80 block">Min Period (d)</label>
                <input type="number" step="0.1" min="0.1" className="input h-12 bg-white/5 border-white/10 font-mono" value={config.min_period}
                  onChange={e => setConfig(c => ({ ...c, min_period: +e.target.value }))} />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-sans uppercase tracking-widest text-cosmic-purple/80 block">Max Period (d)</label>
                <input type="number" step="1" min="1" className="input h-12 bg-white/5 border-white/10 font-mono" value={config.max_period}
                  onChange={e => setConfig(c => ({ ...c, max_period: +e.target.value }))} />
              </div>
            </div>
            
            <div className="space-y-2 group">
              <label className="text-[10px] font-sans uppercase tracking-widest text-cosmic-purple/80 block">SNR Threshold</label>
              <div className="flex items-center gap-4">
                <input type="range" min="3" max="20" step="0.5" value={config.snr_threshold}
                  onChange={e => setConfig(c => ({ ...c, snr_threshold: +e.target.value }))}
                  className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer focus:outline-none"
                  style={{ accentColor: '#8B5CF6' }}
                />
                <div className="text-sm text-white font-mono bg-white/5 px-2 py-1 rounded border border-white/10 w-12 text-center">{config.snr_threshold}</div>
              </div>
            </div>
          </div>
          
          <button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="btn-accent w-full justify-center h-14 text-base mt-8">
            {mutation.isPending ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
            {mutation.isPending ? 'SCANNING SECTOR...' : 'INITIATE TRANSIT SCAN'}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-8 space-y-6">
          <AnimatePresence mode="wait">
            {mutation.isPending && (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="card flex flex-col items-center py-32 border border-cosmic-purple/30 bg-cosmic-purple/5 relative overflow-hidden h-full"
              >
                <div className="absolute inset-0 bg-cosmic-purple/10 animate-pulse pointer-events-none"></div>
                <Radar size={56} className="text-cosmic-purple animate-spin-slow mb-6 drop-shadow-glow-purple relative z-10" />
                <p className="text-lg font-display uppercase tracking-widest text-cosmic-purple font-bold relative z-10">Searching for Anomalies...</p>
                <p className="text-xs text-cosmic-purple/60 mt-2 font-mono uppercase tracking-widest relative z-10">Computing Periodogram Matrix</p>
              </motion.div>
            )}

            {!r && !mutation.isPending && (
              <motion.div 
                key="empty"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="card flex flex-col items-center justify-center h-full py-32 text-center border-dashed border-2 border-white/5 bg-white/5"
              >
                <Radio size={48} className="text-white/10 mb-4" />
                <p className="text-sm font-sans tracking-wide text-gray-400 max-w-sm">Set scanner configurations and initiate scan to detect periodic light curve anomalies.</p>
              </motion.div>
            )}

            {r && !mutation.isPending && (
              <motion.div 
                key="results"
                initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                className="space-y-6"
              >
                {/* Candidates list */}
                <div className="card">
                  <h3 className="section-title flex items-center gap-3"><TrendingUp size={20} className="text-cosmic-cyan" />Detected Anomalies <span className="text-sm font-normal text-gray-500 bg-white/5 px-3 py-1 rounded-full border border-white/10">{r.num_candidates} found</span></h3>
                  
                  {r.num_candidates === 0 ? (
                    <div className="text-sm text-cosmic-gold/80 bg-cosmic-gold/10 border border-cosmic-gold/20 rounded-xl p-6 text-center mt-4">
                      No significant periodic anomalies detected in this sector. Try lowering the SNR threshold.
                    </div>
                  ) : (
                    <div className="space-y-3 mt-4">
                      {r.candidates.map((c, i) => (
                        <motion.div 
                          initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                          key={c.id} onClick={() => { setSelectedCand(c); setActiveCandidateId(c.id) }}
                          className={clsx(
                            'flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all duration-300 relative overflow-hidden group',
                            (cand?.id === c.id) ? 'border-cosmic-cyan/50 bg-cosmic-cyan/10 shadow-glow-cyan' : 'border-white/10 bg-white/5 hover:border-cosmic-cyan/30 hover:bg-white/10'
                          )}>
                          {(cand?.id === c.id) && <div className="absolute inset-0 bg-gradient-to-r from-cosmic-cyan/5 to-transparent pointer-events-none"></div>}
                          
                          <div className={clsx("w-10 h-10 rounded-lg flex items-center justify-center font-display font-bold text-lg transition-colors z-10", (cand?.id === c.id) ? "bg-cosmic-cyan/20 text-cosmic-cyan border border-cosmic-cyan/30" : "bg-white/5 text-gray-400 border border-white/10")}>
                            {i + 1}
                          </div>
                          
                          <div className="flex-1 grid grid-cols-2 sm:grid-cols-5 gap-3 relative z-10">
                            <div className="flex flex-col gap-1">
                              <div className="text-[10px] uppercase font-sans tracking-widest text-gray-500">Method</div>
                              <div><span className={clsx('badge', c.method === 'TLS' ? 'badge-tls' : 'badge-bls')}>{c.method}</span></div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <div className="text-[10px] uppercase font-sans tracking-widest text-gray-500">Period</div>
                              <div className="font-mono text-white text-sm">{c.period?.toFixed(4)} <span className="text-gray-500 text-xs">d</span></div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <div className="text-[10px] uppercase font-sans tracking-widest text-gray-500">Depth</div>
                              <div className="font-mono text-white text-sm">{((c.depth || 0) * 1e6).toFixed(0)} <span className="text-gray-500 text-xs">ppm</span></div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <div className="text-[10px] uppercase font-sans tracking-widest text-gray-500">SNR</div>
                              <div className="font-mono text-white text-sm">{c.snr?.toFixed(1)}</div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <div className="text-[10px] uppercase font-sans tracking-widest text-gray-500">Transits</div>
                              <div className="font-mono text-white text-sm">{c.num_transits}</div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Charts */}
                {cand?.transit_data && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-0 overflow-hidden">
                    <div className="p-4 border-b border-white/10 bg-space-900/50 flex items-center justify-between">
                      <div className="font-display font-semibold text-white tracking-wide">
                        <span className="text-cosmic-cyan">{cand.method}</span> Hologram Analysis
                      </div>
                      <div className="flex gap-4 text-xs font-mono text-gray-400">
                        <span>P: <span className="text-white">{cand.period?.toFixed(4)} d</span></span>
                        <span>SNR: <span className="text-white">{cand.snr?.toFixed(1)}</span></span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/5">
                      <div className="p-4 bg-space-800">
                        <PlotlyChart
                          data={[{ x: cand.transit_data.periodogram_periods, y: cand.transit_data.periodogram_power, mode: 'lines', line: { color: '#8B5CF6', width: 1.5 }, name: 'Power' }]}
                          layout={{ title: { text: 'Periodogram Matrix', font: { size: 12, color: '#fff' } }, xaxis: { title: 'Period (d)', type: 'log', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#aaa' } }, yaxis: { title: 'Power Density', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#aaa' } }, height: 320, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#aaa' } }}
                        />
                      </div>
                      <div className="p-4 bg-space-800">
                        <PlotlyChart
                          data={[
                            { x: cand.transit_data.folded_time, y: cand.transit_data.folded_flux, mode: 'markers', marker: { color: 'rgba(6,182,212,0.4)', size: 3 }, name: 'Telemetry' },
                            { x: Array.from({ length: (cand.transit_data.model_flux || []).length }, (_, i) => -0.5 + i / (cand.transit_data.model_flux?.length - 1)), y: cand.transit_data.model_flux, mode: 'lines', line: { color: '#F43F5E', width: 2 }, name: 'Model Fit' },
                          ]}
                          layout={{ title: { text: 'Phase-Folded Superposition', font: { size: 12, color: '#fff' } }, xaxis: { title: 'Phase', range: [-0.5, 0.5], gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#aaa' } }, yaxis: { title: 'Relative Flux', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#aaa' } }, height: 320, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#aaa' }, legend: { font: { color: '#aaa' } } }}
                        />
                      </div>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
