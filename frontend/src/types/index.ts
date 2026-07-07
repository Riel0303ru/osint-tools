// ============================================
// OSINT FUSION - TYPE DEFINITIONS
// ============================================

// Navigation & Layout Types
export type NavItem = {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
  children?: NavItem[];
};

export type SidebarState = {
  collapsed: boolean;
  mobileOpen: boolean;
  activeSection: string | null;
};

// Theme Types
export type ThemeMode = 'dark' | 'light';

export type ThemeState = {
  mode: ThemeMode;
  systemPreference: ThemeMode;
};

// Intelligence Module Types
export type IntelligenceModule =
  | 'username'
  | 'email'
  | 'domain'
  | 'ip'
  | 'phone'
  | 'company'
  | 'image'
  | 'document'
  | 'video'
  | 'darkweb'
  | 'correlation'
  | 'ai';

// Risk Level Types
export type RiskLevel = 'safe' | 'low' | 'medium' | 'high' | 'critical' | 'unknown';

export type RiskScore = {
  level: RiskLevel;
  score: number; // 0-100
  confidence: number; // 0-100
  factors: string[];
};

// Scan Types
export type ScanStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

export type ScanType = IntelligenceModule;

export type Scan = {
  id: string;
  type: ScanType;
  target: string;
  status: ScanStatus;
  progress: number;
  startTime: string;
  endTime?: string;
  result?: ScanResult;
  error?: string;
};

export type ScanResult = {
  id: string;
  scanId: string;
  type: ScanType;
  target: string;
  timestamp: string;
  data: Record<string, unknown>;
  riskScore: RiskScore;
  correlations: Correlation[];
  aiInsights?: AIInsight[];
};

// Username Intelligence Types
export type UsernameResult = {
  platforms: PlatformDiscovery[];
  correlations: IdentityCorrelation[];
  confidence: number;
  suggestions: string[];
  riskScore: RiskScore;
};

export type PlatformDiscovery = {
  platform: string;
  url: string;
  exists: boolean;
  username: string;
  profileUrl?: string;
  avatar?: string;
  bio?: string;
  joinDate?: string;
  lastActive?: string;
  followers?: number;
  following?: number;
  confidence: number;
};

export type IdentityCorrelation = {
  type: 'username' | 'email' | 'phone' | 'name' | 'location';
  value: string;
  confidence: number;
  source: string;
};

// Email Intelligence Types
export type EmailResult = {
  email: string;
  valid: boolean;
  breaches: BreachRecord[];
  reputation: EmailReputation;
  gravatar?: GravatarInfo;
  mxRecords: MXRecord[];
  riskScore: RiskScore;
};

export type BreachRecord = {
  name: string;
  domain: string;
  breachDate: string;
  addedDate: string;
  modifiedDate: string;
  pwnCount: number;
  description: string;
  dataClasses: string[];
  isVerified: boolean;
  isFabricated: boolean;
  isSensitive: boolean;
  isRetired: boolean;
  isSpamList: boolean;
};

export type EmailReputation = {
  score: number;
  deliverable: boolean;
  disposable: boolean;
  spam: boolean;
  catchAll: boolean;
  reason?: string;
};

export type GravatarInfo = {
  exists: boolean;
  imageUrl?: string;
  profileUrl?: string;
  displayName?: string;
  location?: string;
};

export type MXRecord = {
  priority: number;
  exchange: string;
};

// Domain Intelligence Types
export type DomainResult = {
  domain: string;
  whois: WhoisData;
  dns: DNSRecords;
  ssl?: SSLInfo;
  headers: SecurityHeaders;
  subdomains: Subdomain[];
  technologies: Technology[];
  virustotal?: VirusTotalResult;
  shodan?: ShodanResult;
  wayback?: WaybackSnapshot[];
  riskScore: RiskScore;
};

export type WhoisData = {
  domainName: string;
  registrar: string;
  createdDate: string;
  updatedDate: string;
  expiryDate: string;
  status: string[];
  nameServers: string[];
  registrant: RegistrantInfo;
  dnssec: boolean;
};

export type RegistrantInfo = {
  name?: string;
  organization?: string;
  street?: string;
  city?: string;
  state?: string;
  country?: string;
  postalCode?: string;
  email?: string;
  phone?: string;
};

