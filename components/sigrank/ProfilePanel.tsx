import React from 'react'
import { colors, fonts, radius, shadow } from './tokens'
import { SignalClassBadge } from './SignalClassBadge'
import type { UserProfile } from './types'

interface Props {
  profile?: UserProfile
}

const SAMPLE_PROFILE: UserProfile = {
  id: 'TX-132',
  rank: 13,
  tier: '#13 Overall',
  compositeScore: 0.92,
  metrics: [
    { label: 'Message Volume', score: 0.88, rank: 34 },
    { label: 'Session Depth', score: 0.91, rank: 22 },
    { label: 'Compression', score: 0.94, rank: 11 },
    { label: 'Prompt Complexity', score: 0.90, rank: 27 },
    { label: 'T-Index', score: 0.96, rank: 7 },
  ],
}

function ScoreBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = value >= 0.9 ? colors.bar.high : value >= 0.75 ? colors.bar.mid : colors.bar.low
  return (
    <div style={barStyles.wrapper}>
      <div style={{ ...barStyles.fill, width: `${pct}%`, background: color }} />
    </div>
  )
}

const barStyles: Record<string, React.CSSProperties> = {
  wrapper: {
    height: '4px',
    background: colors.bg.elevated,
    borderRadius: radius.xs,
    overflow: 'hidden',
    flex: 1,
    minWidth: '60px',
  },
  fill: {
    height: '100%',
    borderRadius: radius.xs,
    transition: 'width 0.3s',
  },
}

export function ProfilePanel({ profile = SAMPLE_PROFILE }: Props) {
  return (
    <div style={styles.wrapper}>
      {/* Profile header */}
      <div style={styles.header}>
        <div style={styles.idRow}>
          <span style={styles.profileId}>Profile: {profile.id}</span>
          <SignalClassBadge signalClass="TRANSMITTER" />
        </div>
        <div style={styles.rankRow}>
          <span style={styles.rankLabel}>Rank: {profile.tier}</span>
        </div>
        <div style={styles.scoreRow}>
          <span style={styles.scoreLabel}>Composite Score</span>
          <span style={styles.scoreValue}>{profile.compositeScore.toFixed(2)}</span>
        </div>
      </div>

      {/* Metrics */}
      <div style={styles.metricsSection}>
        {profile.metrics.map((m) => (
          <div key={m.label} style={styles.metricRow}>
            <span style={styles.metricLabel}>{m.label}</span>
            <ScoreBar value={m.score} />
            <span style={styles.metricScore}>{m.score.toFixed(2)}</span>
            <span style={styles.metricRank}>#{m.rank}</span>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div style={styles.actions}>
        <button style={styles.btnPrimary}>🔓 Unlock Full Identity</button>
        <div style={styles.btnRow}>
          <button style={styles.btnSecondary}>✉ Send Support</button>
          <button style={styles.btnSecondary}>◎ Match Heatmap</button>
        </div>
        <button style={styles.btnOutline}>★ Nominate for Guild</button>
      </div>

      {/* Footer note */}
      <div style={styles.footerNote}>
        Sign in with Signal Token to unlock full profile
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    background: colors.bg.surface,
    border: `1px solid ${colors.bg.border}`,
    borderRadius: radius.lg,
    boxShadow: shadow.card,
    padding: '16px',
    minWidth: '220px',
    maxWidth: '280px',
    fontFamily: fonts.sans,
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  header: {
    borderBottom: `1px solid ${colors.bg.border}`,
    paddingBottom: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  idRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  profileId: {
    fontFamily: fonts.mono,
    fontSize: '13px',
    fontWeight: 700,
    color: colors.text.primary,
  },
  rankRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  rankLabel: {
    fontFamily: fonts.mono,
    fontSize: '11px',
    color: colors.text.muted,
  },
  scoreRow: {
    display: 'flex',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginTop: '4px',
  },
  scoreLabel: {
    fontSize: '12px',
    color: colors.text.secondary,
  },
  scoreValue: {
    fontFamily: fonts.mono,
    fontSize: '24px',
    fontWeight: 700,
    color: colors.text.accent,
    letterSpacing: '-0.01em',
  },
  metricsSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  metricRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  metricLabel: {
    fontSize: '11px',
    color: colors.text.secondary,
    minWidth: '110px',
    flexShrink: 0,
  },
  metricScore: {
    fontFamily: fonts.mono,
    fontSize: '12px',
    fontWeight: 600,
    color: colors.text.primary,
    minWidth: '34px',
    textAlign: 'right',
  },
  metricRank: {
    fontFamily: fonts.mono,
    fontSize: '11px',
    color: colors.text.muted,
    minWidth: '28px',
    textAlign: 'right',
  },
  actions: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  btnPrimary: {
    background: `${colors.text.accent}20`,
    border: `1px solid ${colors.text.accent}50`,
    borderRadius: radius.md,
    color: colors.text.accent,
    fontFamily: fonts.sans,
    fontSize: '12px',
    fontWeight: 600,
    padding: '8px 12px',
    cursor: 'pointer',
    textAlign: 'center',
    letterSpacing: '0.02em',
  },
  btnRow: {
    display: 'flex',
    gap: '6px',
  },
  btnSecondary: {
    flex: 1,
    background: colors.bg.elevated,
    border: `1px solid ${colors.bg.border}`,
    borderRadius: radius.sm,
    color: colors.text.secondary,
    fontFamily: fonts.sans,
    fontSize: '11px',
    padding: '6px 8px',
    cursor: 'pointer',
    textAlign: 'center',
  },
  btnOutline: {
    background: 'transparent',
    border: `1px solid ${colors.text.gold}40`,
    borderRadius: radius.sm,
    color: colors.text.gold,
    fontFamily: fonts.sans,
    fontSize: '11px',
    padding: '6px 12px',
    cursor: 'pointer',
    textAlign: 'center',
  },
  footerNote: {
    fontSize: '10px',
    color: colors.text.dim,
    textAlign: 'center',
    fontFamily: fonts.sans,
  },
}
