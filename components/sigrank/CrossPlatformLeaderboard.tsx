import React from 'react'
import { colors, fonts, radius, shadow } from './tokens'
import type { CrossPlatformEntry, Platform } from './types'

interface Props {
  entries?: CrossPlatformEntry[]
  title?: string
}

const SAMPLE_ENTRIES: CrossPlatformEntry[] = [
  { rank: 1, username: 'keter-3862-US', platform: 'ChatGPT', transmitter: 25443, sdrm: 3.14, signalForce: 12.8 },
  { rank: 2, username: 'archplus-3271-CA', platform: 'Claude', transmitter: 22100, sdrm: 2.95, signalForce: 11.4 },
  { rank: 3, username: 'arch-2197-EU', platform: 'Pi', transmitter: 20442, sdrm: 2.75, signalForce: 10.6 },
]

const PLATFORM_COLORS: Record<Platform, string> = {
  ChatGPT: '#10a37f',
  Claude: '#d97706',
  Pi: '#6366f1',
  Gemini: '#4285f4',
}

const PLATFORM_SYMBOLS: Record<Platform, string> = {
  ChatGPT: '⊕',
  Claude: 'C',
  Pi: 'π',
  Gemini: 'G',
}

function PlatformBadge({ platform }: { platform: Platform }) {
  const color = PLATFORM_COLORS[platform]
  const symbol = PLATFORM_SYMBOLS[platform]
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
    }}>
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '20px',
        height: '20px',
        borderRadius: '50%',
        background: `${color}25`,
        border: `1px solid ${color}60`,
        fontFamily: fonts.mono,
        fontSize: '11px',
        fontWeight: 700,
        color,
      }}>
        {symbol}
      </span>
      <span style={{
        fontFamily: fonts.sans,
        fontSize: '12px',
        color,
        fontWeight: 500,
      }}>
        {platform}
      </span>
    </div>
  )
}

function RankMedal({ rank }: { rank: number }) {
  const configs: Record<number, { color: string; glow: string }> = {
    1: { color: '#f5a020', glow: 'rgba(245,160,32,0.3)' },
    2: { color: '#94a3b8', glow: 'rgba(148,163,184,0.3)' },
    3: { color: '#cd7f32', glow: 'rgba(205,127,50,0.3)' },
  }
  const cfg = configs[rank] ?? { color: colors.text.muted, glow: 'transparent' }
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '28px',
      height: '28px',
      borderRadius: '50%',
      background: `${cfg.color}15`,
      border: `1.5px solid ${cfg.color}50`,
      boxShadow: `0 0 8px ${cfg.glow}`,
      fontFamily: fonts.mono,
      fontSize: '13px',
      fontWeight: 700,
      color: cfg.color,
    }}>
      #{rank}
    </span>
  )
}

export function CrossPlatformLeaderboard({
  entries = SAMPLE_ENTRIES,
  title = 'Cross-Platform Leaderboard — Live Transmission Index',
}: Props) {
  return (
    <div style={styles.wrapper}>
      {/* Starfield background overlay */}
      <div style={styles.starfield} aria-hidden />

      <div style={styles.content}>
        {/* Header */}
        <div style={styles.header}>
          <span style={styles.fire}>🔥</span>
          <h2 style={styles.title}>{title}</h2>
        </div>

        {/* Table */}
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>RANK</th>
                <th style={styles.th}>USERNAME</th>
                <th style={styles.th}>AI PLATFORM</th>
                <th style={{ ...styles.th, textAlign: 'right' }}>TRANSMITTER</th>
                <th style={{ ...styles.th, textAlign: 'right' }}>SDRM</th>
                <th style={{ ...styles.th, textAlign: 'right' }}>SIGNAL FORCE</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.rank} style={styles.row}>
                  <td style={styles.td}>
                    <RankMedal rank={entry.rank} />
                  </td>
                  <td style={styles.td}>
                    <span style={styles.username}>{entry.username}</span>
                  </td>
                  <td style={styles.td}>
                    <PlatformBadge platform={entry.platform} />
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right' }}>
                    <span style={styles.metric}>{entry.transmitter.toLocaleString()}</span>
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right' }}>
                    <span style={styles.metric}>{entry.sdrm.toFixed(2)}</span>
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right' }}>
                    <span style={{
                      ...styles.metric,
                      color: entry.rank === 1 ? colors.text.gold : colors.text.accent,
                      fontWeight: 700,
                      fontSize: '15px',
                    }}>
                      {entry.signalForce.toFixed(1)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Logo footer */}
        <div style={styles.logoRow}>
          <span style={styles.logoS}>◈</span>
          <span style={styles.logoText}>SIGRANK</span>
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    position: 'relative',
    background: 'radial-gradient(ellipse at 50% 0%, #0a1a2e 0%, #030810 70%)',
    border: `1px solid #0d2040`,
    borderRadius: radius.xl,
    overflow: 'hidden',
    boxShadow: '0 4px 40px rgba(0,0,0,0.8)',
    fontFamily: fonts.sans,
    minWidth: '520px',
  },
  starfield: {
    position: 'absolute',
    inset: 0,
    backgroundImage:
      'radial-gradient(1px 1px at 15% 20%, rgba(255,255,255,0.4) 0%, transparent 100%),' +
      'radial-gradient(1px 1px at 40% 60%, rgba(255,255,255,0.3) 0%, transparent 100%),' +
      'radial-gradient(1px 1px at 70% 15%, rgba(255,255,255,0.5) 0%, transparent 100%),' +
      'radial-gradient(1px 1px at 85% 75%, rgba(255,255,255,0.2) 0%, transparent 100%),' +
      'radial-gradient(1px 1px at 25% 85%, rgba(255,255,255,0.3) 0%, transparent 100%),' +
      'radial-gradient(2px 2px at 90% 40%, rgba(0,207,255,0.4) 0%, transparent 100%)',
    pointerEvents: 'none',
  },
  content: {
    position: 'relative',
    padding: '24px 20px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    justifyContent: 'center',
  },
  fire: {
    fontSize: '18px',
  },
  title: {
    fontFamily: fonts.sans,
    fontSize: '14px',
    fontWeight: 700,
    color: colors.text.primary,
    margin: 0,
    letterSpacing: '0.02em',
  },
  tableWrapper: {
    background: 'rgba(10,20,40,0.7)',
    border: `1px solid #0d2040`,
    borderRadius: radius.md,
    overflow: 'hidden',
    backdropFilter: 'blur(4px)',
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
    padding: '8px 14px',
    background: 'rgba(10,24,50,0.8)',
    borderBottom: `1px solid #0d2040`,
    letterSpacing: '0.08em',
    whiteSpace: 'nowrap',
  },
  row: {
    borderBottom: `1px solid rgba(13,32,64,0.6)`,
  },
  td: {
    padding: '14px',
    verticalAlign: 'middle',
  },
  username: {
    fontFamily: fonts.mono,
    fontSize: '13px',
    color: colors.text.primary,
    fontWeight: 500,
  },
  metric: {
    fontFamily: fonts.mono,
    fontSize: '13px',
    color: colors.text.primary,
    fontWeight: 600,
  },
  logoRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
  },
  logoS: {
    fontFamily: fonts.mono,
    fontSize: '18px',
    color: colors.text.accent,
  },
  logoText: {
    fontFamily: fonts.mono,
    fontSize: '16px',
    fontWeight: 700,
    color: colors.text.accent,
    letterSpacing: '0.15em',
  },
}