export type DNSRecords = {
  a: string[];
  aaaa: string[];
  mx: MXRecord[];
  ns: string[];
  txt: string[];
  cname: string[];
  srv: SRVRecord[];
  soa?: SOARecord;
};

export type SRVRecord = {
  priority: number;
  weight: number;
  port: number;
  target: string;
};

export type SOARecord = {
  mname: string;
  rname: string;
  serial: number;
  refresh: number;
  retry: number;
  expire: number;
  minimum: number;
};

export type SSLInfo = {
  issuer: string;
  subject: string;
  validFrom: string;
  validTo: string;
  fingerprint: string;
  protocol: string;
  keySize: number;
  valid: boolean;
};

export type SecurityHeaders = {
  headers: Record<string, string>;
  score: number;
  missing: string[];
  warnings: string[];
};

export type Subdomain = {
  subdomain: string;
  ip?: string;
  ports?: number[];
  services?: string[];
  status: 'active' | 'inactive' | 'unknown';
};

export type Technology = {
  name: string;
  category: string;
  version?: string;
  confidence: number;
};

export type VirusTotalResult = {
  detectionRatio: string;
  positives: number;
  total: number;
  scanDate: string;
  permalink: string;
  verdict: 'clean' | 'suspicious' | 'malicious';
};

export type ShodanResult = {
  ip: string;
  ports: number[];
  hostnames: string[];
  country: string;
  city: string;
  org: string;
  isp: string;
  services: ShodanService[];
};

export type ShodanService = {
  port: number;
  protocol: string;
  product?: string;
  version?: string;
  banner?: string;
};

export type WaybackSnapshot = {
  url: string;
  timestamp: string;
  status: number;
  mime: string;
};

// IP Intelligence Types
export type IPResult = {
  ip: string;
  geolocation: IPLocation;
  asn: ASNInfo;
  abuse?: AbuseInfo;
  reputation: IPReputation;
  services: IPService[];
  riskScore: RiskScore;
};

export type IPLocation = {
  country: string;
  countryCode: string;
  region: string;
  city: string;
  latitude: number;
  longitude: number;
  timezone: string;
  isp: string;
  organization: string;
};

export type ASNInfo = {
  asn: string;
  name: string;
  country: string;
  route: string;
  type: 'isp' | 'hosting' | 'business' | 'education' | 'government';
};

export type AbuseInfo = {
  email: string;
  network: string;
  country: string;
  address: string;
  phone?: string;
};

export type IPReputation = {
  score: number;
  isProxy: boolean;
  isVPN: boolean;
  isTor: boolean;
  isHosting: boolean;
  isBlacklisted: boolean;
  blacklists: string[];
};

export type IPService = {
  port: number;
  protocol: string;
  service: string;
  banner?: string;
};

// Phone Intelligence Types
export type PhoneResult = {
  number: string;
  valid: boolean;
  formatted: string;
  type: 'mobile' | 'landline' | 'voip' | 'unknown';
  carrier: string;
  location: PhoneLocation;
  whatsapp: boolean;
  telegram: boolean;
  breaches: BreachRecord[];
  riskScore: RiskScore;
};

export type PhoneLocation = {
  country: string;
  countryCode: string;
  region: string;
  timezone: string;
};

// Company Intelligence Types
export type CompanyResult = {
  name: string;
  domains: string[];
  infrastructure: CompanyInfrastructure;
  saas: SaaSDetection[];
  employees: number;
  industry: string;
  founded?: string;
  headquarters?: string;
  socialProfiles: SocialProfile[];
  security: CompanySecurity;
  riskScore: RiskScore;
};

export type CompanyInfrastructure = {
  domains: number;
  subdomains: number;
  ips: number;
  cloudProviders: string[];
  technologies: Technology[];
};

export type SaaSDetection = {
  service: string;
  domain: string;
  category: string;
  verified: boolean;
};

export type SocialProfile = {
  platform: string;
  url: string;
  followers?: number;
  verified: boolean;
};

export type CompanySecurity = {
  sslGrade: string;
  securityHeaders: number;
  vulnerabilities: number;
  score: number;
};

// Image Intelligence Types
export type ImageResult = {
  url?: string;
  hash: ImageHash;
  metadata: ImageMetadata;
  exif?: EXIFData;
  analysis: ImageAnalysis;
  reverseSearch: ReverseSearchResult[];
  riskScore: RiskScore;
};

