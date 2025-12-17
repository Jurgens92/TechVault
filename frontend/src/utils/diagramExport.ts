import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import type { DiagramData } from '@/types/core';

export type ExportFormat = 'png' | 'json' | 'svg' | 'pdf' | 'print';

/**
 * Export diagram as PNG image
 */
export async function exportAsPNG(elementId: string, filename: string): Promise<void> {
  const element = document.getElementById(elementId);
  if (!element) {
    throw new Error('Diagram element not found');
  }

  try {
    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#ffffff',
      logging: false,
      useCORS: true,
      allowTaint: true,
    });

    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    }, 'image/png');
  } catch (error) {
    throw new Error('Failed to export diagram as PNG');
  }
}

/**
 * Export diagram data as JSON
 */
export function exportAsJSON(data: DiagramData, orgName: string): void {
  const exportData = {
    organization: orgName,
    exportDate: new Date().toISOString(),
    data: {
      network_devices: data.network_devices,
      endpoint_users: data.endpoint_users,
      servers: data.servers,
      peripherals: data.peripherals,
      backups: data.backups,
      software: data.software,
      voip: data.voip,
    },
  };

  const jsonString = JSON.stringify(exportData, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${sanitizeFilename(orgName)}_diagram_data.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Export diagram as SVG
 */
export function exportAsSVG(data: DiagramData, orgName: string): void {
  const svg = generateSVGDiagram(data, orgName);
  const blob = new Blob([svg], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${sanitizeFilename(orgName)}_diagram.svg`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Export diagram as professional PDF document
 * Matches the layout of Diagram.tsx for print with a light, printable theme
 * Uses a single continuous page (no pagination) for cleaner output
 */
export async function exportAsPDF(
  data: DiagramData,
  orgName: string,
  elementId?: string
): Promise<void> {
  // Calculate total height needed for content
  const estimatedHeight = calculateTotalHeight(data);

  // Create PDF with custom height to fit all content on one page
  const pdf = new jsPDF({
    orientation: 'landscape',
    unit: 'mm',
    format: [297, Math.max(210, estimatedHeight + 40)], // A4 width, dynamic height
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 15;
  const contentWidth = pageWidth - margin * 2;
  let yPosition = margin;

  // Colors - Light theme matching web view
  const primaryColor: [number, number, number] = [59, 130, 246]; // Blue-500
  const darkColor: [number, number, number] = [15, 23, 42]; // Slate-900
  const textColor: [number, number, number] = [30, 41, 59]; // Slate-800
  const mutedColor: [number, number, number] = [100, 116, 139]; // Slate-500
  const borderColor: [number, number, number] = [226, 232, 240]; // Slate-200
  const cardBgColor: [number, number, number] = [255, 255, 255]; // White
  const accentBgColor: [number, number, number] = [248, 250, 252]; // Slate-50

  // Semantic colors
  const redColor: [number, number, number] = [239, 68, 68]; // Red-500
  const redBgColor: [number, number, number] = [254, 242, 242]; // Red-50
  const greenColor: [number, number, number] = [34, 197, 94]; // Green-500
  const greenBgColor: [number, number, number] = [240, 253, 244]; // Green-50
  const purpleColor: [number, number, number] = [168, 85, 247]; // Purple-500
  const purpleBgColor: [number, number, number] = [250, 245, 255]; // Purple-50
  const blueBgColor: [number, number, number] = [239, 246, 255]; // Blue-50
  const yellowColor: [number, number, number] = [234, 179, 8]; // Yellow-500
  const yellowBgColor: [number, number, number] = [254, 252, 232]; // Yellow-50

  // Helper to estimate total document height
  function calculateTotalHeight(data: DiagramData): number {
    let height = 50; // Title section

    // Network section
    if (data.network_devices.length > 0) {
      height += 50; // Internet node + section header
      const firewalls = data.network_devices.filter(d => d.device_type === 'firewall' || d.device_type === 'firewall_router' || d.device_type === 'router');
      const switches = data.network_devices.filter(d => d.device_type === 'switch');
      const wifiDevices = data.network_devices.filter(d => d.device_type === 'wifi');
      if (firewalls.length > 0) height += 60;
      if (switches.length > 0) height += 50;
      if (wifiDevices.length > 0) height += 40;
    }

    // Endpoints section
    if (data.endpoint_users.length > 0) {
      const maxRows = Math.max(
        data.endpoint_users.filter(e => e.device_type === 'desktop').length,
        data.endpoint_users.filter(e => e.device_type === 'laptop').length,
        data.endpoint_users.filter(e => e.device_type === 'workstation').length
      );
      height += 30 + (maxRows * 40);
    }

    // Servers section
    if (data.servers.length > 0) {
      const rows = Math.ceil(data.servers.length / 3);
      height += 30 + (rows * 55);
    }

    // Peripherals section
    if (data.peripherals.length > 0) {
      const rows = Math.ceil(data.peripherals.length / 4);
      height += 30 + (rows * 40);
    }

    // Backups section
    if (data.backups.length > 0) {
      const rows = Math.ceil(data.backups.length / 2);
      height += 30 + (rows * 60);
    }

    // Software section
    if (data.software.length > 0) {
      const rows = Math.ceil(data.software.length / 3);
      height += 30 + (rows * 45);
    }

    // VoIP section
    if (data.voip.length > 0) {
      const rows = Math.ceil(data.voip.length / 3);
      height += 30 + (rows * 45);
    }

    return height;
  }

  // Helper function to add footer at the end
  const addFooter = (): void => {
    pdf.setDrawColor(...borderColor);
    pdf.setLineWidth(0.3);
    pdf.line(margin, yPosition + 10, pageWidth - margin, yPosition + 10);

    pdf.setFontSize(7);
    pdf.setTextColor(...mutedColor);
    pdf.text(
      `Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}`,
      margin,
      yPosition + 16
    );
    pdf.text('TechVault • IT Infrastructure Diagram', pageWidth - margin, yPosition + 16, { align: 'right' });
  };

  // Helper to draw section header matching web view style
  const drawSectionHeader = (title: string, iconColor: [number, number, number], iconBgColor: [number, number, number]): void => {
    // Section container with border (like web view cards)
    pdf.setDrawColor(...borderColor);
    pdf.setLineWidth(0.4);
    pdf.setFillColor(...cardBgColor);

    // Icon background circle
    const iconSize = 8;
    pdf.setFillColor(...iconBgColor);
    pdf.roundedRect(margin, yPosition, iconSize + 4, iconSize + 4, 2, 2, 'F');

    // Draw a simple icon indicator (circle)
    pdf.setFillColor(...iconColor);
    pdf.circle(margin + (iconSize + 4) / 2, yPosition + (iconSize + 4) / 2, 2, 'F');

    // Section title
    pdf.setTextColor(...darkColor);
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'bold');
    pdf.text(title, margin + iconSize + 8, yPosition + 8);

    yPosition += 16;
  };

  // Helper to draw a badge (like web view)
  const drawBadge = (x: number, y: number, text: string, bgColor: [number, number, number], textColorArr: [number, number, number]): void => {
    pdf.setFontSize(6);
    const badgeWidth = pdf.getTextWidth(text) + 6;
    const badgeHeight = 5;

    pdf.setFillColor(...bgColor);
    pdf.roundedRect(x, y - badgeHeight + 1, badgeWidth, badgeHeight, 1.5, 1.5, 'F');
    pdf.setTextColor(...textColorArr);
    pdf.setFont('helvetica', 'bold');
    pdf.text(text, x + 3, y - 0.5);
  };

  // Helper to truncate text
  const truncateText = (text: string, maxWidth: number): string => {
    if (!text) return '';
    if (pdf.getTextWidth(text) <= maxWidth) return text;
    while (pdf.getTextWidth(text + '...') > maxWidth && text.length > 0) {
      text = text.slice(0, -1);
    }
    return text + '...';
  };

  // Helper to draw a card with icon (matching web view style)
  const drawCard = (
    x: number,
    y: number,
    width: number,
    height: number
  ): void => {
    // Card shadow effect (subtle)
    pdf.setFillColor(240, 240, 240);
    pdf.roundedRect(x + 0.5, y + 0.5, width, height, 3, 3, 'F');

    // Card background
    pdf.setFillColor(...cardBgColor);
    pdf.setDrawColor(...borderColor);
    pdf.setLineWidth(0.4);
    pdf.roundedRect(x, y, width, height, 3, 3, 'FD');
  };

  // Helper to draw icon background (like web view bg-color/10)
  const drawIconBg = (
    x: number,
    y: number,
    size: number,
    bgColor: [number, number, number]
  ): void => {
    pdf.setFillColor(...bgColor);
    pdf.roundedRect(x, y, size, size, 2, 2, 'F');
  };

  // Add first page header
  addHeader();

  // Title Section
  pdf.setTextColor(...darkColor);
  pdf.setFontSize(20);
  pdf.setFont('helvetica', 'bold');
  pdf.text(orgName, margin, yPosition + 6);
  yPosition += 10;

  pdf.setFontSize(11);
  pdf.setTextColor(...mutedColor);
  pdf.setFont('helvetica', 'normal');
  pdf.text('IT Infrastructure Diagram', margin, yPosition + 3);
  yPosition += 12;

  // ==================== NETWORK INFRASTRUCTURE ====================
  // Matches the hierarchical layout in Diagram.tsx with light theme
  if (data.network_devices.length > 0) {
    // Section header with icon
    drawSectionHeader('Network Infrastructure', primaryColor, blueBgColor);

    const firewalls = data.network_devices.filter(d =>
      d.device_type === 'firewall' || d.device_type === 'firewall_router' || d.device_type === 'router'
    );
    const switches = data.network_devices.filter(d => d.device_type === 'switch');
    const wifiDevices = data.network_devices.filter(d => d.device_type === 'wifi');

    const centerX = pageWidth / 2;

    // Internet node - gradient-like circle (matching web view)
    const internetRadius = 12;
    // Outer gradient effect
    pdf.setFillColor(147, 197, 253); // Blue-300
    pdf.circle(centerX, yPosition + internetRadius, internetRadius, 'F');
    // Inner circle
    pdf.setFillColor(...primaryColor);
    pdf.circle(centerX, yPosition + internetRadius, internetRadius - 2, 'F');
    // Globe icon (simplified)
    pdf.setDrawColor(255, 255, 255);
    pdf.setLineWidth(0.8);
    pdf.circle(centerX, yPosition + internetRadius, 5, 'S');
    pdf.line(centerX - 6, yPosition + internetRadius, centerX + 6, yPosition + internetRadius);
    pdf.line(centerX, yPosition + internetRadius - 6, centerX, yPosition + internetRadius + 6);
    // Curved lines for globe
    pdf.ellipse(centerX, yPosition + internetRadius, 3, 6, 'S');

    pdf.setTextColor(...textColor);
    pdf.setFontSize(9);
    pdf.setFont('helvetica', 'medium');
    pdf.text('Internet', centerX, yPosition + internetRadius * 2 + 5, { align: 'center' });
    yPosition += internetRadius * 2 + 10;

    // Connection line
    pdf.setDrawColor(...borderColor);
    pdf.setLineWidth(0.8);
    pdf.line(centerX, yPosition, centerX, yPosition + 8);
    yPosition += 10;

    // Firewalls/Routers
    if (firewalls.length > 0) {
      const fwCardWidth = 65;
      const fwCardHeight = 42;
      const fwGap = 10;
      const totalFwWidth = Math.min(firewalls.length, 4) * fwCardWidth + (Math.min(firewalls.length, 4) - 1) * fwGap;
      let fwStartX = centerX - totalFwWidth / 2;

      firewalls.forEach((fw, idx) => {
        if (idx >= 4) return; // Limit to 4 per row
        const x = fwStartX + idx * (fwCardWidth + fwGap);

        // Card with shadow
        drawCard(x, yPosition, fwCardWidth, fwCardHeight);

        // Icon background (red/10)
        const iconSize = 14;
        drawIconBg(x + (fwCardWidth - iconSize) / 2, yPosition + 4, iconSize, redBgColor);

        // Shield icon
        pdf.setFillColor(...redColor);
        const shieldX = x + fwCardWidth / 2;
        const shieldY = yPosition + 11;
        // Draw shield shape
        pdf.setDrawColor(...redColor);
        pdf.setLineWidth(1);
        pdf.line(shieldX - 4, shieldY - 3, shieldX, shieldY - 5);
        pdf.line(shieldX, shieldY - 5, shieldX + 4, shieldY - 3);
        pdf.line(shieldX + 4, shieldY - 3, shieldX + 4, shieldY + 1);
        pdf.line(shieldX + 4, shieldY + 1, shieldX, shieldY + 5);
        pdf.line(shieldX, shieldY + 5, shieldX - 4, shieldY + 1);
        pdf.line(shieldX - 4, shieldY + 1, shieldX - 4, shieldY - 3);

        // Name
        pdf.setTextColor(...textColor);
        pdf.setFontSize(8);
        pdf.setFont('helvetica', 'bold');
        const fwName = truncateText(fw.name, fwCardWidth - 8);
        pdf.text(fwName, x + fwCardWidth / 2, yPosition + 22, { align: 'center' });

        // Manufacturer
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(6.5);
        pdf.setTextColor(...mutedColor);
        if (fw.manufacturer) {
          pdf.text(truncateText(`${fw.manufacturer} ${fw.model || ''}`, fwCardWidth - 8), x + fwCardWidth / 2, yPosition + 27, { align: 'center' });
        }

        // Internet speed (highlighted)
        if (fw.internet_speed) {
          pdf.setTextColor(...primaryColor);
          pdf.setFont('helvetica', 'bold');
          pdf.setFontSize(7);
          pdf.text(truncateText(fw.internet_speed, fwCardWidth - 8), x + fwCardWidth / 2, yPosition + 32, { align: 'center' });
        }

        // IP Address
        if (fw.ip_address) {
          pdf.setTextColor(...mutedColor);
          pdf.setFont('courier', 'normal');
          pdf.setFontSize(5.5);
          pdf.text(fw.ip_address, x + fwCardWidth / 2, yPosition + 38, { align: 'center' });
        }
      });

      yPosition += fwCardHeight + 6;

      // Connection line
      pdf.setDrawColor(...borderColor);
      pdf.setLineWidth(0.8);
      pdf.line(centerX, yPosition, centerX, yPosition + 8);
      yPosition += 10;
    }

    // Switches
    if (switches.length > 0) {
      const swCardWidth = 58;
      const swCardHeight = 36;
      const swGap = 10;
      const totalSwWidth = Math.min(switches.length, 4) * swCardWidth + (Math.min(switches.length, 4) - 1) * swGap;
      let swStartX = centerX - totalSwWidth / 2;

      switches.forEach((sw, idx) => {
        if (idx >= 4) return;
        const x = swStartX + idx * (swCardWidth + swGap);

        // Card
        drawCard(x, yPosition, swCardWidth, swCardHeight);

        // Icon background (green/10)
        const iconSize = 14;
        drawIconBg(x + (swCardWidth - iconSize) / 2, yPosition + 3, iconSize, greenBgColor);

        // Switch icon (network dots)
        pdf.setFillColor(...greenColor);
        const dotY = yPosition + 10;
        pdf.circle(x + swCardWidth / 2 - 4, dotY, 1.5, 'F');
        pdf.circle(x + swCardWidth / 2, dotY, 1.5, 'F');
        pdf.circle(x + swCardWidth / 2 + 4, dotY, 1.5, 'F');

        // Name
        pdf.setTextColor(...textColor);
        pdf.setFontSize(7.5);
        pdf.setFont('helvetica', 'bold');
        pdf.text(truncateText(sw.name, swCardWidth - 6), x + swCardWidth / 2, yPosition + 22, { align: 'center' });

        // Manufacturer
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(6);
        pdf.setTextColor(...mutedColor);
        if (sw.manufacturer) {
          pdf.text(truncateText(sw.manufacturer, swCardWidth - 6), x + swCardWidth / 2, yPosition + 27, { align: 'center' });
        }

        // IP
        if (sw.ip_address) {
          pdf.setFont('courier', 'normal');
          pdf.setFontSize(5.5);
          pdf.text(sw.ip_address, x + swCardWidth / 2, yPosition + 32, { align: 'center' });
        }
      });

      yPosition += swCardHeight + 8;
    }

    // WiFi Devices
    if (wifiDevices.length > 0) {
      const wifiCardWidth = 70;
      const wifiCardHeight = 26;
      const wifiGap = 8;
      const maxPerRow = Math.floor((contentWidth + wifiGap) / (wifiCardWidth + wifiGap));
      const visibleWifi = wifiDevices.slice(0, maxPerRow);
      const totalWifiWidth = visibleWifi.length * wifiCardWidth + (visibleWifi.length - 1) * wifiGap;
      let wifiStartX = centerX - totalWifiWidth / 2;

      visibleWifi.forEach((wifi, idx) => {
        const x = wifiStartX + idx * (wifiCardWidth + wifiGap);

        // Card - horizontal layout
        drawCard(x, yPosition, wifiCardWidth, wifiCardHeight);

        // Icon background (purple/10)
        const iconSize = 12;
        drawIconBg(x + 4, yPosition + (wifiCardHeight - iconSize) / 2, iconSize, purpleBgColor);

        // WiFi icon
        pdf.setFillColor(...purpleColor);
        const wifiX = x + 10;
        const wifiY = yPosition + wifiCardHeight / 2 + 3;
        pdf.circle(wifiX, wifiY, 1.2, 'F');

        // WiFi arcs
        pdf.setDrawColor(...purpleColor);
        pdf.setLineWidth(0.6);
        drawArc(pdf, wifiX, wifiY, 3, 220, 320);
        drawArc(pdf, wifiX, wifiY, 5, 220, 320);

        // Name and details
        pdf.setTextColor(...textColor);
        pdf.setFontSize(7);
        pdf.setFont('helvetica', 'bold');
        pdf.text(truncateText(wifi.name, wifiCardWidth - 22), x + 20, yPosition + 8);

        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(5.5);
        pdf.setTextColor(...mutedColor);
        if (wifi.manufacturer) {
          pdf.text(truncateText(`${wifi.manufacturer} ${wifi.model || ''}`, wifiCardWidth - 22), x + 20, yPosition + 13);
        }
        if (wifi.ip_address) {
          pdf.setFont('courier', 'normal');
          pdf.text(wifi.ip_address, x + 20, yPosition + 18);
        }
      });

      yPosition += wifiCardHeight + 8;
    }

    yPosition += 10;
  }

  // Helper to draw an arc using lines (jsPDF does not support arc natively)
  function drawArc(pdf: jsPDF, cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
    const segments = 20;
    const points: number[][] = [];
    for (let i = 0; i <= segments; i++) {
      const angle = (startAngle + (endAngle - startAngle) * (i / segments)) * Math.PI / 180;
      points.push([
        cx + r * Math.cos(angle),
        cy + r * Math.sin(angle)
      ]);
    }
    for (let i = 0; i < points.length - 1; i++) {
      pdf.line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]);
    }
  }

  // Helper to calculate network section height
  function calculateNetworkSectionHeight(devices: DiagramData['network_devices']): number {
    let height = 50; // Base for internet node
    const firewalls = devices.filter(d => d.device_type === 'firewall' || d.device_type === 'firewall_router' || d.device_type === 'router');
    const switches = devices.filter(d => d.device_type === 'switch');
    const wifiDevices = devices.filter(d => d.device_type === 'wifi');
    if (firewalls.length > 0) height += 60;
    if (switches.length > 0) height += 50;
    if (wifiDevices.length > 0) height += 40;
    return height;
  }

  // ==================== USER ENDPOINTS ====================
  // 3 columns: Desktops, Laptops, Workstations (matching web view)
  if (data.endpoint_users.length > 0) {
    drawSectionHeader('User Endpoints', mutedColor, accentBgColor);

    const desktops = data.endpoint_users.filter(e => e.device_type === 'desktop');
    const laptops = data.endpoint_users.filter(e => e.device_type === 'laptop');
    const workstations = data.endpoint_users.filter(e => e.device_type === 'workstation');

    const colGap = 8;
    const colWidth = (contentWidth - colGap * 2) / 3;
    const cardHeight = 34;
    const cardGap = 4;

    const col1X = margin;
    const col2X = margin + colWidth + colGap;
    const col3X = margin + (colWidth + colGap) * 2;

    // Column headers (like web view h3)
    pdf.setTextColor(...textColor);
    pdf.setFontSize(9);
    pdf.setFont('helvetica', 'bold');

    if (desktops.length > 0) pdf.text(`Desktops (${desktops.length})`, col1X, yPosition);
    if (laptops.length > 0) pdf.text(`Laptops (${laptops.length})`, col2X, yPosition);
    if (workstations.length > 0) pdf.text(`Workstations (${workstations.length})`, col3X, yPosition);
    yPosition += 6;

    // Draw endpoint cards in columns
    const maxRows = Math.max(desktops.length, laptops.length, workstations.length);

    const drawEndpointCard = (endpoint: typeof data.endpoint_users[0], x: number, y: number, width: number) => {
      // Card with shadow
      drawCard(x, y, width, cardHeight);

      // Icon + Name row
      const iconSize = 10;
      drawIconBg(x + 4, y + 4, iconSize, accentBgColor);

      // Monitor icon (simple rectangle)
      pdf.setDrawColor(...mutedColor);
      pdf.setLineWidth(0.5);
      pdf.rect(x + 6, y + 6, 6, 5, 'S');
      pdf.line(x + 9, y + 11, x + 9, y + 12);

      // Name
      pdf.setTextColor(...textColor);
      pdf.setFontSize(7.5);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(endpoint.name, width - 20), x + 17, y + 8);

      // User (using text instead of emoji since jsPDF doesn't support emojis)
      if (endpoint.assigned_to_name) {
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(6);
        pdf.setTextColor(...mutedColor);
        pdf.text(truncateText(`User: ${endpoint.assigned_to_name}`, width - 20), x + 17, y + 12);
      }

      // Details
      let detailY = y + 18;
      pdf.setFontSize(5.5);

      if (endpoint.operating_system) {
        pdf.setTextColor(...mutedColor);
        pdf.text('OS:', x + 4, detailY);
        pdf.setTextColor(...textColor);
        pdf.setFont('helvetica', 'bold');
        pdf.text(truncateText(endpoint.operating_system, width - 18), x + 12, detailY);
        detailY += 4;
      }

      pdf.setFont('helvetica', 'normal');
      if (endpoint.cpu) {
        pdf.setTextColor(...mutedColor);
        pdf.text(truncateText(`CPU: ${endpoint.cpu}`, width - 8), x + 4, detailY);
        detailY += 4;
      }
      if (endpoint.ram) {
        pdf.text(truncateText(`RAM: ${endpoint.ram}`, width - 8), x + 4, detailY);
        detailY += 4;
      }
      if (endpoint.ip_address) {
        pdf.text('IP:', x + 4, detailY);
        pdf.setFont('courier', 'normal');
        pdf.text(endpoint.ip_address, x + 12, detailY);
      }
    };

    for (let row = 0; row < maxRows; row++) {
      if (desktops[row]) {
        drawEndpointCard(desktops[row], col1X, yPosition, colWidth);
      }
      if (laptops[row]) {
        drawEndpointCard(laptops[row], col2X, yPosition, colWidth);
      }
      if (workstations[row]) {
        drawEndpointCard(workstations[row], col3X, yPosition, colWidth);
      }

      yPosition += cardHeight + cardGap;
    }

    yPosition += 8;
  }

  // ==================== SERVERS ====================
  if (data.servers.length > 0) {
    drawSectionHeader('Servers', mutedColor, accentBgColor);

    const cardsPerRow = 3;
    const cardGap = 6;
    const cardWidth = (contentWidth - cardGap * (cardsPerRow - 1)) / cardsPerRow;
    const cardHeight = 44;

    data.servers.forEach((server, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
      }

      const x = margin + col * (cardWidth + cardGap);
      const y = yPosition;

      // Card with shadow
      drawCard(x, y, cardWidth, cardHeight);

      // Icon background
      const iconSize = 14;
      drawIconBg(x + 5, y + 5, iconSize, accentBgColor);

      // Server icon (simple stacked boxes)
      pdf.setDrawColor(...mutedColor);
      pdf.setLineWidth(0.5);
      pdf.rect(x + 7.5, y + 7, 9, 4, 'S');
      pdf.rect(x + 7.5, y + 11.5, 9, 4, 'S');
      // Indicator dots
      pdf.setFillColor(...greenColor);
      pdf.circle(x + 9, y + 9, 0.7, 'F');
      pdf.circle(x + 9, y + 13.5, 0.7, 'F');

      // Name
      pdf.setTextColor(...textColor);
      pdf.setFontSize(8);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(server.name, cardWidth - 45), x + 22, y + 10);

      // Role subtitle
      if (server.role) {
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(6);
        pdf.setTextColor(...mutedColor);
        pdf.text(truncateText(server.role, cardWidth - 45), x + 22, y + 15);
      }

      // Badge (physical/virtual)
      const badgeText = server.server_type;
      const badgeColor = server.server_type === 'physical' ? primaryColor : purpleColor;
      const badgeBgColor = server.server_type === 'physical' ? blueBgColor : purpleBgColor;
      drawBadge(x + cardWidth - 24, y + 10, badgeText, badgeBgColor, badgeColor);

      // Details
      let detailY = y + 22;
      pdf.setFontSize(6);
      pdf.setFont('helvetica', 'normal');

      if (server.operating_system) {
        pdf.setTextColor(...mutedColor);
        pdf.text('OS:', x + 5, detailY);
        pdf.setTextColor(...textColor);
        pdf.setFont('helvetica', 'bold');
        pdf.text(truncateText(server.operating_system, cardWidth - 18), x + 13, detailY);
        detailY += 4.5;
      }

      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(...mutedColor);
      if (server.cpu) {
        pdf.text(truncateText(`CPU: ${server.cpu}`, cardWidth - 10), x + 5, detailY);
        detailY += 4;
      }
      if (server.ram) {
        pdf.text(`RAM: ${server.ram}`, x + 5, detailY);
        detailY += 4;
      }
      if (server.ip_address) {
        pdf.text('IP:', x + 5, detailY);
        pdf.setFont('courier', 'normal');
        pdf.text(server.ip_address, x + 13, detailY);
      }
    });

    yPosition += cardHeight + 12;
  }

  // ==================== PERIPHERALS ====================
  if (data.peripherals.length > 0) {
    drawSectionHeader('Peripherals', mutedColor, accentBgColor);

    const cardsPerRow = 4;
    const cardGap = 5;
    const cardWidth = (contentWidth - cardGap * (cardsPerRow - 1)) / cardsPerRow;
    const cardHeight = 30;

    data.peripherals.forEach((peripheral, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card with shadow
      drawCard(x, yPosition, cardWidth, cardHeight);

      // Icon background
      const iconSize = 12;
      drawIconBg(x + 4, yPosition + 4, iconSize, accentBgColor);

      // Printer icon
      pdf.setDrawColor(...mutedColor);
      pdf.setLineWidth(0.5);
      pdf.rect(x + 6, yPosition + 7, 8, 5, 'S');
      pdf.line(x + 7, yPosition + 9.5, x + 13, yPosition + 9.5);
      // Paper tray
      pdf.rect(x + 7, yPosition + 12, 6, 2, 'S');

      // Name
      pdf.setTextColor(...textColor);
      pdf.setFontSize(7);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(peripheral.name, cardWidth - 20), x + 18, yPosition + 8);

      // Type
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(5.5);
      pdf.setTextColor(...mutedColor);
      pdf.text(peripheral.device_type, x + 18, yPosition + 12);

      // Manufacturer/Model
      if (peripheral.manufacturer || peripheral.model) {
        const details = [peripheral.manufacturer, peripheral.model].filter(Boolean).join(' ');
        pdf.text(truncateText(details, cardWidth - 20), x + 18, yPosition + 17);
      }

      // Serial number
      if (peripheral.serial_number) {
        pdf.setFont('courier', 'normal');
        pdf.setFontSize(5);
        pdf.text(`S/N: ${truncateText(peripheral.serial_number, cardWidth - 24)}`, x + 18, yPosition + 22);
      }
    });

    yPosition += cardHeight + 12;
  }

  // ==================== BACKUPS ====================
  if (data.backups.length > 0) {
    drawSectionHeader('Backups', mutedColor, accentBgColor);

    const cardsPerRow = 2;
    const cardGap = 8;
    const cardWidth = (contentWidth - cardGap) / cardsPerRow;
    const cardHeight = 50;

    data.backups.forEach((backup, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card with shadow
      drawCard(x, yPosition, cardWidth, cardHeight);

      // Icon background
      const iconSize = 14;
      drawIconBg(x + 5, yPosition + 5, iconSize, accentBgColor);

      // Database/disk icon
      pdf.setDrawColor(...mutedColor);
      pdf.setLineWidth(0.5);
      // Cylinder shape
      pdf.ellipse(x + 12, yPosition + 8, 5, 2, 'S');
      pdf.line(x + 7, yPosition + 8, x + 7, yPosition + 14);
      pdf.line(x + 17, yPosition + 8, x + 17, yPosition + 14);
      pdf.ellipse(x + 12, yPosition + 14, 5, 2, 'S');

      // Name
      pdf.setTextColor(...textColor);
      pdf.setFontSize(8);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(backup.name, cardWidth - 55), x + 24, yPosition + 10);

      // Status badge
      if (backup.backup_status) {
        let statusBgColor: [number, number, number] = accentBgColor;
        let statusTextColor: [number, number, number] = mutedColor;
        if (backup.backup_status === 'active') {
          statusBgColor = greenBgColor;
          statusTextColor = greenColor;
        } else if (backup.backup_status === 'failed') {
          statusBgColor = redBgColor;
          statusTextColor = redColor;
        } else if (backup.backup_status === 'warning') {
          statusBgColor = yellowBgColor;
          statusTextColor = yellowColor;
        }
        drawBadge(x + cardWidth - 22, yPosition + 10, backup.backup_status, statusBgColor, statusTextColor);
      }

      // Type subtitle
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(6);
      pdf.setTextColor(...mutedColor);
      pdf.text(`Type: ${backup.backup_type.replace(/_/g, ' ')}`, x + 24, yPosition + 16);

      // Details in two columns
      let detailY = yPosition + 24;
      const detailCol1X = x + 5;
      const detailCol2X = x + cardWidth / 2;
      pdf.setFontSize(5.5);

      if (backup.vendor) {
        pdf.setTextColor(...mutedColor);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Vendor:', detailCol1X, detailY);
        pdf.setFont('helvetica', 'normal');
        pdf.text(truncateText(backup.vendor, cardWidth / 2 - 20), detailCol1X + 15, detailY);
      }
      if (backup.frequency) {
        pdf.setFont('helvetica', 'bold');
        pdf.text('Frequency:', detailCol2X, detailY);
        pdf.setFont('helvetica', 'normal');
        pdf.text(truncateText(backup.frequency, cardWidth / 2 - 22), detailCol2X + 18, detailY);
      }
      detailY += 5;

      if (backup.storage_location) {
        pdf.setFont('helvetica', 'bold');
        pdf.text('Storage:', detailCol1X, detailY);
        pdf.setFont('helvetica', 'normal');
        pdf.text(truncateText(backup.storage_location, cardWidth / 2 - 20), detailCol1X + 15, detailY);
      }
      if (backup.retention_period) {
        pdf.setFont('helvetica', 'bold');
        pdf.text('Retention:', detailCol2X, detailY);
        pdf.setFont('helvetica', 'normal');
        pdf.text(truncateText(backup.retention_period, cardWidth / 2 - 22), detailCol2X + 18, detailY);
      }
      detailY += 5;

      if (backup.target_systems) {
        pdf.setFont('helvetica', 'bold');
        pdf.text('Targets:', detailCol1X, detailY);
        pdf.setFont('helvetica', 'normal');
        pdf.text(truncateText(backup.target_systems, cardWidth - 25), detailCol1X + 15, detailY);
      }
    });

    yPosition += cardHeight + 12;
  }

  // ==================== SOFTWARE ====================
  if (data.software.length > 0) {
    drawSectionHeader('Software', mutedColor, accentBgColor);

    const cardsPerRow = 3;
    const cardGap = 6;
    const cardWidth = (contentWidth - cardGap * (cardsPerRow - 1)) / cardsPerRow;
    const cardHeight = 36;

    data.software.forEach((software, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card with shadow
      drawCard(x, yPosition, cardWidth, cardHeight);

      // Icon background
      const iconSize = 12;
      drawIconBg(x + 4, yPosition + 4, iconSize, accentBgColor);

      // Package icon (box with ribbon)
      pdf.setDrawColor(...mutedColor);
      pdf.setLineWidth(0.5);
      pdf.rect(x + 6, yPosition + 7, 8, 6, 'S');
      // Top flaps
      pdf.line(x + 6, yPosition + 7, x + 8, yPosition + 5);
      pdf.line(x + 14, yPosition + 7, x + 12, yPosition + 5);
      pdf.line(x + 8, yPosition + 5, x + 12, yPosition + 5);
      // Vertical line on box
      pdf.line(x + 10, yPosition + 5, x + 10, yPosition + 13);

      // Name
      pdf.setTextColor(...textColor);
      pdf.setFontSize(7.5);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(software.name, cardWidth - 22), x + 19, yPosition + 9);

      // Type
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(6);
      pdf.setTextColor(...mutedColor);
      pdf.text(software.software_type.replace(/_/g, ' '), x + 19, yPosition + 14);

      // Contacts
      let detailY = yPosition + 21;
      pdf.setFontSize(5.5);
      if (software.assigned_contacts && software.assigned_contacts.length > 0) {
        software.assigned_contacts.slice(0, 2).forEach(contact => {
          pdf.text(`• ${truncateText(contact.contact_name, cardWidth - 12)}`, x + 5, detailY);
          detailY += 4;
        });
      }

      // Notes
      if (software.notes && detailY < yPosition + cardHeight - 3) {
        pdf.setFontSize(5);
        pdf.setTextColor(...mutedColor);
        pdf.text(truncateText(software.notes, cardWidth - 10), x + 5, detailY);
      }
    });

    yPosition += cardHeight + 12;
  }

  // ==================== VOIP ====================
  if (data.voip.length > 0) {
    drawSectionHeader('VoIP Services', mutedColor, accentBgColor);

    const cardsPerRow = 3;
    const cardGap = 6;
    const cardWidth = (contentWidth - cardGap * (cardsPerRow - 1)) / cardsPerRow;
    const cardHeight = 38;

    data.voip.forEach((voip, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card with shadow
      drawCard(x, yPosition, cardWidth, cardHeight);

      // Icon background
      const iconSize = 12;
      drawIconBg(x + 4, yPosition + 4, iconSize, accentBgColor);

      // Phone icon
      pdf.setDrawColor(...mutedColor);
      pdf.setLineWidth(0.6);
      // Phone receiver shape
      pdf.line(x + 6, yPosition + 7, x + 6, yPosition + 13);
      pdf.line(x + 6, yPosition + 7, x + 9, yPosition + 7);
      pdf.line(x + 9, yPosition + 7, x + 11, yPosition + 9);
      pdf.line(x + 11, yPosition + 9, x + 11, yPosition + 11);
      pdf.line(x + 11, yPosition + 11, x + 9, yPosition + 13);
      pdf.line(x + 9, yPosition + 13, x + 6, yPosition + 13);
      // Base
      pdf.line(x + 13, yPosition + 11, x + 13, yPosition + 14);
      pdf.line(x + 13, yPosition + 14, x + 7, yPosition + 14);

      // Name
      pdf.setTextColor(...textColor);
      pdf.setFontSize(7.5);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(voip.name, cardWidth - 22), x + 19, yPosition + 9);

      // Type
      const voipTypeDisplay = voip.voip_type === 'teams' ? 'Microsoft Teams' :
                              voip.voip_type === '3cx' ? '3CX' :
                              voip.voip_type === 'yeastar' ? 'Yeastar' : 'Other';
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(6);
      pdf.setTextColor(...mutedColor);
      pdf.text(voipTypeDisplay, x + 19, yPosition + 14);

      // Contacts
      let detailY = yPosition + 21;
      pdf.setFontSize(5.5);
      if (voip.assigned_contacts && voip.assigned_contacts.length > 0) {
        voip.assigned_contacts.slice(0, 2).forEach(contact => {
          let contactText = `• ${contact.contact_name}`;
          if (contact.extension) contactText += ` (Ext: ${contact.extension})`;
          pdf.text(truncateText(contactText, cardWidth - 10), x + 5, detailY);
          detailY += 4;
        });
      }

      // Licenses
      if (voip.quantity) {
        pdf.setFont('helvetica', 'bold');
        pdf.text('Licenses:', x + 5, detailY);
        pdf.setFont('helvetica', 'normal');
        pdf.text(`${voip.assigned_count || 0}/${voip.quantity}`, x + 22, detailY);
      }
    });

    yPosition += cardHeight + 12;
  }

  // Add footers to all pages
  addFooter();

  // Save the PDF
  pdf.save(`${sanitizeFilename(orgName)}_infrastructure_diagram.pdf`);
}

/**
 * Trigger browser print dialog (legacy fallback)
 */
export function printDiagram(): void {
  window.print();
}

/**
 * Generate SVG representation of the diagram
 */
function generateSVGDiagram(data: DiagramData, orgName: string): string {
  const width = 1200;
  let yOffset = 60;
  const sectionGap = 100;

  let svgContent = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${width}" height="3000" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title { font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; }
      .section-title { font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; }
      .label { font-family: Arial, sans-serif; font-size: 12px; }
      .small-label { font-family: Arial, sans-serif; font-size: 10px; fill: #666; }
      .device-box { fill: #ffffff; stroke: #ccc; stroke-width: 1; }
      .connection-line { stroke: #666; stroke-width: 2; }
    </style>
  </defs>

  <!-- Title -->
  <text x="${width / 2}" y="30" text-anchor="middle" class="title">${escapeXml(orgName)} - IT Infrastructure Diagram</text>
`;

  // Network Devices Section
  if (data.network_devices.length > 0) {
    svgContent += `\n  <!-- Network Devices -->
  <text x="20" y="${yOffset}" class="section-title">Network Infrastructure</text>`;
    yOffset += 30;

    data.network_devices.forEach((device, idx) => {
      const x = 50 + (idx % 4) * 280;
      const y = yOffset + Math.floor(idx / 4) * 100;

      svgContent += `
  <g>
    <rect x="${x}" y="${y}" width="260" height="80" class="device-box" rx="5"/>
    <text x="${x + 10}" y="${y + 20}" class="label" font-weight="bold">${escapeXml(device.name)}</text>
    <text x="${x + 10}" y="${y + 35}" class="small-label">Type: ${escapeXml(device.device_type)}</text>
    ${device.manufacturer ? `<text x="${x + 10}" y="${y + 50}" class="small-label">${escapeXml(device.manufacturer)} ${escapeXml(device.model || '')}</text>` : ''}
    ${device.ip_address ? `<text x="${x + 10}" y="${y + 65}" class="small-label">IP: ${escapeXml(device.ip_address)}</text>` : ''}
  </g>`;
    });

    yOffset += Math.ceil(data.network_devices.length / 4) * 100 + sectionGap;
  }

  // Servers Section
  if (data.servers.length > 0) {
    svgContent += `\n  <!-- Servers -->
  <text x="20" y="${yOffset}" class="section-title">Servers</text>`;
    yOffset += 30;

    data.servers.forEach((server, idx) => {
      const x = 50 + (idx % 3) * 380;
      const y = yOffset + Math.floor(idx / 3) * 120;

      svgContent += `
  <g>
    <rect x="${x}" y="${y}" width="360" height="100" class="device-box" rx="5"/>
    <text x="${x + 10}" y="${y + 20}" class="label" font-weight="bold">${escapeXml(server.name)}</text>
    <text x="${x + 10}" y="${y + 35}" class="small-label">Type: ${escapeXml(server.server_type)} | Role: ${escapeXml(server.role || 'N/A')}</text>
    ${server.operating_system ? `<text x="${x + 10}" y="${y + 50}" class="small-label">OS: ${escapeXml(server.operating_system)}</text>` : ''}
    ${server.cpu ? `<text x="${x + 10}" y="${y + 65}" class="small-label">CPU: ${escapeXml(server.cpu)}</text>` : ''}
    ${server.ram ? `<text x="${x + 10}" y="${y + 80}" class="small-label">RAM: ${escapeXml(server.ram)}</text>` : ''}
    ${server.ip_address ? `<text x="${x + 10}" y="${y + 95}" class="small-label">IP: ${escapeXml(server.ip_address)}</text>` : ''}
  </g>`;
    });

    yOffset += Math.ceil(data.servers.length / 3) * 120 + sectionGap;
  }

  // Add remaining sections...
  svgContent += '\n</svg>';
  return svgContent;
}

/**
 * Sanitize filename for safe file system usage
 */
function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[^a-z0-9]/gi, '_')
    .replace(/_+/g, '_')
    .toLowerCase();
}

/**
 * Escape XML special characters
 */
function escapeXml(text: string): string {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}