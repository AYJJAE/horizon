import { useQuery } from '@tanstack/react-query'
import { visualizationApi } from '../api/client'
import { useAppStore } from '../store/appStore'
import PlotlyChart from '../components/charts/PlotlyChart'
import { BarChart3, AlertCircle, Loader2, Activity } from 'lucide-react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

const getDarkThemeLayout = (baseLayout = {}) => ({
  ...baseLayout,
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { color: '#aaa', family: '"Inter", sans-serif' },
  title: { ...baseLayout.title, font: { color: '#fff', size: 14, family: '"Space Grotesk", sans-serif' } },
  xaxis: { ...baseLayout.xaxis, gridcolor: 'rgba(255,255,255,0.05)', zerolinecolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#888' } },
  yaxis: { ...baseLayout.yaxis, gridcolor: 'rgba(255,255,255,0.05)', zerolinecolor: 'rgba(255,255,255,0.1)', tickfont: { color: '#888' } },
  legend: { ...baseLayout.legend, font: { color: '#aaa' }, bgcolor: 'rgba(0,0,0,0.5)', bordercolor: 'rgba(255,255,255,0.1)' }
})

const getDarkThemeData = (data = []) => {
  return data.map(trace => {
    // Modify colors if they exist in the trace to fit dark theme
    const newTrace = { ...trace };
    if (newTrace.line && newTrace.line.color) {
      // Very basic color mapping for dark theme pop
      if (newTrace.line.color === '#3B82F6') newTrace.line.color = '#06B6D4';
      if (newTrace.line.color === '#F59E0B') newTrace.line.color = '#FBBF24';
      if (newTrace.line.color === '#EF4444') newTrace.line.color = '#F43F5E';
    }
    if (newTrace.marker && newTrace.marker.color) {
      if (newTrace.marker.color === '#CBD5E1') newTrace.marker.color = 'rgba(255,255,255,0.2)';
    }
    return newTrace;
  })
}

export default function Visualization() {
  const { activeDataset } = useAppStore()

  const { data, isLoading, error } = useQuery({
    queryKey: ['visualization', activeDataset?.id],
    queryFn: () => visualizationApi.getPlots(activeDataset.id).then(r => r.data),
    enabled: !!activeDataset?.id,
  })

  if (!activeDataset) return (
    <div className="card flex flex-col items-center py-24 text-center animate-fade-in border-dashed border-2">
      <AlertCircle size={48} className="text-cosmic-gold mb-4 drop-shadow-glow-cyan" />
      <h2 className="text-xl font-display font-bold text-white tracking-widest uppercase">Observatory Offline</h2>
      <p className="text-sm text-gray-400 mt-2 max-w-sm">Target acquisition required. Load a dataset to initialize the observatory console.</p>
    </div>
  )

  if (isLoading) return (
    <div className="card flex flex-col items-center py-32 border border-cosmic-cyan/30 bg-cosmic-cyan/5 relative overflow-hidden">
      <div className="absolute inset-0 bg-cosmic-cyan/10 animate-pulse pointer-events-none"></div>
      <Loader2 size={56} className="text-cosmic-cyan animate-spin mb-6 drop-shadow-glow-cyan relative z-10" />
      <p className="text-lg font-display uppercase tracking-widest text-cosmic-cyan font-bold relative z-10">Rendering Holograms...</p>
      <p className="text-xs text-cosmic-cyan/60 mt-2 font-mono uppercase tracking-widest relative z-10">Constructing Interactive Data Models</p>
    </div>
  )

  return (
    <div className="space-y-8 pb-10">
      
      <div className="flex items-center justify-between border-b border-white/10 pb-6">
        <div>
          <h2 className="text-3xl font-display font-bold text-white flex items-center gap-3 tracking-wide">
            <BarChart3 size={28} className="text-cosmic-cyan drop-shadow-glow-cyan" />
            OBSERVATORY CONSOLE
          </h2>
          <p className="text-cosmic-cyan/80 font-mono text-xs mt-2 uppercase tracking-widest">Active Target: {activeDataset.name}</p>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full border border-cosmic-cyan/30 bg-cosmic-cyan/10">
          <span className="w-2 h-2 rounded-full bg-cosmic-cyan animate-pulse"></span>
          <span className="text-cosmic-cyan text-[10px] font-display uppercase tracking-widest font-bold">Telemetry Live</span>
        </div>
      </div>

      {/* Raw Light Curve */}
      {data?.raw_light_curve && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card p-0 overflow-hidden border-white/10 bg-space-900/40">
          <div className="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center gap-3">
            <Activity size={16} className="text-cosmic-cyan" />
            <div className="font-display font-bold text-white tracking-widest uppercase text-sm">Full Light Curve Telemetry</div>
          </div>
          <div className="p-2">
            <PlotlyChart 
              data={getDarkThemeData(data.raw_light_curve.data)} 
              layout={getDarkThemeLayout({ ...data.raw_light_curve.layout, height: 400 })} 
            />
          </div>
        </motion.div>
      )}

      {/* Periodogram + Folded Transit */}
      {(data?.periodogram || data?.folded_transit) && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {data?.periodogram && (
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="card p-0 overflow-hidden border-white/10 bg-space-900/40">
              <div className="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center gap-3">
                <div className="font-display font-bold text-white tracking-widest uppercase text-sm">
                  {data.periodogram.layout?.title?.text || 'Periodogram Matrix'}
                </div>
              </div>
              <div className="p-2">
                <PlotlyChart 
                  data={getDarkThemeData(data.periodogram.data)} 
                  layout={getDarkThemeLayout({ ...data.periodogram.layout, height: 350, title: '' })} 
                />
              </div>
            </motion.div>
          )}
          {data?.folded_transit && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="card p-0 overflow-hidden border-white/10 bg-space-900/40">
              <div className="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center gap-3">
                <div className="font-display font-bold text-white tracking-widest uppercase text-sm">Phase-Folded Superposition</div>
              </div>
              <div className="p-2">
                <PlotlyChart 
                  data={getDarkThemeData(data.folded_transit.data)} 
                  layout={getDarkThemeLayout({ ...data.folded_transit.layout, height: 350, title: '' })} 
                />
              </div>
            </motion.div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Detection Timeline */}
        {data?.detection_timeline && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card p-0 overflow-hidden border-white/10 bg-space-900/40">
            <div className="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center gap-3">
              <div className="font-display font-bold text-white tracking-widest uppercase text-sm">Transit Chronology</div>
            </div>
            <div className="p-2">
              <PlotlyChart 
                data={getDarkThemeData(data.detection_timeline.data)} 
                layout={getDarkThemeLayout({ ...data.detection_timeline.layout, height: 320, title: '' })} 
              />
            </div>
          </motion.div>
        )}

        {/* Depth Comparison */}
        {data?.transit_depth_chart && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card p-0 overflow-hidden border-white/10 bg-space-900/40">
            <div className="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center gap-3">
              <div className="font-display font-bold text-white tracking-widest uppercase text-sm">Depth Consistency Analysis</div>
            </div>
            <div className="p-2">
              <PlotlyChart 
                data={getDarkThemeData(data.transit_depth_chart.data)} 
                layout={getDarkThemeLayout({ ...data.transit_depth_chart.layout, height: 320, title: '' })} 
              />
            </div>
          </motion.div>
        )}
      </div>

      {!data?.raw_light_curve && !data?.periodogram && (
        <div className="card flex flex-col items-center py-24 text-center border-dashed border-2 border-white/5 bg-white/5">
          <BarChart3 size={48} className="text-white/10 mb-4" />
          <p className="text-sm font-sans tracking-wide text-gray-400 max-w-sm">Execute preprocessing and transit scans to generate holographic data visualizations.</p>
        </div>
      )}
    </div>
  )
}
