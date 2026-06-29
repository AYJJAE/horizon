import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { reportsApi } from '../api/client'
import { useAppStore } from '../store/appStore'
import toast from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import { FileDown, Loader2, AlertCircle, FileText, FileSpreadsheet, CheckCircle2, Satellite } from 'lucide-react'
import clsx from 'clsx'

export default function Reports() {
  const { activeDataset } = useAppStore()
  const [format, setFormat] = useState('both')
  const [includePlots, setIncludePlots] = useState(true)
  const [reportResult, setReportResult] = useState(null)

  const mutation = useMutation({
    mutationFn: () => reportsApi.generate({ dataset_id: activeDataset.id, format, include_plots: includePlots }),
    onSuccess: (res) => { setReportResult(res.data); toast.success('Data export completed successfully.') },
    onError: () => toast.error('Failed to generate report export'),
  })

  const getFilename = (path) => path?.split(/[\\/]/).pop()

  if (!activeDataset) return (
    <div className="card flex flex-col items-center py-24 text-center animate-fade-in border-dashed border-2">
      <AlertCircle size={48} className="text-cosmic-gold mb-4 drop-shadow-glow-cyan" />
      <h2 className="text-xl font-display font-bold text-white tracking-widest uppercase">No Active Target</h2>
      <p className="text-sm text-gray-400 mt-2 max-w-sm">Load a target from the archives before generating communication logs and scientific reports.</p>
    </div>
  )

  return (
    <div className="space-y-8 pb-10 max-w-4xl mx-auto">
      
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card relative overflow-hidden p-8 sm:p-10">
        <div className="absolute top-0 right-0 w-64 h-64 bg-cosmic-purple/10 blur-3xl rounded-full pointer-events-none"></div>
        <div className="relative z-10">
          <h3 className="text-2xl font-display font-bold text-white flex items-center gap-3 tracking-wide mb-2">
            <FileDown size={24} className="text-cosmic-purple drop-shadow-glow-purple" />
            Communications Array
          </h3>
          <p className="text-gray-400 font-sans text-sm mb-8">Export comprehensive telemetric data, validation matrices, and planetary parameters.</p>

          <div className="space-y-8">
            {/* Dataset info */}
            <div className="p-6 rounded-2xl bg-white/5 border border-white/10 flex items-start gap-4">
              <Satellite size={24} className="text-cosmic-cyan animate-pulse-slow" />
              <div>
                <div className="text-[10px] uppercase font-sans tracking-widest text-gray-400 mb-1">Target Loaded</div>
                <div className="text-lg font-display font-bold text-white tracking-wide">{activeDataset.name}</div>
                {activeDataset.tic_id && <div className="text-xs text-cosmic-cyan font-mono mt-1">TIC {activeDataset.tic_id}</div>}
              </div>
            </div>

            {/* Format */}
            <div className="space-y-3">
              <label className="text-[10px] uppercase font-sans tracking-widest text-cosmic-purple/80 block">Data Transmission Format</label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  { value: 'pdf', label: 'PDF DOCUMENT', icon: FileText, desc: 'Scientific layout with data tables' },
                  { value: 'csv', label: 'CSV MATRIX', icon: FileSpreadsheet, desc: 'Raw unformatted data for analysis' },
                  { value: 'both', label: 'FULL PACKAGE', icon: FileDown, desc: 'Complete PDF + CSV bundle' },
                ].map(({ value, label, icon: Icon, desc }) => (
                  <label key={value} className={clsx(
                    'flex flex-col items-center gap-3 p-6 rounded-2xl border cursor-pointer transition-all text-center relative overflow-hidden group',
                    format === value ? 'border-cosmic-purple/50 bg-cosmic-purple/10 shadow-glow-purple scale-[1.02]' : 'border-white/10 bg-white/5 hover:border-cosmic-purple/30 hover:bg-white/10'
                  )}>
                    {format === value && <div className="absolute inset-0 bg-cosmic-purple/5 pointer-events-none"></div>}
                    <input type="radio" name="format" value={value} checked={format === value}
                      onChange={() => setFormat(value)} className="sr-only" />
                    <Icon size={28} className={clsx("transition-colors relative z-10", format === value ? 'text-cosmic-purple' : 'text-gray-400 group-hover:text-white')} />
                    <div className="relative z-10">
                      <div className={clsx("text-sm font-display font-bold tracking-widest", format === value ? "text-white" : "text-gray-300")}>{label}</div>
                      <div className="text-[10px] font-sans text-gray-500 mt-2 uppercase tracking-wide">{desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Include plots */}
            <div className="flex items-center justify-between p-6 rounded-2xl border border-white/10 bg-white/5 hover:border-cosmic-purple/30 transition-colors">
              <div>
                <div className="text-sm font-display font-bold text-white tracking-widest uppercase mb-1 cursor-pointer" onClick={() => setIncludePlots(v => !v)}>Embed Holograms</div>
                <div className="text-xs text-gray-400 font-sans">Include rendered light curves and periodograms in the PDF output</div>
              </div>
              <button onClick={() => setIncludePlots(v => !v)}
                className={clsx('w-12 h-6 rounded-full transition-colors duration-300 relative border border-white/20', includePlots ? 'bg-cosmic-purple shadow-glow-purple' : 'bg-white/10')}>
                <span className={clsx('absolute top-0.5 left-0.5 block w-4 h-4 bg-white rounded-full shadow transition-transform duration-300', includePlots ? 'translate-x-6' : 'translate-x-0')} />
              </button>
            </div>

            <button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="btn-accent w-full justify-center h-14 text-base tracking-widest">
              {mutation.isPending ? <Loader2 size={18} className="animate-spin" /> : <FileDown size={18} />}
              {mutation.isPending ? 'ENCRYPTING DATA PACKAGE...' : 'TRANSMIT REPORT TO LOCAL STORAGE'}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Download links */}
      <AnimatePresence>
        {reportResult && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="card border-cosmic-green/30 bg-cosmic-green/5 relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-32 h-32 bg-cosmic-green/10 blur-2xl rounded-full pointer-events-none"></div>
            
            <div className="flex items-center gap-3 mb-6 relative z-10">
              <CheckCircle2 size={24} className="text-cosmic-green drop-shadow-glow-green" />
              <h3 className="font-display font-bold text-white tracking-widest text-lg">TRANSMISSION RECEIVED</h3>
            </div>
            
            <div className="space-y-4 relative z-10">
              {reportResult.pdf_path && (
                <a
                  href={reportsApi.downloadUrl(getFilename(reportResult.pdf_path))}
                  download
                  className="flex items-center gap-4 p-5 rounded-2xl border border-white/10 bg-white/5 hover:border-cosmic-red/50 hover:bg-cosmic-red/10 transition-all cursor-pointer group"
                >
                  <FileText size={28} className="text-cosmic-red drop-shadow-glow-red flex-shrink-0" />
                  <div className="flex-1">
                    <div className="font-display font-bold text-white tracking-wider group-hover:text-cosmic-red transition-colors">{getFilename(reportResult.pdf_path)}</div>
                    <div className="text-[10px] uppercase font-sans tracking-widest text-gray-400 mt-1">PDF Scientific Report</div>
                  </div>
                  <FileDown size={20} className="text-gray-500 group-hover:text-white transition-colors" />
                </a>
              )}
              {reportResult.csv_path && (
                <a
                  href={reportsApi.downloadUrl(getFilename(reportResult.csv_path))}
                  download
                  className="flex items-center gap-4 p-5 rounded-2xl border border-white/10 bg-white/5 hover:border-cosmic-green/50 hover:bg-cosmic-green/10 transition-all cursor-pointer group"
                >
                  <FileSpreadsheet size={28} className="text-cosmic-green drop-shadow-glow-green flex-shrink-0" />
                  <div className="flex-1">
                    <div className="font-display font-bold text-white tracking-wider group-hover:text-cosmic-green transition-colors">{getFilename(reportResult.csv_path)}</div>
                    <div className="text-[10px] uppercase font-sans tracking-widest text-gray-400 mt-1">CSV Data Export Matrix</div>
                  </div>
                  <FileDown size={20} className="text-gray-500 group-hover:text-white transition-colors" />
                </a>
              )}
            </div>
            
            <div className="mt-6 text-[10px] text-gray-500 font-mono tracking-widest uppercase text-center relative z-10">
              Timestamp: {new Date(reportResult.generated_at).toISOString()}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
