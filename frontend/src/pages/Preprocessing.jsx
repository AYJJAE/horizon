import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { preprocessingApi } from '../api/client'
import { useAppStore } from '../store/appStore'
import PlotlyChart from '../components/charts/PlotlyChart'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { Play, Sliders, AlertCircle, Loader2, CheckCircle2, Activity, Settings2 } from 'lucide-react'
import clsx from 'clsx'

const CONFIG_DEFAULTS = { sigma_clip: 4.0, detrend_method: 'savgol', savgol_window: 51, interpolate: true, normalize: true }

export default function Preprocessing() {
  const { activeDataset, preprocessingResult, setPreprocessingResult } = useAppStore()
  const [config, setConfig] = useState(CONFIG_DEFAULTS)
  const [activeTab, setActiveTab] = useState('overlay')

  const mutation = useMutation({
    mutationFn: () => preprocessingApi.run(activeDataset.id, config),
    onSuccess: (res) => { setPreprocessingResult(res.data); toast.success('Signal cleaning complete!') },
    onError: () => toast.error('Preprocessing failed to complete'),
  })

  if (!activeDataset) return (
    <div className="card flex flex-col items-center py-20 text-center animate-fade-in border-dashed border-2">
      <AlertCircle size={48} className="text-cosmic-gold mb-4 drop-shadow-glow-cyan" />
      <h2 className="text-xl font-display font-bold text-white tracking-widest uppercase">No Active Target</h2>
      <p className="text-sm text-gray-400 mt-2 max-w-sm">Access the Archive to load a target into memory before initiating signal cleaning protocols.</p>
    </div>
  )

  const r = preprocessingResult

  return (
    <div className="space-y-8 pb-10">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Config panel */}
        <div className="card lg:col-span-4 flex flex-col h-full">
          <h3 className="section-title flex items-center gap-3"><Settings2 size={20} className="text-cosmic-cyan" />Cleaning Protocol</h3>
          <p className="section-subtitle text-xs mb-8">Configure pipeline parameters for signal noise reduction</p>
          
          <div className="space-y-6 flex-1">
            <div className="space-y-2 relative group">
              <label className="text-[10px] font-sans uppercase tracking-widest text-cosmic-cyan/80 block">Sigma Clipping (σ)</label>
              <div className="flex items-center gap-4">
                <input type="range" min="2" max="8" step="0.5" value={config.sigma_clip}
                  onChange={e => setConfig(c => ({ ...c, sigma_clip: +e.target.value }))}
                  className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer focus:outline-none" 
                  style={{ accentColor: '#06B6D4' }}
                />
                <div className="text-sm text-white font-mono bg-white/5 px-2 py-1 rounded border border-white/10 w-12 text-center">{config.sigma_clip}</div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-sans uppercase tracking-widest text-cosmic-cyan/80 block">Detrending Method</label>
              <select className="input h-12 bg-white/5 border-white/10" value={config.detrend_method}
                onChange={e => setConfig(c => ({ ...c, detrend_method: e.target.value }))}>
                <option value="savgol" className="bg-space-800">Savitzky-Golay Filter</option>
                <option value="spline" className="bg-space-800">Cubic Spline Interpolation</option>
                <option value="wotan" className="bg-space-800">Wotan Biweight</option>
              </select>
            </div>

            {config.detrend_method === 'savgol' && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="space-y-2">
                <label className="text-[10px] font-sans uppercase tracking-widest text-cosmic-cyan/80 block">Savgol Window</label>
                <input type="number" min="11" max="301" step="10" className="input h-12 bg-white/5 border-white/10 font-mono" value={config.savgol_window}
                  onChange={e => setConfig(c => ({ ...c, savgol_window: +e.target.value }))} />
              </motion.div>
            )}

            <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 hover:border-cosmic-cyan/30 transition-colors">
              <label className="text-xs font-display uppercase tracking-widest text-white cursor-pointer select-none" onClick={() => setConfig(c => ({ ...c, interpolate: !c.interpolate }))}>Interpolate Gaps</label>
              <button onClick={() => setConfig(c => ({ ...c, interpolate: !c.interpolate }))}
                className={clsx('w-12 h-6 rounded-full transition-colors duration-300 relative border border-white/20', config.interpolate ? 'bg-cosmic-cyan shadow-glow-cyan' : 'bg-white/10')}>
                <span className={clsx('absolute top-0.5 left-0.5 block w-4 h-4 bg-white rounded-full shadow transition-transform duration-300', config.interpolate ? 'translate-x-6' : 'translate-x-0')} />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 hover:border-cosmic-cyan/30 transition-colors">
              <label className="text-xs font-display uppercase tracking-widest text-white cursor-pointer select-none" onClick={() => setConfig(c => ({ ...c, normalize: !c.normalize }))}>Median Normalize</label>
              <button onClick={() => setConfig(c => ({ ...c, normalize: !c.normalize }))}
                className={clsx('w-12 h-6 rounded-full transition-colors duration-300 relative border border-white/20', config.normalize ? 'bg-cosmic-purple shadow-glow-purple' : 'bg-white/10')}>
                <span className={clsx('absolute top-0.5 left-0.5 block w-4 h-4 bg-white rounded-full shadow transition-transform duration-300', config.normalize ? 'translate-x-6' : 'translate-x-0')} />
              </button>
            </div>
          </div>

          <button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="btn-primary w-full justify-center h-14 text-base mt-6">
            {mutation.isPending ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
            {mutation.isPending ? 'PROCESSING SIGNAL...' : 'INITIALIZE PROTOCOL'}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-8 space-y-6">
          {r && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { label: 'Raw Data Points', value: r.summary?.raw_points?.toLocaleString() },
                { label: 'Cleaned Points', value: r.summary?.clean_points?.toLocaleString() },
                { label: 'Anomalies Purged', value: r.outliers_removed, color: 'text-cosmic-red' },
                { label: 'Signal Gaps Filled', value: r.gaps_interpolated, color: 'text-cosmic-green' },
                { label: 'Flux Mean Base', value: r.summary?.flux_mean?.toFixed(5) },
                { label: 'Standard Deviation', value: r.summary?.flux_std?.toFixed(6) },
              ].map(({ label, value, color }, i) => (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}
                  key={label} className="p-4 rounded-xl bg-white/5 border border-white/10 relative overflow-hidden group hover:bg-white/10 hover:border-cosmic-cyan/30 transition-colors"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <div className={clsx("text-2xl font-display font-bold relative z-10", color || "text-white")}>{value ?? '—'}</div>
                  <div className="text-[10px] uppercase font-sans tracking-widest text-gray-400 mt-1 relative z-10">{label}</div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {r && (
            <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="card p-2 overflow-hidden flex flex-col min-h-[450px]">
              <div className="flex gap-2 p-2 border-b border-white/10">
                {['overlay', 'clean', 'trend'].map(t => (
                  <button key={t} onClick={() => setActiveTab(t)}
                    className={clsx('px-4 py-2 rounded-lg text-xs font-display uppercase tracking-widest transition-all relative overflow-hidden', activeTab === t ? 'text-cosmic-cyan bg-cosmic-cyan/10 border border-cosmic-cyan/30 shadow-glow-cyan' : 'text-gray-500 hover:text-white hover:bg-white/5 border border-transparent')}>
                    {t === 'overlay' ? 'Raw vs Clean' : t === 'clean' ? 'Cleaned Signal' : 'Stellar Trend'}
                  </button>
                ))}
              </div>
              <div className="flex-1 p-2 bg-space-900/50 rounded-xl mt-2 relative">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3N2Zz4=')] opacity-50 pointer-events-none"></div>
                {activeTab === 'overlay' && (
                  <PlotlyChart data={[
                    { x: r.raw_time, y: r.raw_flux, mode: 'markers', marker: { color: 'rgba(255,255,255,0.2)', size: 3 }, name: 'Raw' },
                    { x: r.clean_time, y: r.clean_flux, mode: 'markers', marker: { color: '#06B6D4', size: 3 }, name: 'Clean' },
                    { x: r.raw_time, y: r.trend, mode: 'lines', line: { color: '#F59E0B', width: 2, dash: 'dash' }, name: 'Trend' },
                  ]} layout={{ xaxis: { title: 'Time (BTJD)', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#fff' }, titlefont: { color: '#fff' } }, yaxis: { title: 'Flux', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#fff' }, titlefont: { color: '#fff' } }, height: 400, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#fff' }, legend: { font: { color: '#fff' } } }} />
                )}
                {activeTab === 'clean' && (
                  <PlotlyChart data={[
                    { x: r.clean_time, y: r.clean_flux, mode: 'markers', marker: { color: '#8B5CF6', size: 3 }, name: 'Cleaned' },
                  ]} layout={{ xaxis: { title: 'Time (BTJD)', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#fff' }, titlefont: { color: '#fff' } }, yaxis: { title: 'Normalized Flux', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#fff' }, titlefont: { color: '#fff' } }, height: 400, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#fff' }, legend: { font: { color: '#fff' } } }} />
                )}
                {activeTab === 'trend' && (
                  <PlotlyChart data={[
                    { x: r.raw_time, y: r.trend, mode: 'lines', line: { color: '#F59E0B', width: 2 }, name: 'Stellar Trend' },
                  ]} layout={{ xaxis: { title: 'Time (BTJD)', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#fff' }, titlefont: { color: '#fff' } }, yaxis: { title: 'Trend', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#fff' }, titlefont: { color: '#fff' } }, height: 400, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#fff' }, legend: { font: { color: '#fff' } } }} />
                )}
              </div>
            </motion.div>
          )}

          {!r && !mutation.isPending && (
            <div className="card flex flex-col items-center py-24 text-center border-dashed border-2 border-white/5 bg-white/5">
              <Activity size={48} className="text-white/10 mb-4" />
              <p className="text-sm font-sans tracking-wide text-gray-400">Configure parameters and run the protocol to analyze telemetry.</p>
            </div>
          )}
          
          {mutation.isPending && (
            <div className="card flex flex-col items-center py-24 border border-cosmic-cyan/30 bg-cosmic-cyan/5 relative overflow-hidden">
              <div className="absolute inset-0 bg-cosmic-cyan/10 animate-pulse pointer-events-none"></div>
              <Loader2 size={48} className="text-cosmic-cyan animate-spin mb-6 drop-shadow-glow-cyan relative z-10" />
              <p className="text-base font-display uppercase tracking-widest text-cosmic-cyan font-bold relative z-10">Processing Telemetry...</p>
              <p className="text-xs text-cosmic-cyan/70 mt-2 font-mono uppercase relative z-10">Sigma Clipping → Detrending → Interpolation</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
