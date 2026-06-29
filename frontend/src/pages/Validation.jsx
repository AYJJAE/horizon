import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { validationApi } from '../api/client'
import { useAppStore } from '../store/appStore'
import PlotlyChart from '../components/charts/PlotlyChart'
import toast from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import { ShieldCheck, Play, Loader2, AlertCircle, CheckCircle2, XCircle, HelpCircle, Activity } from 'lucide-react'
import clsx from 'clsx'

const LABEL_CONFIG = {
  PLANET: { color: 'text-cosmic-green', bg: 'bg-cosmic-green/10 border-cosmic-green/30 shadow-glow-green', icon: CheckCircle2, badge: 'badge-planet' },
  FALSE_POSITIVE: { color: 'text-cosmic-red', bg: 'bg-cosmic-red/10 border-cosmic-red/30 shadow-glow-red', icon: XCircle, badge: 'badge-fp' },
  UNKNOWN: { color: 'text-cosmic-gold', bg: 'bg-cosmic-gold/10 border-cosmic-gold/30 shadow-[0_0_15px_rgba(245,158,11,0.2)]', icon: HelpCircle, badge: 'badge-unknown' },
}

const FlagRow = ({ label, value, flag, delay = 0 }) => (
  <motion.div 
    initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay }}
    className="flex items-center justify-between p-3 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-colors"
  >
    <span className="text-sm font-display text-gray-300">{label}</span>
    <span className={clsx('text-[10px] font-sans tracking-widest uppercase font-bold px-3 py-1 rounded-md border', flag ? 'bg-cosmic-red/10 text-cosmic-red border-cosmic-red/30' : 'bg-cosmic-green/10 text-cosmic-green border-cosmic-green/30')}>
      {flag ? '⚠ Anomalous' : '✓ Nominal'}
    </span>
  </motion.div>
)