export type ImageHash = {
  md5: string;
  sha1: string;
  sha256: string;
  perceptual: string;
  average: string;
  difference: string;
};

export type ImageMetadata = {
  width: number;
  height: number;
  format: string;
  size: number;
  bitDepth: number;
  colorSpace: string;
  alpha: boolean;
};

export type EXIFData = {
  make?: string;
  model?: string;
  dateTime?: string;
  exposureTime?: string;
  aperture?: string;
  iso?: number;
  focalLength?: string;
  gps?: GPSData;
  software?: string;
  orientation?: number;
};

export type GPSData = {
  latitude: number;
  longitude: number;
  altitude?: number;
  address?: string;
  country?: string;
  city?: string;
};

export type ImageAnalysis = {
  ocr: OCRResult[];
  faces: FaceDetection[];
  objects: ObjectDetection[];
  steganography?: SteganographyResult;
};

export type OCRResult = {
  text: string;
  confidence: number;
  boundingBox: BoundingBox;
  language: string;
};

export type BoundingBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type FaceDetection = {
  id: string;
  boundingBox: BoundingBox;
  confidence: number;
  age?: { min: number; max: number };
  gender?: string;
  emotions?: Record<string, number>;
  landmarks?: FaceLandmarks[];
};

export type FaceLandmarks = {
  type: string;
  x: number;
  y: number;
};

export type ObjectDetection = {
  label: string;
  confidence: number;
  boundingBox: BoundingBox;
};

export type SteganographyResult = {
  detected: boolean;
  method?: string;
  hiddenData?: string;
  confidence: number;
};

export type ReverseSearchResult = {
  engine: string;
  url: string;
  matches: number;
  topResults: ReverseSearchMatch[];
};

export type ReverseSearchMatch = {
  url: string;
  title?: string;
  source?: string;
  similarity: number;
};

// Document Intelligence Types
export type DocumentResult = {
  filename: string;
  type: string;
  size: number;
  hash: DocumentHash;
  metadata: DocumentMetadata;
  content: DocumentContent;
  sensitiveData: SensitiveData[];
  analysis: DocumentAnalysis;
  riskScore: RiskScore;
};

export type DocumentHash = {
  md5: string;
  sha1: string;
  sha256: string;
};

export type DocumentMetadata = {
  author?: string;
  title?: string;
  subject?: string;
  keywords?: string[];
  creator?: string;
  producer?: string;
  creationDate?: string;
  modificationDate?: string;
  pageCount?: number;
  wordCount?: number;
};

export type DocumentContent = {
  text: string;
  pages: DocumentPage[];
  images: ImageResult[];
  links: DocumentLink[];
};

export type DocumentPage = {
  number: number;
  text: string;
  images: ImageResult[];
};

export type DocumentLink = {
  url: string;
  text?: string;
  page?: number;
};

export type SensitiveData = {
  type: 'email' | 'phone' | 'ssn' | 'credit_card' | 'api_key' | 'password' | 'ip' | 'url';
  value: string;
  location: string;
  context: string;
  risk: RiskLevel;
};

export type DocumentAnalysis = {
  ocr: OCRResult[];
  ai?: AIInsight;
  language: string;
  topics: string[];
  sentiment?: {
    score: number;
    label: 'positive' | 'negative' | 'neutral';
  };
};

// Video Intelligence Types
export type VideoResult = {
  url?: string;
  filename?: string;
  metadata: VideoMetadata;
  frames: VideoFrame[];
  audio: AudioAnalysis;
  analysis: VideoAnalysis;
  riskScore: RiskScore;
};

export type VideoMetadata = {
  duration: number;
  width: number;
  height: number;
  codec: string;
  bitrate: number;
  fps: number;
  size: number;
  hash: string;
};

export type VideoFrame = {
  timestamp: number;
  image: ImageResult;
  detections: FrameDetection[];
};

export type FrameDetection = {
  type: 'face' | 'object' | 'text' | 'landmark';
  data: unknown;
  confidence: number;
};

export type AudioAnalysis = {
  transcript?: string;
  language?: string;
  speakers?: number;
  sentiment?: {
    score: number;
    label: 'positive' | 'negative' | 'neutral';
  };
};

export type VideoAnalysis = {
  timeline: VideoTimelineEvent[];
  locations: GPSData[];
  objects: ObjectDetection[];
  faces: FaceDetection[];
  text: OCRResult[];
  ai?: AIInsight;
};

