import React from 'react'
import { colors, fonts, radius, shadow } from './tokens'
import type { SystemMetricRow } from './types'

interface Props {
  username?: string
  rank?: number
  score?: number
  metrics?: SystemMetricRow[]
  unlockMessage?: string
  footerNote?: string
}

const SAMPLE_METRICS: SystemMetricRow[] = [
  { label: 'Session Depth', avgUser: 7.4, avgAI: 9.2, userValue: 31.5 },
  { label: 'Message Volume', avgUser: 240, avgAI: 340, userValue: 1170 },
  { label: 'Compression Ratio', avgUser: 0.61, avgAI: 0.72, userValue: 0.83 },
  { label: 'Prompt Complexity', avgUser: 4.1, avgAI: 5.8, userValue: 8.9 },
  { label: 'Cross-Thread Ref', avgUser: 1.6, avgAI: 2.5, userValue: 7.0 },
  { label: 'Account Age', avgUser: 92, avgAI: 160, userValue: 580, unit: 'd' },
  { label: 'Total Messages', avgUser: 1600, avgAI: 2500, userValue: 8700 },
  { label: 'System Type Score', avgUser: 1.0, avgAI: 2.4, userValue: 4.6 },
]

function CompareBar({ avgUser, avgAI, user }: { avgUser: number; avgAI: number; user: number }) {
  const max = Math.max(avgUser, avgAI, user) * 1.1
  const userPct = (user / max) * 100
  const aiPct = (avgAI / max) * 100
  const userBarPct = (avgUser / max) * 100

  return (
    <div style={barStyles.wrapper}>
      {/* User bar (faint background) */}
      <div style={{ ...barStyles.track }}>
        <div style={{ ...barStyles.barUser, width: `${userBarPct}%` }} />
      </div>
      <div style={{ ...barStyles.track }}>
        <div style={{ ...barStyles.barAI, width: `${aiPct}%` }} />
      </div>
      <div style={{ ...barStyles.track }}>
        <div style={{ ...barStyles.barYou, width: `${userPct}%` }} />
      </div>
    </div>
  )
}

const barStyles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    minWidth: '80px',
    flex: 1,
  },
  track: {
    height: '4px',
    background: colors.bg.elevated,
    borderRadius: '2px',
    overflow: 'hidden',
  },
  barUser: {
    height: '100%',
    background: `${colors.class.BASE}80`,
    borderRadius: '2px',
  },
  barAI: {
    height: '100%',
    background: `${colors.class['ARCH+']}80`,
    borderRadius: '2px',
  },
  barYou: {
    height: '100%',
    background: colors.text.accent,
    borderRadius: '2px',
  },
}

function formatVal(v: number, unit?: string) {
  if (unit) return `${v}${unit}`
  if (v >= 1000) return v.toLocaleString()
  if (v < 10 && v % 1 !== 0) return v.toFixed(2)
  return v.toString()
}

