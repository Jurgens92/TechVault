/**
 * PDF Icon Assets
 * High-quality SVG icons converted to base64 data URLs for use in PDF exports
 * These icons are designed to render beautifully in jsPDF exports
 */

// SVG icon definitions - crisp vector graphics
export const SVG_ICONS = {
  // Globe/Internet icon
  internet: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    <path d="M2 12h20"/>
  </svg>`,

  // Shield/Firewall icon
  firewall: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>`,

  // Router icon
  router: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="8" x="2" y="14" rx="2"/>
    <path d="M6.01 18H6"/>
    <path d="M10.01 18H10"/>
    <path d="M15 10v4"/>
    <path d="M17.84 7.17a4 4 0 0 0-5.66 0"/>
    <path d="M20.66 4.34a8 8 0 0 0-11.31 0"/>
  </svg>`,

  // Network Switch icon
  switch: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="8" x="2" y="8" rx="2" ry="2"/>
    <path d="M6 8v-2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2"/>
    <path d="M6 16v2"/>
    <path d="M18 16v2"/>
    <path d="M12 16v2"/>
    <circle cx="6" cy="12" r="1" fill="#22c55e"/>
    <circle cx="10" cy="12" r="1" fill="#22c55e"/>
    <circle cx="14" cy="12" r="1" fill="#22c55e"/>
    <circle cx="18" cy="12" r="1" fill="#22c55e"/>
  </svg>`,

  // WiFi icon
  wifi: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 20h.01"/>
    <path d="M2 8.82a15 15 0 0 1 20 0"/>
    <path d="M5 12.859a10 10 0 0 1 14 0"/>
    <path d="M8.5 16.429a5 5 0 0 1 7 0"/>
  </svg>`,

  // Server icon
  server: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="8" x="2" y="2" rx="2" ry="2"/>
    <rect width="20" height="8" x="2" y="14" rx="2" ry="2"/>
    <line x1="6" x2="6.01" y1="6" y2="6"/>
    <line x1="6" x2="6.01" y1="18" y2="18"/>
    <line x1="10" x2="10.01" y1="6" y2="6"/>
    <line x1="10" x2="10.01" y1="18" y2="18"/>
  </svg>`,

  // Desktop/Monitor icon
  desktop: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="14" x="2" y="3" rx="2"/>
    <line x1="8" x2="16" y1="21" y2="21"/>
    <line x1="12" x2="12" y1="17" y2="21"/>
  </svg>`,

  // Laptop icon
  laptop: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16"/>
  </svg>`,

  // Workstation icon (CPU)
  workstation: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="4" y="4" width="16" height="16" rx="2"/>
    <rect x="9" y="9" width="6" height="6"/>
    <path d="M9 2v2"/>
    <path d="M15 2v2"/>
    <path d="M9 20v2"/>
    <path d="M15 20v2"/>
    <path d="M2 9h2"/>
    <path d="M2 15h2"/>
    <path d="M20 9h2"/>
    <path d="M20 15h2"/>
  </svg>`,

  // Printer icon
  printer: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
    <path d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6"/>
    <rect width="12" height="8" x="6" y="14" rx="1"/>
  </svg>`,

  // Scanner icon
  scanner: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
    <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
    <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
    <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
    <path d="M7 12h10"/>
  </svg>`,

  // Database/Backup icon
  backup: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3"/>
    <path d="M3 5V19A9 3 0 0 0 21 19V5"/>
    <path d="M3 12A9 3 0 0 0 21 12"/>
  </svg>`,

  // Hard Drive icon
  hardDrive: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="22" x2="2" y1="12" y2="12"/>
    <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>
    <line x1="6" x2="6.01" y1="16" y2="16"/>
    <line x1="10" x2="10.01" y1="16" y2="16"/>
  </svg>`,

  // Software/Package icon
  software: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="m7.5 4.27 9 5.15"/>
    <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
    <path d="m3.3 7 8.7 5 8.7-5"/>
    <path d="M12 22V12"/>
  </svg>`,

  // Phone/VoIP icon
  voip: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
  </svg>`,

  // Headset (for Teams/VoIP)
  headset: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 11h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5Zm0 0a9 9 0 1 1 18 0m0 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3Z"/>
    <path d="M21 16v2a4 4 0 0 1-4 4h-5"/>
  </svg>`,

  // UPS/Power icon
  ups: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#84cc16" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect width="18" height="12" x="3" y="8" rx="2"/>
    <path d="M7 8V6a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2"/>
    <path d="M13 12v4"/>
    <path d="M11 14h4"/>
  </svg>`,

  // Camera icon
  camera: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
    <circle cx="12" cy="13" r="3"/>
  </svg>`,

  // Generic peripheral icon
  peripheral: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect width="14" height="20" x="5" y="2" rx="2" ry="2"/>
    <path d="M12 18h.01"/>
    <path d="M8 6h8"/>
    <path d="M8 10h8"/>
    <path d="M8 14h8"/>
  </svg>`,
};

// Color-filled icon variations for badge backgrounds
export const FILLED_ICONS = {
  internetFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    <path d="M2 12h20"/>
  </svg>`,

  firewallFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>`,

  switchFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#dcfce7" stroke="#22c55e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="8" x="2" y="8" rx="2" ry="2"/>
    <path d="M6 8v-2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2"/>
    <path d="M6 16v2"/>
    <path d="M18 16v2"/>
    <path d="M12 16v2"/>
    <circle cx="6" cy="12" r="1" fill="#22c55e"/>
    <circle cx="10" cy="12" r="1" fill="#22c55e"/>
    <circle cx="14" cy="12" r="1" fill="#22c55e"/>
    <circle cx="18" cy="12" r="1" fill="#22c55e"/>
  </svg>`,

  wifiFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#f3e8ff" stroke="#a855f7" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="20" r="2" fill="#a855f7"/>
    <path d="M2 8.82a15 15 0 0 1 20 0"/>
    <path d="M5 12.859a10 10 0 0 1 14 0"/>
    <path d="M8.5 16.429a5 5 0 0 1 7 0"/>
  </svg>`,

  serverFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#e0e7ff" stroke="#6366f1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="8" x="2" y="2" rx="2" ry="2"/>
    <rect width="20" height="8" x="2" y="14" rx="2" ry="2"/>
    <circle cx="6" cy="6" r="1" fill="#6366f1"/>
    <circle cx="6" cy="18" r="1" fill="#6366f1"/>
    <circle cx="10" cy="6" r="1" fill="#6366f1"/>
    <circle cx="10" cy="18" r="1" fill="#6366f1"/>
  </svg>`,

  backupFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3"/>
    <path d="M3 5V19A9 3 0 0 0 21 19V5"/>
    <path d="M3 12A9 3 0 0 0 21 12"/>
  </svg>`,

  softwareFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#fce7f3" stroke="#ec4899" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="m7.5 4.27 9 5.15"/>
    <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
    <path d="m3.3 7 8.7 5 8.7-5"/>
    <path d="M12 22V12"/>
  </svg>`,

  voipFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#cffafe" stroke="#06b6d4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
  </svg>`,

  desktopFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#e0f2fe" stroke="#0ea5e9" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="14" x="2" y="3" rx="2"/>
    <line x1="8" x2="16" y1="21" y2="21"/>
    <line x1="12" x2="12" y1="17" y2="21"/>
  </svg>`,

  laptopFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#ccfbf1" stroke="#14b8a6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16"/>
  </svg>`,

  printerFilled: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
    <path d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6"/>
    <rect width="12" height="8" x="6" y="14" rx="1"/>
  </svg>`,
};