export type VideoTimelineEvent = {
  timestamp: number;
  type: string;
  description: string;
  confidence: number;
};

// Dark Web Intelligence Types
export type DarkWebResult = {
  query: string;
  breaches: BreachRecord[];
  exposedData: ExposedData[];
  mentions: DarkWebMention[];
  markets: DarkWebMarket[];
  riskScore: RiskScore;
};

export type ExposedData = {
  type: string;
  value: string;
  source: string;
  dateExposed: string;
  context?: string;
};

export type DarkWebMention = {
  platform: string;
  url?: string;
  content: string;
  date: string;
  author?: string;
  sentiment: 'positive' | 'negative' | 'neutral';
};

export type DarkWebMarket = {
  name: string;
  url?: string;
  listings: number;
  relevantListings: DarkWebListing[];
};

export type DarkWebListing = {
  title: string;
  description: string;
  price?: string;
  seller?: string;
  date: string;
  category?: string;
};

// Correlation Engine Types
export type Correlation = {
  id: string;
  type: 'identity' | 'infrastructure' | 'behavior' | 'timeline';
  entities: Entity[];
  relationship: string;
  confidence: number;
  evidence: CorrelationEvidence[];
  riskScore: RiskScore;
};

export type Entity = {
  id: string;
  type: 'username' | 'email' | 'phone' | 'domain' | 'ip' | 'company' | 'person' | 'location' | 'image' | 'document';
  value: string;
  source: string;
  timestamp: string;
  confidence: number;
  properties?: Record<string, unknown>;
};

export type CorrelationEvidence = {
  source: string;
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
};

// Graph Types
export type GraphNode = {
  id: string;
  type: EntityType;
  data: Record<string, unknown>;
  position?: { x: number; y: number };
  style?: NodeStyle;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  animated?: boolean;
  style?: EdgeStyle;
};

export type NodeStyle = {
  color?: string;
  size?: number;
  icon?: string;
  glow?: boolean;
};

export type EdgeStyle = {
  color?: string;
  width?: number;
  dashed?: boolean;
};

export type EntityType = 'username' | 'email' | 'phone' | 'domain' | 'ip' | 'company' | 'person' | 'location';

// AI Types
export type AIInsight = {
  id: string;
  type: 'summary' | 'recommendation' | 'risk_assessment' | 'correlation' | 'threat';
  title: string;
  content: string;
  confidence: number;
  priority: 'low' | 'medium' | 'high';
  timestamp: string;
  actions?: AIAction[];
  relatedEntities?: string[];
};

export type AIAction = {
  label: string;
  type: string;
  params: Record<string, unknown>;
};

// Report Types
export type Report = {
  id: string;
  title: string;
  type: 'investigation' | 'scan' | 'threat' | 'summary';
  status: 'draft' | 'generating' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
  author?: string;
  targets: string[];
  modules: IntelligenceModule[];
  summary: string;
  sections: ReportSection[];
  riskScore: RiskScore;
  format: 'pdf' | 'html' | 'json';
};

export type ReportSection = {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'chart' | 'table' | 'timeline' | 'graph';
  data?: unknown;
};

// Dashboard Types
export type DashboardStats = {
  totalScans: number;
  activeInvestigations: number;
  threatsDetected: number;
  riskScore: number;
  moduleUsage: ModuleUsage[];
  recentActivity: ActivityEvent[];
  threatTimeline:威胁Timeline[];
};

export type ModuleUsage = {
  module: IntelligenceModule;
  count: number;
  avgTime: number;
  successRate: number;
};

export type ActivityEvent = {
  id: string;
  type: 'scan' | 'correlation' | 'insight' | 'report' | 'alert';
  module?: IntelligenceModule;
  description: string;
  timestamp: string;
  severity: RiskLevel;
  target?: string;
};

export type 威胁Timeline = {
  date: string;
  count: number;
  severity: RiskLevel;
};

// Notification Types
export type Notification = {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'alert';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: NotificationAction[];
};

export type NotificationAction = {
  label: string;
  action: string;
};

// API Response Types
export type APIResponse<T> = {
  success: boolean;
  data?: T;
  error?: APIError;
  meta?: {
    timestamp: string;
    requestId: string;
  };
};

export type APIError = {
  code: string;
  message: string;
  details?: Record<string, unknown>;
};
