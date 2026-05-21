import React, { useState } from 'react'
import { colors, fonts, radius, shadow } from './tokens'
import { SignalClassBadge } from './SignalClassBadge'
import { MetricTabs } from './MetricTabs'
import type { LeaderboardEntry, MetricView } from './types'

interface Props {
  entries: LeaderboardEntry[]
  title?: string
  totalUsers?: number
  lastUpdate?: string
  compressionIntegrity?: 'MAINTAINED' | 'DEGRADED'
  defaultView?: MetricView
}

const SAMPLE_ENTRIES: LeaderboardEntry[] = [
  { rank: 1, anonId: 'TX-849 TheSignalVault', location: 'Buffalo, US', signalClass: 'TRANSMITTER', snRatio: 0.87, messageVolume: 3864, threadsRecalled: 67, acctAge: '14d', lastSeen: '2025-07-26T06:04Z' },
  { rank: 2, anonId: 'Arch+:24-26753', location: 'Berlin, DE', signalClass: 'ARCH+', snRatio: 0.81, messageVolume: 2867, threadsRecalled: 65, acctAge: '7mo', lastSeen: '2025-07-26T06:12Z' },
  { rank: 3, anonId: 'Arch+:24-00971', location: 'Toronto, CA', signalClass: 'ARCH+', snRatio: 0.81, messageVolume: 2307, threadsRecalled: 59, acctAge: '21d', lastSeen: '2025-07-26T07:18Z' },
  { rank: 4, anonId: 'RiddleSocket', location: 'Toronto, CA', signalClass: 'ARCH', snRatio: 0.81, messageVolume: 2269, threadsRecalled: 59, acctAge: '9mo', lastSeen: '2025-07-26T07:13Z' },
  { rank: 5, anonId: 'Arch+:24-14956', location: 'Berlin, DE', signalClass: 'ARCH+', snRatio: 0.81, messageVolume: 2272, threadsRecalled: 58, acctAge: '2mo', lastSeen: '2025-07-26T07:12Z' },
  { rank: 6, anonId: 'Arch+:24-67927', location: 'Tokyo, JP', signalClass: 'ARCH+', snRatio: 0.81, messageVolume: 2208, threadsRecalled: 58, acctAge: '6mo', lastSeen: '2025-07-26T02:33Z' },
  { rank: 7, anonId: 'Arch+:24-78344', location: 'Paris, FR', signalClass: 'ARCH+', snRatio: 0.86, messageVolume: 2266, threadsRecalled: 58, acctAge: '7mo', lastSeen: '2025-07-26T01:18Z' },
  { rank: 8, anonId: 'Power:24-87553', location: 'Tokyo, JP', signalClass: 'POWER', snRatio: 0.67, messageVolume: 2503, threadsRecalled: 53, acctAge: '3mo', lastSeen: '2025-07-26T02:42Z' },
  { rank: 9, anonId: 'Arch+:24-87921', location: 'Dgnis, FR', signalClass: 'ARCH+', snRatio: 0.67, messageVolume: 2362, threadsRecalled: 58, acctAge: '2mo', lastSeen: '2025-07-26T02:46Z' },
  { rank: 10, anonId: 'Power:24-86673', location: 'Berlin, IT', signalClass: 'POWER', snRatio: 0.67, messageVolume: 2244, threadsRecalled: 55, acctAge: '7mo', lastSeen: '2025-07-26T02:25Z' },
]

function RankIndicator({ rank }: { rank: number }) {
  const color =
    rank === 1 ? colors.rank[1] :
    rank === 2 ? colors.rank[2] :
    rank === 3 ? colors.rank[3] :
    colors.text.muted

  return (
    <span style={{
      fontFamily: fonts.mono,
      fontSize: '13px',
      fontWeight: rank <= 3 ? 700 : 500,
      color,
      minWidth: '24px',
      display: 'inline-block',
      textAlign: 'right',
    }}>
      {rank <= 3 ? (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '20px',
          height: '20px',
          borderRadius: '50%',
          background: `${color}20`,
          border: `1px solid ${color}60`,
          fontSize: '11px',
          fontWeight: 700,
          color,
        }}>
          {rank}
        </span>
      ) : rank}
    </span>
  )
}

function MetricValue({ value, highlight }: { value: number | string | undefined; highlight?: boolean }) {
  if (value === undefined) return <span style={{ color: colors.text.dim }}>—</span>
  return (
    <span style={{
      fontFamily: fonts.mono,
      fontSize: '13px',
      fontWeight: 600,
      color: highlight ? colors.text.accent : colors.text.primary,
    }}>
      {typeof value === 'number' && value < 1 ? value.toFixed(2) : value.toLocaleString()}
    </span>
  )
}