/**
 * Icon cache for performance - stores converted PNG data URLs
 */
const iconCache: Map<string, string> = new Map();

/**
 * Convert an SVG string to a PNG data URL using canvas
 * This creates a high-quality rasterized image suitable for jsPDF
 */
export async function svgToPngDataUrl(
  svgString: string,
  width: number = 64,
  height: number = 64
): Promise<string> {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    canvas.width = width * 2; // 2x for retina quality
    canvas.height = height * 2;
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      reject(new Error('Could not get canvas context'));
      return;
    }

    const img = new Image();
    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      const pngDataUrl = canvas.toDataURL('image/png');
      resolve(pngDataUrl);
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load SVG'));
    };

    img.src = url;
  });
}

/**
 * Get a cached PNG icon, converting from SVG if necessary
 */
export async function getPngIcon(
  iconName: keyof typeof SVG_ICONS | keyof typeof FILLED_ICONS,
  width: number = 64,
  height: number = 64,
  filled: boolean = false
): Promise<string> {
  const cacheKey = `${iconName}-${width}-${height}-${filled}`;

  if (iconCache.has(cacheKey)) {
    return iconCache.get(cacheKey)!;
  }

  const icons = filled ? FILLED_ICONS : SVG_ICONS;
  const svgString = (icons as Record<string, string>)[iconName] || SVG_ICONS.peripheral;

  const pngDataUrl = await svgToPngDataUrl(svgString, width, height);
  iconCache.set(cacheKey, pngDataUrl);

  return pngDataUrl;
}

/**
 * Pre-load all icons for faster PDF generation
 */
export async function preloadAllIcons(): Promise<Map<string, string>> {
  const filledIconKeys = Object.keys(FILLED_ICONS) as (keyof typeof FILLED_ICONS)[];

  const promises = filledIconKeys.map(async (key) => {
    const dataUrl = await getPngIcon(key as any, 64, 64, true);
    return [key, dataUrl] as [string, string];
  });

  const results = await Promise.all(promises);
  const iconMap = new Map(results);

  return iconMap;
}

/**
 * Get the appropriate icon name based on device type
 */
export function getIconForDeviceType(
  deviceType: string,
  category: 'network' | 'endpoint' | 'server' | 'peripheral' | 'backup' | 'software' | 'voip'
): keyof typeof FILLED_ICONS {
  const typeMap: Record<string, keyof typeof FILLED_ICONS> = {
    // Network devices
    'firewall': 'firewallFilled',
    'firewall_router': 'firewallFilled',
    'router': 'firewallFilled',
    'switch': 'switchFilled',
    'wifi': 'wifiFilled',
    'access_point': 'wifiFilled',

    // Endpoints
    'desktop': 'desktopFilled',
    'laptop': 'laptopFilled',
    'workstation': 'desktopFilled',

    // Servers
    'physical': 'serverFilled',
    'virtual': 'serverFilled',

    // Peripherals
    'printer': 'printerFilled',
    'scanner': 'printerFilled',
    'mfp': 'printerFilled',
    'ups': 'printerFilled',
    'camera': 'printerFilled',

    // VoIP
    'teams': 'voipFilled',
    '3cx': 'voipFilled',
    'yeastar': 'voipFilled',
  };

  // Check for direct match first
  const lowerType = deviceType.toLowerCase();
  if (typeMap[lowerType]) {
    return typeMap[lowerType];
  }

  // Default icons by category
  const categoryDefaults: Record<string, keyof typeof FILLED_ICONS> = {
    'network': 'switchFilled',
    'endpoint': 'desktopFilled',
    'server': 'serverFilled',
    'peripheral': 'printerFilled',
    'backup': 'backupFilled',
    'software': 'softwareFilled',
    'voip': 'voipFilled',
  };

  return categoryDefaults[category] || 'printerFilled';
}