export function SignalSystemBoard({
  username = 'signalxxxUSA',
  rank = 17,
  score = 4.6,
  metrics = SAMPLE_METRICS,
  unlockMessage = 'Your signal class unlocks next tier access!\nTransmitter-class confirmed // Private channel unlocked. Welcome to the rebellion.',
  footerNote = '© 2025 SignalVault | SurveyKard | Luther\'s\nAll signal is monitored. All drift is noted.\nUnauthorized replication? That\'s our signal if life\'s its own noise.\nTT: Welcome to the Board of Leaders.',
}: Props) {
  return (
    <div style={styles.wrapper}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.brandRow}>
          <span style={styles.brand}>◈ SIGRANK</span>
          <span style={styles.rankChip}>★ Rank #{rank} • {score}</span>
        </div>
        <div style={styles.titleRow}>
          <span style={styles.titleMain}>YOUR SIGNAL SYSTEM</span>
        </div>
        <div style={styles.subtitle}>BOARD OF LEADERS</div>
      </div>

      {/* Table */}
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Metric</th>
              <th style={{ ...styles.th, textAlign: 'right' }}>Avg User</th>
              <th style={{ ...styles.th, textAlign: 'right' }}>Avg AI</th>
              <th style={{ ...styles.th, textAlign: 'right' }}>{username}</th>
              <th style={{ ...styles.th, width: '100px' }}></th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((row) => {
              const isTop = row.userValue > row.avgAI * 1.5
              return (
                <tr key={row.label} style={styles.row}>
                  <td style={styles.td}>
                    <span style={styles.metricLabel}>{row.label}</span>
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right' }}>
                    <span style={styles.avgUser}>{formatVal(row.avgUser, row.unit)}</span>
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right' }}>
                    <span style={styles.avgAI}>{formatVal(row.avgAI, row.unit)}</span>
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right' }}>
                    <span style={{
                      ...styles.userVal,
                      color: isTop ? colors.text.accent : colors.text.primary,
                    }}>
                      {formatVal(row.userValue, row.unit)}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <CompareBar avgUser={row.avgUser} avgAI={row.avgAI} user={row.userValue} />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div style={styles.legend}>
        {[
          { color: `${colors.class.BASE}80`, label: 'Avg User' },
          { color: `${colors.class['ARCH+']}80`, label: 'Avg AI' },
          { color: colors.text.accent, label: 'You' },
        ].map((l) => (
          <div key={l.label} style={styles.legendItem}>
            <div style={{ width: '20px', height: '3px', background: l.color, borderRadius: '2px' }} />
            <span style={styles.legendLabel}>{l.label}</span>
          </div>
        ))}
      </div>

      {/* Unlock message */}
      {unlockMessage && (
        <div style={styles.unlockBlock}>
          <div style={styles.unlockIcon}>🔓</div>
          <div style={styles.unlockText}>
            {unlockMessage.split('\n').map((line, i) => (
              <div key={i} style={i === 0 ? styles.unlockPrimary : styles.unlockSecondary}>
                {line}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      {footerNote && (
        <div style={styles.footer}>
          {footerNote.split('\n').map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      )}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    background: `linear-gradient(160deg, #070e1c 0%, #060a14 100%)`,
    border: `1px solid ${colors.bg.border}`,
    borderRadius: radius.lg,
    overflow: 'hidden',
    boxShadow: shadow.card,
    fontFamily: fonts.sans,
    maxWidth: '580px',
  },
  header: {
    padding: '16px 20px 12px',
    background: `linear-gradient(180deg, #0d1e38 0%, #080f1e 100%)`,
    borderBottom: `1px solid ${colors.bg.border}`,
    textAlign: 'center',
  },
  brandRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '8px',
  },
  brand: {
    fontFamily: fonts.mono,
    fontSize: '13px',
    fontWeight: 700,
    color: colors.text.accent,
    letterSpacing: '0.08em',
  },
  rankChip: {
    fontFamily: fonts.mono,
    fontSize: '11px',
    color: colors.text.gold,
    background: `${colors.text.gold}15`,
    border: `1px solid ${colors.text.gold}30`,
    borderRadius: radius.sm,
    padding: '2px 8px',
  },
  titleRow: {
    marginBottom: '2px',
  },
  titleMain: {
    fontFamily: fonts.mono,
    fontSize: '17px',
    fontWeight: 700,
    color: colors.text.primary,
    letterSpacing: '0.1em',
  },
  subtitle: {
    fontFamily: fonts.mono,
    fontSize: '11px',
    color: colors.text.muted,
    letterSpacing: '0.14em',
  },
  tableWrapper: {
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    fontFamily: fonts.mono,
    fontSize: '10px',
    fontWeight: 700,
    color: colors.text.muted,
    textAlign: 'left',
    padding: '8px 12px',
    background: colors.bg.elevated,
    borderBottom: `1px solid ${colors.bg.border}`,
    letterSpacing: '0.06em',
    whiteSpace: 'nowrap',
  },
  row: {
    borderBottom: `1px solid ${colors.bg.borderSubtle}`,
  },
  td: {
    padding: '9px 12px',
    verticalAlign: 'middle',
  },
  metricLabel: {
    fontFamily: fonts.sans,
    fontSize: '12px',
    color: colors.text.secondary,
    whiteSpace: 'nowrap',
  },
  avgUser: {
    fontFamily: fonts.mono,
    fontSize: '12px',
    color: colors.text.muted,
  },
  avgAI: {
    fontFamily: fonts.mono,
    fontSize: '12px',
    color: colors.class['ARCH+'],
  },
  userVal: {
    fontFamily: fonts.mono,
    fontSize: '13px',
    fontWeight: 700,
  },
  legend: {
    display: 'flex',
    gap: '16px',
    padding: '8px 14px',
    background: colors.bg.surface,
    borderBottom: `1px solid ${colors.bg.border}`,
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  legendLabel: {
    fontFamily: fonts.sans,
    fontSize: '10px',
    color: colors.text.muted,
  },
  unlockBlock: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '10px',
    padding: '12px 16px',
    background: `${colors.text.accent}08`,
    borderBottom: `1px solid ${colors.text.accent}20`,
    borderTop: `1px solid ${colors.text.accent}20`,
  },
  unlockIcon: {
    fontSize: '16px',
    flexShrink: 0,
    marginTop: '1px',
  },
  unlockText: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  unlockPrimary: {
    fontFamily: fonts.sans,
    fontSize: '12px',
    fontWeight: 600,
    color: colors.text.accent,
  },
  unlockSecondary: {
    fontFamily: fonts.sans,
    fontSize: '11px',
    color: colors.text.secondary,
  },
  footer: {
    padding: '10px 16px',
    fontFamily: fonts.mono,
    fontSize: '9px',
    color: colors.text.dim,
    lineHeight: 1.7,
    background: colors.bg.surface,
    textAlign: 'center',
  },
}
