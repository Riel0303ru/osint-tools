// Mock data for demonstration

export const threatTimelineData = [
  { date: 'Mon', threats: 12, scans: 45, critical: 2 },
  { date: 'Tue', threats: 18, scans: 52, critical: 3 },
  { date: 'Wed', threats: 8, scans: 38, critical: 1 },
  { date: 'Thu', threats: 25, scans: 67, critical: 5 },
  { date: 'Fri', threats: 15, scans: 48, critical: 2 },
  { date: 'Sat', threats: 10, scans: 32, critical: 1 },
  { date: 'Sun', threats: 7, scans: 28, critical: 0 },
];

export const moduleUsageData = [
  { module: 'Username', count: 145 },
  { module: 'Email', count: 123 },
  { module: 'Domain', count: 98 },
  { module: 'IP', count: 87 },
  { module: 'Image', count: 65 },
  { module: 'Company', count: 43 },
  { module: 'Darkweb', count: 38 },
  { module: 'Video', count: 22 },
];

export const riskDistributionData = [
  { name: 'Safe', value: 45, color: '#10b981' },
  { name: 'Low', value: 28, color: '#22c55e' },
  { name: 'Medium', value: 18, color: '#f59e0b' },
  { name: 'High', value: 7, color: '#f97316' },
  { name: 'Critical', value: 2, color: '#ef4444' },
];

export const scanPerformanceData = [
  { time: '00:00', speed: 120 },
  { time: '04:00', speed: 100 },
  { time: '08:00', speed: 150 },
  { time: '12:00', speed: 180 },
  { time: '16:00', speed: 160 },
  { time: '20:00', speed: 140 },
];

export const intelligenceCoverageData = [
  { subject: 'OSINT', score: 85 },
  { subject: 'Domain', score: 72 },
  { subject: 'Email', score: 90 },
  { subject: 'Social', score: 65 },
  { subject: 'Darkweb', score: 45 },
  { subject: 'Images', score: 78 },
];

export const recentActivityData = [
  {
    id: '1',
    type: 'scan',
    module: 'username',
    description: 'Username scan completed for target "john_doe"',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    severity: 'low',
    target: 'john_doe',
  },
  {
    id: '2',
    type: 'alert',
    description: 'Critical vulnerability detected in domain analysis',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    severity: 'critical',
    target: 'example.com',
  },
  {
    id: '3',
    type: 'correlation',
    description: 'New correlation found between email and phone records',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    severity: 'medium',
  },
  {
    id: '4',
    type: 'insight',
    module: 'ai',
    description: 'AI identified suspicious pattern in dark web mentions',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    severity: 'high',
  },
  {
    id: '5',
    type: 'scan',
    module: 'domain',
    description: 'Domain reconnaissance initiated for target "target.org"',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    severity: 'low',
    target: 'target.org',
  },
];

export const platformDiscoveryData = [
  { platform: 'GitHub', exists: true, url: 'https://github.com/johndoe', confidence: 95 },
  { platform: 'Twitter', exists: true, url: 'https://twitter.com/johndoe', confidence: 88 },
  { platform: 'LinkedIn', exists: true, url: 'https://linkedin.com/in/johndoe', confidence: 92 },
  { platform: 'Instagram', exists: false, url: '', confidence: 45 },
  { platform: 'Reddit', exists: true, url: 'https://reddit.com/u/johndoe', confidence: 75 },
  { platform: 'Facebook', exists: false, url: '', confidence: 30 },
  { platform: 'Medium', exists: true, url: 'https://medium.com/@johndoe', confidence: 80 },
];

export const breachData = [
  {
    name: 'Collection #1',
    breachDate: '2019-01-01',
    pwnCount: 772904991,
    dataClasses: ['Email addresses', 'Passwords'],
    isVerified: true,
  },
  {
    name: 'LinkedIn',
    breachDate: '2012-06-01',
    pwnCount: 164611949,
    dataClasses: ['Email addresses', 'Passwords'],
    isVerified: true,
  },
  {
    name: 'Adobe',
    breachDate: '2013-10-01',
    pwnCount: 152445165,
    dataClasses: ['Email addresses', 'Passwords', 'Usernames'],
    isVerified: true,
  },
];

export const domainIntelligenceData = {
  domain: 'example.com',
  whois: {
    registrar: 'GoDaddy.com, LLC',
    createdDate: '1995-08-14',
    expiryDate: '2025-08-13',
    nameServers: ['ns1.example.com', 'ns2.example.com'],
    registrant: {
      organization: 'Example Inc.',
      country: 'US',
      state: 'California',
    },
  },
  dns: {
    a: ['93.184.216.34'],
    mx: [{ priority: 10, exchange: 'mail.example.com' }],
    ns: ['ns1.example.com', 'ns2.example.com'],
    txt: ['v=spf1 include:_spf.example.com ~all'],
  },
  ssl: {
    issuer: 'DigiCert Inc',
    validFrom: '2024-01-01',
    validTo: '2025-01-01',
    valid: true,
  },
  technologies: [
    { name: 'React', category: 'Frontend', confidence: 95 },
    { name: 'Node.js', category: 'Backend', confidence: 80 },
    { name: 'AWS', category: 'Cloud', confidence: 90 },
  ],
  subdomains: [
    { subdomain: 'www', ip: '93.184.216.34', status: 'active' },
    { subdomain: 'api', ip: '93.184.216.35', status: 'active' },
    { subdomain: 'mail', ip: '93.184.216.36', status: 'active' },
    { subdomain: 'dev', ip: '', status: 'inactive' },
  ],
};

export const correlationNodes = [
  { id: '1', type: 'username', data: { label: 'johndoe' } },
  { id: '2', type: 'email', data: { label: 'john.doe@email.com' } },
  { id: '3', type: 'phone', data: { label: '+1-555-123-4567' } },
  { id: '4', type: 'domain', data: { label: 'johndoe.com' } },
  { id: '5', type: 'company', data: { label: 'TechCorp Inc' } },
  { id: '6', type: 'ip', data: { label: '192.168.1.1' } },
];

export const correlationEdges = [
  { id: 'e1-2', source: '1', target: '2', type: 'linked' },
  { id: 'e2-3', source: '2', target: '3', type: 'associated' },
  { id: 'e2-4', source: '2', target: '4', type: 'registered' },
  { id: 'e4-5', source: '4', target: '5', type: 'employee' },
  { id: 'e4-6', source: '4', target: '6', type: 'hosted' },
];
