export type SignalClass =
  | 'TRANSMITTER'
  | 'ARCH+'
  | 'ARCH'
  | 'POWER'
  | 'BASE'
  | 'SEEKER'
  | 'REFINER'
  | 'BEARER'
  | 'IGNITER'

export type MetricView =
  | 'message-volume'
  | 'compression-ratio'
  | 'x-referencing'
  | 'session-depth'
  | 'prompt-complexity'

export type Platform = 'ChatGPT' | 'Claude' | 'Pi' | 'Gemini'

export interface LeaderboardEntry {
  rank: number
  anonId: string
  location?: string
  signalClass: SignalClass
  snRatio?: number
  messageVolume?: number
  sessionDepth?: number
  promptComplexity?: number
  threadsRecalled?: number
  compositeScore?: number
  acctAge: string
  lastSeen: string
}

export interface ProfileMetric {
  label: string
  score: number
  rank: number
}

export interface UserProfile {
  id: string
  rank: number
  tier: string
  compositeScore: number
  metrics: ProfileMetric[]
}

export interface K2ClassEntry {
  signalClass: SignalClass
  trait: string
  liveCount: number
  maxCount?: number
}

export interface RegionalCount {
  region: string
  count: number
}

export interface CrossPlatformEntry {
  rank: number
  username: string
  platform: Platform
  transmitter: number
  sdrm: number
  signalForce: number
}

export interface SystemMetricRow {
  label: string
  avgUser: number
  avgAI: number
  userValue: number
  unit?: string
}

export interface WrappedStat {
  label: string
  value: string | number
}

export interface ActivityDay {
  date: string
  count: number
}

export interface Badge {
  name: string
  description: string
}

export interface RadarMetric {
  label: string
  value: number
  max?: number
}