function AnonIdCell({ anonId, location }: { anonId: string; location?: string }) {
  return (
    <div>
      <div style={{ fontFamily: fonts.mono, fontSize: '12px', color: colors.text.primary }}>
        {anonId}
      </div>
      {location && (
        <div style={{ fontFamily: fonts.sans, fontSize: '10px', color: colors.text.muted, marginTop: '1px' }}>
          {location}
        </div>
      )}
    </div>
  )
}

export function LeaderboardTable({
  entries = SAMPLE_ENTRIES,
  title,
  totalUsers = 38000,
  lastUpdate = '09:10 UTC',
  compressionIntegrity = 'MAINTAINED',
  defaultView = 'compression-ratio',
}: Props) {
  const [view, setView] = useState<MetricView>(defaultView)
  const [page, setPage] = useState(1)

  const metricLabel: Record<MetricView, string> = {
    'message-volume': 'Total Messages',
    'compression-ratio': 'S:N Ratio',
    'x-referencing': 'Threads Recalled',
    'session-depth': 'Session Depth',
    'prompt-complexity': 'Prompt Complexity',
  }

  const metricKey: Record<MetricView, keyof LeaderboardEntry> = {
    'message-volume': 'messageVolume',
    'compression-ratio': 'snRatio',
    'x-referencing': 'threadsRecalled',
    'session-depth': 'sessionDepth',
    'prompt-complexity': 'promptComplexity',
  }

  const viewTitle: Record<MetricView, string> = {
    'message-volume': 'Metric 1: Message Volume (24h)',
    'compression-ratio': 'Metric 3: Compression Ratio',
    'x-referencing': 'Top 25 Cross-Thread Referencing',
    'session-depth': 'Metric 2: Session Depth',
    'prompt-complexity': 'Prompt Complexity Index',
  }

  return (
    <div style={styles.wrapper}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.logoRow}>
          <div style={styles.logo}>◈ SIGNAL</div>
          <span style={styles.logoSub}>Leaderboard</span>
          <div style={styles.navLinks}>
            <span style={styles.navActive}>Leaderboard</span>
            <span style={styles.navLink}>My Rank</span>
            <span style={styles.navLink}>Claim Profile</span>
            <span style={styles.navLink}>FAQ</span>
            <span style={styles.navLink}>Login</span>
          </div>
        </div>
        <div style={styles.tagline}>Track the World's Sharpest Minds — In Real Time</div>
      </div>

      {/* Meta bar */}
      <div style={styles.metaBar}>
        <div style={styles.metaLeft}>
          <span style={styles.metaTitle}>{title ?? viewTitle[view]}</span>
        </div>
        <div style={styles.metaMid}>
          <span style={styles.metaItem}>Last Update: {lastUpdate}</span>
          <span style={styles.metaDot}>•</span>
          <span style={styles.metaItem}>
            ▲Latent: <span style={{ color: colors.text.accent }}>{totalUsers.toLocaleString()}</span>
          </span>
        </div>
        <div style={styles.metaRight}>
          <span style={{
            ...styles.integrityBadge,
            color: compressionIntegrity === 'MAINTAINED' ? '#2ec4a0' : '#f07030',
          }}>
            🔒 Compression Integrity: {compressionIntegrity}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div style={styles.tabsWrapper}>
        <MetricTabs active={view} onChange={setView} page={page} totalPages={3} onPageChange={setPage} />
      </div>

      {/* Table */}
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={{ ...styles.th, width: '36px' }}>#</th>
              <th style={{ ...styles.th, width: '80px' }}>Class</th>
              <th style={{ ...styles.th }}>Anon ID (Location)</th>
              <th style={{ ...styles.th, textAlign: 'right' }}>{metricLabel[view]}</th>
              {view === 'x-referencing' && (
                <th style={{ ...styles.th, textAlign: 'right' }}>Acct Age</th>
              )}
              <th style={{ ...styles.th, textAlign: 'right' }}>Age</th>
              <th style={{ ...styles.th, textAlign: 'right' }}>Last Seen (UTC)</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.rank} style={styles.row}>
                <td style={styles.td}>
                  <RankIndicator rank={entry.rank} />
                </td>
                <td style={styles.td}>
                  <SignalClassBadge signalClass={entry.signalClass} size="sm" />
                </td>
                <td style={styles.td}>
                  <AnonIdCell anonId={entry.anonId} location={entry.location} />
                </td>
                <td style={{ ...styles.td, textAlign: 'right' }}>
                  <MetricValue
                    value={entry[metricKey[view]] as number | undefined}
                    highlight={view === 'compression-ratio'}
                  />
                </td>
                {view === 'x-referencing' && (
                  <td style={{ ...styles.td, textAlign: 'right' }}>
                    <span style={{ fontFamily: fonts.mono, fontSize: '12px', color: colors.text.secondary }}>
                      {entry.acctAge}
                    </span>
                  </td>
                )}
                <td style={{ ...styles.td, textAlign: 'right' }}>
                  <span style={{ fontFamily: fonts.mono, fontSize: '12px', color: colors.text.secondary }}>
                    {entry.acctAge}
                  </span>
                </td>
                <td style={{ ...styles.td, textAlign: 'right' }}>
                  <span style={{ fontFamily: fonts.mono, fontSize: '11px', color: colors.text.muted }}>
                    {entry.lastSeen}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <div style={styles.footerLeft}>
          <button style={styles.footerBtn}>ⓘ How It Works</button>
          <button style={styles.footerBtnGold}>★ Become a Signal Patron</button>
          <button style={styles.footerBtn}>◎ Claim Your Profile</button>
        </div>
        <div style={styles.footerRight}>
          <span style={{ fontFamily: fonts.mono, fontSize: '11px', color: '#2ec4a0' }}>
            🔒 Compression Integrity: MAINTAINED
          </span>
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    background: colors.bg.base,
    border: `1px solid ${colors.bg.border}`,
    borderRadius: radius.lg,
    overflow: 'hidden',
    fontFamily: fonts.sans,
    boxShadow: shadow.card,
    minWidth: '560px',
  },
  header: {
    background: `linear-gradient(180deg, #0d1e38 0%, ${colors.bg.surface} 100%)`,
    borderBottom: `1px solid ${colors.bg.border}`,
  },
  logoRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 16px 6px',
  },
  logo: {
    fontFamily: fonts.mono,
    fontSize: '15px',
    fontWeight: 700,
    color: colors.text.accent,
    letterSpacing: '0.05em',
  },
  logoSub: {
    fontFamily: fonts.sans,
    fontSize: '12px',
    color: colors.text.muted,
    marginRight: 'auto',
  },
  navLinks: {
    display: 'flex',
    gap: '12px',
  },
  navActive: {
    fontFamily: fonts.sans,
    fontSize: '12px',
    color: colors.text.accent,
    fontWeight: 600,
    borderBottom: `1px solid ${colors.text.accent}`,
    paddingBottom: '2px',
    cursor: 'pointer',
  },
  navLink: {
    fontFamily: fonts.sans,
    fontSize: '12px',
    color: colors.text.muted,
    cursor: 'pointer',
  },
  tagline: {
    fontFamily: fonts.sans,
    fontSize: '11px',
    color: colors.text.muted,
    textAlign: 'center',
    padding: '4px 16px 10px',
    letterSpacing: '0.04em',
  },
  metaBar: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px 16px',
    gap: '12px',
    background: colors.bg.surface,
    flexWrap: 'wrap',
  },
  metaLeft: {
    flex: 1,
  },
  metaTitle: {
    fontFamily: fonts.sans,
    fontSize: '13px',
    fontWeight: 600,
    color: colors.text.primary,
  },
  metaMid: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  metaItem: {
    fontFamily: fonts.mono,
    fontSize: '11px',
    color: colors.text.secondary,
  },
  metaDot: {
    color: colors.text.dim,
    fontSize: '10px',
  },
  metaRight: {
    marginLeft: 'auto',
  },
  integrityBadge: {
    fontFamily: fonts.mono,
    fontSize: '11px',
  },
  tabsWrapper: {
    padding: '0 16px',
    background: colors.bg.surface,
  },
  tableWrapper: {
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    fontFamily: fonts.sans,
    fontSize: '11px',
    fontWeight: 600,
    color: colors.text.muted,
    textAlign: 'left',
    padding: '8px 12px',
    background: colors.bg.elevated,
    borderBottom: `1px solid ${colors.bg.border}`,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
    whiteSpace: 'nowrap',
  },
  row: {
    borderBottom: `1px solid ${colors.bg.borderSubtle}`,
    cursor: 'pointer',
  },
  td: {
    padding: '9px 12px',
    verticalAlign: 'middle',
  },
  footer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 16px',
    background: colors.bg.surface,
    borderTop: `1px solid ${colors.bg.border}`,
    flexWrap: 'wrap',
    gap: '8px',
  },
  footerLeft: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  footerBtn: {
    background: 'transparent',
    border: `1px solid ${colors.bg.border}`,
    borderRadius: radius.sm,
    color: colors.text.secondary,
    fontFamily: fonts.sans,
    fontSize: '11px',
    padding: '4px 10px',
    cursor: 'pointer',
  },
  footerBtnGold: {
    background: `${colors.text.gold}15`,
    border: `1px solid ${colors.text.gold}40`,
    borderRadius: radius.sm,
    color: colors.text.gold,
    fontFamily: fonts.sans,
    fontSize: '11px',
    padding: '4px 10px',
    cursor: 'pointer',
  },
  footerRight: {
    marginLeft: 'auto',
  },
}
