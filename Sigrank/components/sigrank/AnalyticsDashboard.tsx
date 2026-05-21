import React from 'react'
import { colors, fonts, radius, shadow } from './tokens'
import type { RadarMetric, ActivityDay } from './types'

// ─── Radar Chart (pure SVG) ─────────────────────────────────────────────────

interface RadarChartProps {
  metrics: RadarMetric[]
  size?: number
  compareMetrics?: RadarMetric[]
}

function RadarChart({ metrics, size = 160, compareMetrics }: RadarChartProps) {
  const cx = size / 2
  const cy = size / 2
  const r = size * 0.38
  const n = metrics.length

  function polarToXY(angle: number, radius: number) {
    const a = angle - Math.PI / 2
    return { x: cx + radius * Math.cos(a), y: cy + radius * Math.sin(a) }
  }

  function metricToPoints(mets: RadarMetric[]) {
    return mets.map((m, i) => {
      const angle = (2 * Math.PI * i) / n
      const val = Math.min(1, Math.max(0, m.value / (m.max ?? 1)))
      return polarToXY(angle, r * val)
    })
  }

  const gridLevels = [0.25, 0.5, 0.75, 1.0]

  const primaryPoints = metricToPoints(metrics)
  const primaryPath = primaryPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') + ' Z'

  const comparePoints = compareMetrics ? metricToPoints(compareMetrics) : null
  const comparePath = comparePoints
    ? comparePoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') + ' Z'
    : null

  return (
    <svg width={size} height={size} style={{ overflow: 'visible' }}>
      {/* Grid */}
      {gridLevels.map((level) => {
        const pts = Array.from({ length: n }, (_, i) => polarToXY((2 * Math.PI * i) / n, r * level))
        const path = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') + ' Z'
        return (
          <path key={level} d={path} fill="none" stroke={colors.bg.border} strokeWidth="0.8" />
        )
      })}

      {/* Axes */}
      {metrics.map((_, i) => {
        const outer = polarToXY((2 * Math.PI * i) / n, r)
        return (
          <line key={i} x1={cx} y1={cy} x2={outer.x.toFixed(1)} y2={outer.y.toFixed(1)}
            stroke={colors.bg.border} strokeWidth="0.8" />
        )
      })}

      {/* Compare area */}
      {comparePath && (
        <path d={comparePath} fill={`${colors.class.ARCH}20`} stroke={colors.class.ARCH} strokeWidth="1.2" strokeDasharray="3,2" />
      )}

      {/* Primary area */}
      <path d={primaryPath} fill={`${colors.text.accent}25`} stroke={colors.text.accent} strokeWidth="1.5" />

      {/* Dots */}
      {primaryPoints.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="3" fill={colors.text.accent} />
      ))}

      {/* Labels */}
      {metrics.map((m, i) => {
        const angle = (2 * Math.PI * i) / n
        const labelPt = polarToXY(angle, r * 1.25)
        return (
          <text key={i}
            x={labelPt.x.toFixed(1)}
            y={labelPt.y.toFixed(1)}
            textAnchor="middle"
            dominantBaseline="middle"
            fill={colors.text.muted}
            fontSize="8"
            fontFamily={fonts.sans}
          >
            {m.label}
          </text>
        )
      })}
    </svg>
  )
}

// ─── Activity Heatmap ────────────────────────────────────────────────────────

interface HeatmapProps {
  days: ActivityDay[]
  weeks?: number
}

function ActivityHeatmap({ days, weeks = 16 }: HeatmapProps) {
  const cellSize = 10
  const gap = 2
  const totalCells = weeks * 7

  const filled = [...days].slice(-totalCells)
  while (filled.length < totalCells) filled.unshift({ date: '', count: 0 })

  function countToColor(count: number) {
    if (count === 0) return colors.bg.elevated
    if (count < 5) return `${colors.bar.high}30`
    if (count < 15) return `${colors.bar.high}60`
    if (count < 30) return `${colors.bar.high}90`
    return colors.bar.high
  }

  const grid: ActivityDay[][] = []
  for (let w = 0; w < weeks; w++) {
    grid.push(filled.slice(w * 7, w * 7 + 7))
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
      <div style={{ display: 'flex', gap: `${gap}px` }}>
        {grid.map((week, wi) => (
          <div key={wi} style={{ display: 'flex', flexDirection: 'column', gap: `${gap}px` }}>
            {week.map((day, di) => (
              <div
                key={di}
                title={day.date ? `${day.date}: ${day.count}` : ''}
                style={{
                  width: `${cellSize}px`,
                  height: `${cellSize}px`,
                  borderRadius: '2px',
                  background: countToColor(day.count),
                }}
              />
            ))}
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
        <span style={{ fontFamily: fonts.sans, fontSize: '9px', color: colors.text.muted }}>Less</span>
        {[0, 0.3, 0.6, 0.9, 1].map((v, i) => (
          <div key={i} style={{
            width: '10px', height: '10px', borderRadius: '2px',
            background: v === 0 ? colors.bg.elevated : `${colors.bar.high}${Math.round(v * 100).toString(16).padStart(2, '0')}`,
          }} />
        ))}
        <span style={{ fontFamily: fonts.sans, fontSize: '9px', color: colors.text.muted }}>More</span>
      </div>
    </div>
  )
}

// ─── Score Trend (mini SVG line chart) ───────────────────────────────────────

interface TrendProps {
  points: number[]
  width?: number
  height?: number
  color?: string
  label?: string
}

function ScoreTrend({ points, width = 120, height = 50, color = colors.text.accent, label }: TrendProps) {
  if (points.length < 2) return null
  const min = Math.min(...points)
  const max = Math.max(...points)
  const range = max - min || 1
  const pad = 4

  const coords = points.map((v, i) => ({
    x: pad + (i / (points.length - 1)) * (width - pad * 2),
    y: pad + (1 - (v - min) / range) * (height - pad * 2),
  }))

  const path = coords.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  const areaPath = path + ` L${coords[coords.length - 1].x.toFixed(1)},${height} L${coords[0].x.toFixed(1)},${height} Z`

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
      <svg width={width} height={height}>
        <path d={areaPath} fill={`${color}15`} />
        <path d={path} stroke={color} strokeWidth="1.5" fill="none" />
        {coords.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="2" fill={color} />
        ))}
      </svg>
      {label && (
        <span style={{ fontFamily: fonts.sans, fontSize: '10px', color: colors.text.muted }}>{label}</span>
      )}
    </div>
  )
}

