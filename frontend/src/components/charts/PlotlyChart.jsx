import Plot from 'react-plotly.js'

const DEFAULT_LAYOUT = {
  autosize: true,
  margin: { l: 55, r: 20, t: 30, b: 50 },
  plot_bgcolor: '#FAFAFA',
  paper_bgcolor: '#FFFFFF',
  font: { family: 'Inter, sans-serif', size: 11 },
  legend: { x: 0.01, y: 0.99, bgcolor: 'rgba(255,255,255,0.8)', bordercolor: '#E5E7EB', borderwidth: 1 },
  hovermode: 'closest',
}

const DEFAULT_CONFIG = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['sendDataToCloud', 'toImage'],
  responsive: true,
  displaylogo: false,
}

export default function PlotlyChart({ data = [], layout = {}, config = {}, style = {} }) {
  return (
    <Plot
      data={data}
      layout={{ ...DEFAULT_LAYOUT, ...layout }}
      config={{ ...DEFAULT_CONFIG, ...config }}
      useResizeHandler
      style={{ width: '100%', minHeight: 300, ...style }}
    />
  )
}