export default function Validation() {
  const { activeCandidateId, detectionResult, validationResults, setValidationResult } = useAppStore()
  const [selectedId, setSelectedId] = useState(activeCandidateId)

  const mutation = useMutation({
    mutationFn: (cid) => validationApi.run(cid),
    onSuccess: (res, cid) => { setValidationResult(cid, res.data); toast.success('Machine learning validation complete.') },
    onError: () => toast.error('Validation sequence failed'),
  })

  const candidates = detectionResult?.candidates || []
  const activeId = selectedId || candidates[0]?.id
  const valResult = validationResults[activeId]

  if (!candidates.length) return (
    <div className="card flex flex-col items-center py-24 text-center animate-fade-in border-dashed border-2">
      <AlertCircle size={48} className="text-cosmic-gold mb-4 drop-shadow-glow-cyan" />
      <h2 className="text-xl font-display font-bold text-white tracking-widest uppercase">No Candidates Detected</h2>
      <p className="text-sm text-gray-400 mt-2 max-w-sm">Execute the Transit Scan to identify potential anomalies before validation.</p>
    </div>
  )

  const label = valResult?.ml_label || 'UNKNOWN'
  const cfg = LABEL_CONFIG[label] || LABEL_CONFIG.UNKNOWN
  const LabelIcon = cfg.icon
  const score = valResult?.composite_score || 0

  return (
    <div className="space-y-8 pb-10">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Candidate selector */}
        <div className="card lg:col-span-4 flex flex-col h-full">
          <h3 className="section-title flex items-center gap-3"><ShieldCheck size={20} className="text-cosmic-cyan" />Anomaly Selection</h3>
          <p className="section-subtitle text-xs mb-6">Select a candidate for deep neural network validation</p>
          
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
                
                <span className={clsx('badge relative z-10', c.method === 'TLS' ? 'badge-tls' : 'badge-bls')}>{c.method}</span>
                <div className="flex-1 text-xs relative z-10">
                  <div className="font-display font-semibold text-white tracking-wide">P: {c.period?.toFixed(4)} d</div>
                  <div className="text-gray-400 font-mono mt-0.5 tracking-wider text-[10px]">SNR {c.snr?.toFixed(1)} | {((c.depth || 0) * 1e6).toFixed(0)} ppm</div>
                </div>
                {validationResults[c.id] && (
                  <span className={clsx('badge text-[10px] tracking-widest uppercase relative z-10', LABEL_CONFIG[validationResults[c.id].ml_label]?.badge)}>
                    {(validationResults[c.id].composite_score * 100).toFixed(0)}%
                  </span>
                )}
              </motion.div>
            ))}
          </div>
          
          <button onClick={() => mutation.mutate(activeId)} disabled={mutation.isPending || !activeId} className="btn-primary w-full justify-center h-14 text-base mt-6">
            {mutation.isPending ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
            {mutation.isPending ? 'VALIDATING...' : 'EXECUTE VALIDATION'}
          </button>
        </div>

        {/* Validation results */}
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
                <p className="text-lg font-display uppercase tracking-widest text-cosmic-cyan font-bold relative z-10">Analyzing Candidate...</p>
                <p className="text-xs text-cosmic-cyan/60 mt-2 font-mono uppercase tracking-widest relative z-10">Running Deep Neural Network & Statistical Verification</p>
              </motion.div>
            )}

            {!valResult && !mutation.isPending && (
              <motion.div 
                key="empty"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="card flex flex-col items-center justify-center h-full py-32 text-center border-dashed border-2 border-white/5 bg-white/5"
              >
                <ShieldCheck size={48} className="text-white/10 mb-4" />
                <p className="text-sm font-sans tracking-wide text-gray-400 max-w-sm">Select a detected anomaly and initiate the validation sequence to verify planetary status.</p>
              </motion.div>
            )}

            {valResult && !mutation.isPending && (
              <motion.div 
                key="results"
                initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                className="space-y-6"
              >
                {/* Classification banner */}
                <div className={clsx('card border relative overflow-hidden', cfg.bg)}>
                  <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 blur-3xl rounded-full pointer-events-none"></div>
                  <div className="flex items-center gap-6 relative z-10">
                    <LabelIcon size={48} className={clsx("drop-shadow-glow", cfg.color)} />
                    <div className="flex-1">
                      <div className={clsx('text-3xl font-display font-bold tracking-wider uppercase', cfg.color)}>{label.replace('_', ' ')}</div>
                      <div className="text-xs text-gray-300 font-sans tracking-widest uppercase mt-1">Classification: <span className="font-bold text-white">{valResult.fp_category?.replace(/_/g, ' ')}</span></div>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-display font-bold text-white tracking-widest">{(score * 100).toFixed(1)}<span className="text-xl text-gray-400">%</span></div>
                      <div className="text-[10px] text-gray-400 font-sans tracking-widest uppercase mt-1">Composite Confidence</div>
                    </div>
                  </div>
                  {/* Score bar */}
                  <div className="mt-6 h-2 rounded-full bg-black/40 overflow-hidden relative">
                    <motion.div 
                      initial={{ width: 0 }} animate={{ width: `${score * 100}%` }} transition={{ duration: 1, ease: "easeOut" }}
                      className={clsx("h-full rounded-full relative", label === 'PLANET' ? "bg-cosmic-green" : label === 'FALSE_POSITIVE' ? "bg-cosmic-red" : "bg-cosmic-gold")}
                    >
                      <div className="absolute inset-0 bg-white/20 w-1/3 blur-sm animate-pulse-slow"></div>
                    </motion.div>
                  </div>
                </div>

                {/* Scores breakdown */}
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { label: 'Neural Net Confidence', value: ((valResult.ml_confidence || 0) * 100).toFixed(1) + '%', sub: valResult.ml_label },
                    { label: 'Statistical Integrity', value: ((valResult.statistical_score || 0) * 100).toFixed(1) + '%', sub: 'Weighted metrics' },
                    { label: 'Composite Score', value: (score * 100).toFixed(1) + '%', sub: '60% ML + 40% Stat' },
                  ].map(({ label, value, sub }, i) => (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + (i * 0.1) }}
                      key={label} className="card text-center flex flex-col items-center justify-center p-6 border border-white/5 bg-white/5 hover:border-white/20 transition-colors"
                    >
                      <div className="text-2xl font-display font-bold text-white">{value}</div>
                      <div className="text-[10px] font-sans tracking-widest uppercase text-cosmic-cyan mt-2">{label}</div>
                      <div className="text-xs text-gray-500 font-mono mt-1">{sub}</div>
                    </motion.div>
                  ))}
                </div>

                {/* Statistical flags */}
                <div className="card border border-white/5">
                  <h4 className="section-title text-base flex items-center gap-2"><Activity size={16} className="text-cosmic-cyan" />Statistical Diagnostics</h4>
                  <div className="space-y-3 mt-4">
                    <FlagRow label="Odd-Even Transit Comparison" flag={valResult.odd_even_flag} delay={0.2} />
                    <FlagRow label="Transit Shape Consistency" flag={valResult.shape_flag} delay={0.3} />
                    <FlagRow label="Depth Stability Across Transits" flag={valResult.depth_stability_flag} delay={0.4} />
                    {valResult.details?.snr_flag !== undefined && (
                      <FlagRow label="SNR Threshold Analysis" flag={valResult.details.snr_flag} delay={0.5} />
                    )}
                  </div>
                </div>

                {/* SHAP values */}
                {valResult.shap_values?.values && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="card border border-white/5">
                    <h4 className="section-title text-base flex items-center gap-2">Feature Importance (SHAP Matrix)</h4>
                    <p className="text-[10px] text-gray-400 font-sans tracking-widest uppercase mb-4">Neural Network decision weighting</p>
                    <div className="bg-space-900/50 p-2 rounded-xl border border-white/5">
                      <PlotlyChart
                        data={[{
                          x: valResult.shap_values.values.slice(0, 40),
                          y: valResult.shap_values.feature_names?.slice(0, 40),
                          type: 'bar',
                          orientation: 'h',
                          marker: { color: valResult.shap_values.values.slice(0, 40).map(v => v > 0 ? '#10B981' : '#EF4444') },
                        }]}
                        layout={{ height: 350, margin: { l: 150, r: 20, t: 20, b: 40 }, xaxis: { title: 'SHAP value (Impact on Model)', gridcolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#aaa' }, titlefont: { color: '#aaa' } }, yaxis: { title: '', tickfont: { color: '#aaa', size: 10 } }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#aaa' } }}
                      />
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