// ─── Main Dashboard ──────────────────────────────────────────────────────────

const SAMPLE_RADAR: RadarMetric[] = [
  { label: 'Volume', value: 0.88, max: 1 },
  { label: 'Depth', value: 0.91, max: 1 },
  { label: 'Compress', value: 0.94, max: 1 },
  { label: 'Complexity', value: 0.90, max: 1 },
  { label: 'X-Ref', value: 0.82, max: 1 },
]

const SAMPLE_COMPARE: RadarMetric[] = [
  { label: 'Volume', value: 0.60, max: 1 },
  { label: 'Depth', value: 0.55, max: 1 },
  { label: 'Compress', value: 0.65, max: 1 },
  { label: 'Complexity', value: 0.58, max: 1 },
  { label: 'X-Ref', value: 0.50, max: 1 },
]

function makeActivityDays(): ActivityDay[] {
  const days: ActivityDay[] = []
  const now = new Date()
  for (let i = 112; i >= 0; i--) {
    const d = new Date(now)
    d.setDate(d.getDate() - i)
    days.push({
      date: d.toISOString().slice(0, 10),
      count: Math.random() > 0.3 ? Math.floor(Math.random() * 40) : 0,
    })
  }
  return days
}

const SAMPLE_TRENDS = {
  compression: [0.72, 0.75, 0.78, 0.76, 0.80, 0.83, 0.86, 0.88, 0.87, 0.90, 0.92, 0.94],
  volume: [1200, 1800, 2100, 1900, 2400, 2800, 3100, 2900, 3400, 3600, 3800, 3864],
  depth: [0.60, 0.65, 0.68, 0.70, 0.74, 0.78, 0.80, 0.83, 0.86, 0.88, 0.90, 0.91],
}

interface Props {
  radarMetrics?: RadarMetric[]
  compareMetrics?: RadarMetric[]
  activityDays?: ActivityDay[]
}

export function AnalyticsDashboard({
  radarMetrics = SAMPLE_RADAR,
  compareMetrics = SAMPLE_COMPARE,
  activityDays = makeActivityDays(),
}: Props) {
  return (
    <div style={styles.wrapper}>
      {/* Radar */}
      <div style={styles.panel}>
        <div style={styles.panelTitle}>Performance Overview</div>
        <div style={styles.radarWrapper}>
          <RadarChart metrics={radarMetrics} compareMetrics={compareMetrics} size={160} />
        </div>
        <div style={styles.legend}>
          <div style={styles.legendItem}>
            <div style={{ ...styles.legendDot, background: colors.text.accent }} />
            <span>You</span>
          </div>
          <div style={styles.legendItem}>
            <div style={{ ...styles.legendDot, background: colors.class.ARCH }} />
            <span>Top 50 Avg</span>
          </div>
        </div>
      </div>

      {/* Heatmap */}
      <div style={styles.panel}>
        <div style={styles.panelTitle}>Activity Heatmap</div>
        <ActivityHeatmap days={activityDays} weeks={16} />
      </div>

      {/* Trends */}
      <div style={styles.panel}>
        <div style={styles.panelTitle}>Score Trends</div>
        <div style={styles.trendsGrid}>
          <ScoreTrend points={SAMPLE_TRENDS.compression} color={colors.text.accent} label="Compression" />
          <ScoreTrend points={SAMPLE_TRENDS.depth} color={colors.class.SEEKER} label="Depth" />
          <ScoreTrend
            points={SAMPLE_TRENDS.volume.map(v => v / 4000)}
            color={colors.class['ARCH+']}
            label="Volume"
          />
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap',
    fontFamily: fonts.sans,
  },
  panel: {
    background: colors.bg.surface,
    border: `1px solid ${colors.bg.border}`,
    borderRadius: radius.lg,
    padding: '14px',
    boxShadow: shadow.card,
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    flex: '1 1 180px',
    minWidth: '180px',
  },
  panelTitle: {
    fontSize: '11px',
    fontWeight: 600,
    color: colors.text.muted,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  radarWrapper: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  legend: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    fontSize: '10px',
    color: colors.text.secondary,
    fontFamily: fonts.sans,
  },
  legendDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  trendsGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    alignItems: 'flex-start',
  },
}
