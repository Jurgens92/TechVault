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
 * Matches the layout of Diagram.tsx for print
 */
export async function exportAsPDF(
  data: DiagramData,
  orgName: string,
  elementId?: string
): Promise<void> {
  // Create PDF in landscape A4
  const pdf = new jsPDF({
    orientation: 'landscape',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 12;
  const contentWidth = pageWidth - margin * 2;
  let yPosition = margin;

  // Colors
  const primaryColor: [number, number, number] = [59, 130, 246]; // Blue
  const darkColor: [number, number, number] = [30, 41, 59]; // Slate-800
  const grayColor: [number, number, number] = [100, 116, 139]; // Slate-500
  const lightGray: [number, number, number] = [241, 245, 249]; // Slate-100
  const greenColor: [number, number, number] = [34, 197, 94]; // Green-500
  const redColor: [number, number, number] = [239, 68, 68]; // Red-500
  const purpleColor: [number, number, number] = [168, 85, 247]; // Purple-500
  const blueColor: [number, number, number] = [59, 130, 246]; // Blue-500

  // Helper function to add a new page if needed
  const checkPageBreak = (requiredSpace: number): void => {
    if (yPosition + requiredSpace > pageHeight - margin - 10) {
      pdf.addPage();
      yPosition = margin;
    }
  };

  // Helper function to add header on each page
  const addHeader = (): void => {
    pdf.setFillColor(...primaryColor);
    pdf.rect(0, 0, pageWidth, 10, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(9);
    pdf.setFont('helvetica', 'bold');
    pdf.text('TechVault', margin, 7);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`${orgName} - IT Infrastructure Diagram`, pageWidth - margin, 7, { align: 'right' });
    yPosition = 16;
  };

  // Helper function to add footer
  const addFooter = (): void => {
    const pageCount = pdf.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFontSize(7);
      pdf.setTextColor(...grayColor);
      pdf.text(
        `Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}`,
        margin,
        pageHeight - 6
      );
      pdf.text(`Page ${i} of ${pageCount}`, pageWidth - margin, pageHeight - 6, { align: 'right' });
    }
  };

  // Helper to draw section box with title and icon
  const drawSectionBox = (title: string, iconType: string): void => {
    checkPageBreak(20);
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(0.3);
    // Section title background
    pdf.setFillColor(...primaryColor);
    pdf.roundedRect(margin, yPosition, contentWidth, 9, 1.5, 1.5, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'bold');
    pdf.text(title, margin + 4, yPosition + 6.5);
    yPosition += 13;
  };

  // Helper to draw a small badge
  const drawBadge = (x: number, y: number, text: string, color: [number, number, number]): void => {
    const badgeWidth = pdf.getTextWidth(text) + 4;
    pdf.setFillColor(color[0], color[1], color[2], 0.15);
    pdf.roundedRect(x, y - 3, badgeWidth, 4.5, 1, 1, 'F');
    pdf.setTextColor(...color);
    pdf.setFontSize(6);
    pdf.setFont('helvetica', 'normal');
    pdf.text(text, x + 2, y);
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

  // Add first page header
  addHeader();

  // Title Section
  pdf.setTextColor(...darkColor);
  pdf.setFontSize(18);
  pdf.setFont('helvetica', 'bold');
  pdf.text(orgName, margin, yPosition + 5);
  yPosition += 8;

  pdf.setFontSize(10);
  pdf.setTextColor(...grayColor);
  pdf.setFont('helvetica', 'normal');
  pdf.text('IT Infrastructure Diagram', margin, yPosition + 3);
  yPosition += 10;

  // ==================== NETWORK INFRASTRUCTURE ====================
  // Matches the hierarchical layout in Diagram.tsx
  if (data.network_devices.length > 0) {
    drawSectionBox('Network Infrastructure', 'network');

    const firewalls = data.network_devices.filter(d => 
      d.device_type === 'firewall' || d.device_type === 'firewall_router' || d.device_type === 'router'
    );
    const switches = data.network_devices.filter(d => d.device_type === 'switch');
    const wifiDevices = data.network_devices.filter(d => d.device_type === 'wifi');

    const centerX = pageWidth / 2;

    // Internet circle with globe icon (drawn as circle with crosshairs)
    pdf.setFillColor(...blueColor);
    pdf.circle(centerX, yPosition + 8, 8, 'F');
    pdf.setDrawColor(255, 255, 255);
    pdf.setLineWidth(0.8);
    pdf.circle(centerX, yPosition + 8, 4, 'S');
    pdf.line(centerX - 6, yPosition + 8, centerX + 6, yPosition + 8);
    pdf.line(centerX, yPosition + 2, centerX, yPosition + 14);
    pdf.setTextColor(...darkColor);
    pdf.setFontSize(8);
    pdf.setFont('helvetica', 'normal');
    pdf.text('Internet', centerX, yPosition + 20, { align: 'center' });
    yPosition += 24;

    // Connection line
    pdf.setDrawColor(...grayColor);
    pdf.setLineWidth(0.5);
    pdf.line(centerX, yPosition, centerX, yPosition + 6);
    yPosition += 8;

    // Firewalls/Routers
    if (firewalls.length > 0) {
      const fwCardWidth = 55;
      const fwCardHeight = 32;
      const fwGap = 8;
      const totalFwWidth = firewalls.length * fwCardWidth + (firewalls.length - 1) * fwGap;
      let fwStartX = centerX - totalFwWidth / 2;

      firewalls.forEach((fw, idx) => {
        const x = fwStartX + idx * (fwCardWidth + fwGap);
        
        // Card
        pdf.setFillColor(255, 255, 255);
        pdf.setDrawColor(200, 200, 200);
        pdf.setLineWidth(0.3);
        pdf.roundedRect(x, yPosition, fwCardWidth, fwCardHeight, 2, 2, 'FD');
        
        // Shield icon (drawn as shape)
        pdf.setFillColor(254, 226, 226); // Red light
        pdf.roundedRect(x + fwCardWidth/2 - 6, yPosition + 2, 12, 11, 1, 1, 'F');
        pdf.setFillColor(...redColor);
        // Draw shield shape
        pdf.setDrawColor(...redColor);
        pdf.setLineWidth(0.6);
        const shieldX = x + fwCardWidth/2;
        const shieldY = yPosition + 7;
        pdf.line(shieldX - 3, shieldY - 2, shieldX, shieldY - 4);
        pdf.line(shieldX, shieldY - 4, shieldX + 3, shieldY - 2);
        pdf.line(shieldX + 3, shieldY - 2, shieldX + 3, shieldY + 1);
        pdf.line(shieldX + 3, shieldY + 1, shieldX, shieldY + 4);
        pdf.line(shieldX, shieldY + 4, shieldX - 3, shieldY + 1);
        pdf.line(shieldX - 3, shieldY + 1, shieldX - 3, shieldY - 2);
        
        // Name
        pdf.setTextColor(...darkColor);
        pdf.setFontSize(7);
        pdf.setFont('helvetica', 'bold');
        const fwName = truncateText(fw.name, fwCardWidth - 6);
        pdf.text(fwName, x + fwCardWidth/2, yPosition + 17, { align: 'center' });
        
        // Details
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(6);
        pdf.setTextColor(...grayColor);
        if (fw.manufacturer) {
          pdf.text(truncateText(fw.manufacturer, fwCardWidth - 6), x + fwCardWidth/2, yPosition + 21, { align: 'center' });
        }
        if (fw.internet_speed) {
          pdf.setTextColor(...blueColor);
          pdf.text(truncateText(fw.internet_speed, fwCardWidth - 6), x + fwCardWidth/2, yPosition + 25, { align: 'center' });
        }
        if (fw.ip_address) {
          pdf.setTextColor(...grayColor);
          pdf.setFont('courier', 'normal');
          pdf.setFontSize(5);
          pdf.text(fw.ip_address, x + fwCardWidth/2, yPosition + 29, { align: 'center' });
        }
      });
      
      yPosition += fwCardHeight + 4;
      
      // Connection line
      pdf.setDrawColor(...grayColor);
      pdf.setLineWidth(0.5);
      pdf.line(centerX, yPosition, centerX, yPosition + 6);
      yPosition += 8;
    }

    // Switches
    if (switches.length > 0) {
      const swCardWidth = 50;
      const swCardHeight = 26;
      const swGap = 8;
      const totalSwWidth = switches.length * swCardWidth + (switches.length - 1) * swGap;
      let swStartX = centerX - totalSwWidth / 2;

      switches.forEach((sw, idx) => {
        const x = swStartX + idx * (swCardWidth + swGap);
        
        // Card
        pdf.setFillColor(255, 255, 255);
        pdf.setDrawColor(200, 200, 200);
        pdf.setLineWidth(0.3);
        pdf.roundedRect(x, yPosition, swCardWidth, swCardHeight, 2, 2, 'FD');
        
        // Switch icon (network symbol - box with dots)
        pdf.setFillColor(220, 252, 231); // Green light
        pdf.roundedRect(x + swCardWidth/2 - 6, yPosition + 2, 12, 9, 1, 1, 'F');
        pdf.setFillColor(...greenColor);
        pdf.circle(x + swCardWidth/2 - 3, yPosition + 6.5, 1, 'F');
        pdf.circle(x + swCardWidth/2, yPosition + 6.5, 1, 'F');
        pdf.circle(x + swCardWidth/2 + 3, yPosition + 6.5, 1, 'F');
        
        // Name
        pdf.setTextColor(...darkColor);
        pdf.setFontSize(7);
        pdf.setFont('helvetica', 'bold');
        pdf.text(truncateText(sw.name, swCardWidth - 4), x + swCardWidth/2, yPosition + 15, { align: 'center' });
        
        // Details
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(5);
        pdf.setTextColor(...grayColor);
        if (sw.manufacturer) {
          pdf.text(truncateText(sw.manufacturer, swCardWidth - 4), x + swCardWidth/2, yPosition + 19, { align: 'center' });
        }
        if (sw.ip_address) {
          pdf.setFont('courier', 'normal');
          pdf.text(sw.ip_address, x + swCardWidth/2, yPosition + 23, { align: 'center' });
        }
      });
      
      yPosition += swCardHeight + 6;
    }

    // WiFi Devices
    if (wifiDevices.length > 0) {
      const wifiCardWidth = 60;
      const wifiCardHeight = 20;
      const wifiGap = 6;
      const totalWifiWidth = wifiDevices.length * wifiCardWidth + (wifiDevices.length - 1) * wifiGap;
      let wifiStartX = centerX - totalWifiWidth / 2;

      wifiDevices.forEach((wifi, idx) => {
        const x = wifiStartX + idx * (wifiCardWidth + wifiGap);
        
        // Card - horizontal layout
        pdf.setFillColor(255, 255, 255);
        pdf.setDrawColor(200, 200, 200);
        pdf.setLineWidth(0.3);
        pdf.roundedRect(x, yPosition, wifiCardWidth, wifiCardHeight, 2, 2, 'FD');
        
        // WiFi icon (arcs)
        pdf.setFillColor(243, 232, 255); // Purple light
        pdf.roundedRect(x + 2, yPosition + 3, 14, 14, 1, 1, 'F');
        pdf.setDrawColor(...purpleColor);
        pdf.setLineWidth(0.5);
        // Draw wifi arcs
        const wifiX = x + 9;
        const wifiY = yPosition + 13;
        pdf.circle(wifiX, wifiY, 1, 'F');
        // Arc 1 (approximate with lines)
        drawArc(pdf, wifiX, wifiY, 3, 220, 320);
        // Arc 2 (approximate with lines)
        drawArc(pdf, wifiX, wifiY, 5, 220, 320);

    // Helper to draw an arc using lines (jsPDF does not support arc natively)
    function drawArc(pdf: any, cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
      const segments = 20;
      const points = [];
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
        
        // Name and details
        pdf.setTextColor(...darkColor);
        pdf.setFontSize(6);
        pdf.setFont('helvetica', 'bold');
        pdf.text(truncateText(wifi.name, wifiCardWidth - 20), x + 18, yPosition + 6);
        
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(5);
        pdf.setTextColor(...grayColor);
        if (wifi.manufacturer) {
          pdf.text(truncateText(`${wifi.manufacturer} ${wifi.model || ''}`, wifiCardWidth - 20), x + 18, yPosition + 10);
        }
        if (wifi.ip_address) {
          pdf.setFont('courier', 'normal');
          pdf.text(wifi.ip_address, x + 18, yPosition + 14);
        }
      });
      
      yPosition += wifiCardHeight + 6;
    }

    yPosition += 8;
  }

  // ==================== USER ENDPOINTS ====================
  // 3 columns: Desktops, Laptops, Workstations
  if (data.endpoint_users.length > 0) {
    checkPageBreak(60);
    drawSectionBox('User Endpoints', 'endpoints');

    const desktops = data.endpoint_users.filter(e => e.device_type === 'desktop');
    const laptops = data.endpoint_users.filter(e => e.device_type === 'laptop');
    const workstations = data.endpoint_users.filter(e => e.device_type === 'workstation');

    const colWidth = (contentWidth - 8) / 3;
    const cardHeight = 28;
    const cardGap = 3;

    // Column headers
    pdf.setTextColor(...darkColor);
    pdf.setFontSize(8);
    pdf.setFont('helvetica', 'bold');
    
    const col1X = margin;
    const col2X = margin + colWidth + 4;
    const col3X = margin + (colWidth + 4) * 2;

    pdf.text(`Desktops (${desktops.length})`, col1X, yPosition);
    pdf.text(`Laptops (${laptops.length})`, col2X, yPosition);
    pdf.text(`Workstations (${workstations.length})`, col3X, yPosition);
    yPosition += 5;

    // Draw endpoint cards in columns
    const maxRows = Math.max(desktops.length, laptops.length, workstations.length);
    
    const drawEndpointCard = (endpoint: typeof data.endpoint_users[0], x: number, y: number, width: number) => {
      // Card
      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.3);
      pdf.roundedRect(x, y, width, cardHeight, 1.5, 1.5, 'FD');
      
      // Name
      pdf.setTextColor(...darkColor);
      pdf.setFontSize(7);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(endpoint.name, width - 4), x + 2, y + 5);
      
      // User
      if (endpoint.assigned_to_name) {
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(6);
        pdf.setTextColor(...grayColor);
        pdf.text(truncateText(endpoint.assigned_to_name, width - 8), x + 2, y + 9);
      }
      
      // Details
      let detailY = y + 13;
      pdf.setFontSize(5);
      
      if (endpoint.operating_system) {
        pdf.setTextColor(...darkColor);
        pdf.text(`OS: ${truncateText(endpoint.operating_system, width - 8)}`, x + 2, detailY);
        detailY += 3.5;
      }
      if (endpoint.cpu) {
        pdf.setTextColor(...grayColor);
        pdf.text(`CPU: ${truncateText(endpoint.cpu, width - 8)}`, x + 2, detailY);
        detailY += 3.5;
      }
      if (endpoint.ram) {
        pdf.text(`RAM: ${endpoint.ram}`, x + 2, detailY);
        detailY += 3.5;
      }
      if (endpoint.ip_address) {
        pdf.setFont('courier', 'normal');
        pdf.text(`IP: ${endpoint.ip_address}`, x + 2, detailY);
      }
    };

    for (let row = 0; row < maxRows; row++) {
      checkPageBreak(cardHeight + cardGap);
      
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

    yPosition += 6;
  }

  // ==================== SERVERS ====================
  if (data.servers.length > 0) {
    checkPageBreak(50);
    drawSectionBox('Servers', 'servers');

    const cardsPerRow = 3;
    const cardWidth = (contentWidth - 8) / cardsPerRow;
    const cardHeight = 38;
    const cardGap = 4;

    data.servers.forEach((server, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
        checkPageBreak(cardHeight + cardGap);
      }

      const x = margin + col * (cardWidth + cardGap);
      const y = yPosition;

      // Card
      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.3);
      pdf.roundedRect(x, y, cardWidth, cardHeight, 2, 2, 'FD');

      // Server icon (simple box with lines)
      pdf.setFillColor(240, 240, 240);
      pdf.roundedRect(x + 3, y + 3, 10, 10, 1, 1, 'F');
      pdf.setDrawColor(...grayColor);
      pdf.setLineWidth(0.3);
      pdf.rect(x + 4.5, y + 4.5, 7, 7, 'S');
      pdf.line(x + 4.5, y + 7, x + 11.5, y + 7);
      pdf.line(x + 4.5, y + 9.5, x + 11.5, y + 9.5);

      pdf.setTextColor(...darkColor);
      pdf.setFontSize(8);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(server.name, cardWidth - 20), x + 16, y + 8);

      // Role subtitle
      if (server.role) {
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(6);
        pdf.setTextColor(...grayColor);
        pdf.text(truncateText(server.role, cardWidth - 50), x + 16, y + 12);
      }

      // Badge (physical/virtual)
      const badgeText = server.server_type;
      const badgeColor = server.server_type === 'physical' ? blueColor : purpleColor;
      drawBadge(x + cardWidth - 22, y + 9, badgeText, badgeColor);

      // Details
      let detailY = y + 18;
      pdf.setFontSize(5.5);
      pdf.setFont('helvetica', 'normal');

      if (server.operating_system) {
        pdf.setTextColor(...darkColor);
        pdf.text(`OS: ${truncateText(server.operating_system, cardWidth - 8)}`, x + 3, detailY);
        detailY += 4;
      }
      if (server.cpu) {
        pdf.setTextColor(...grayColor);
        pdf.text(`CPU: ${truncateText(server.cpu, cardWidth - 8)}`, x + 3, detailY);
        detailY += 4;
      }
      if (server.ram) {
        pdf.text(`RAM: ${server.ram}`, x + 3, detailY);
        detailY += 4;
      }
      if (server.ip_address) {
        pdf.setFont('courier', 'normal');
        pdf.text(`IP: ${server.ip_address}`, x + 3, detailY);
      }
    });

    yPosition += cardHeight + 10;
  }

  // ==================== PERIPHERALS ====================
  if (data.peripherals.length > 0) {
    checkPageBreak(40);
    drawSectionBox('Peripherals', 'peripherals');

    const cardsPerRow = 4;
    const cardWidth = (contentWidth - 12) / cardsPerRow;
    const cardHeight = 24;
    const cardGap = 4;

    data.peripherals.forEach((peripheral, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
        checkPageBreak(cardHeight + cardGap);
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card - horizontal layout
      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.3);
      pdf.roundedRect(x, yPosition, cardWidth, cardHeight, 2, 2, 'FD');

      // Icon (simple shape based on type)
      pdf.setFillColor(240, 240, 240);
      pdf.roundedRect(x + 2, yPosition + 2, 12, 12, 1, 1, 'F');
      pdf.setDrawColor(...grayColor);
      pdf.setLineWidth(0.3);
      // Draw a simple printer/device icon
      pdf.rect(x + 4, yPosition + 5, 8, 6, 'S');
      pdf.line(x + 5, yPosition + 8, x + 11, yPosition + 8);

      // Name
      pdf.setTextColor(...darkColor);
      pdf.setFontSize(6.5);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(peripheral.name, cardWidth - 18), x + 16, yPosition + 6);

      // Type and details
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(5);
      pdf.setTextColor(...grayColor);
      pdf.text(peripheral.device_type, x + 16, yPosition + 10);
      
      if (peripheral.manufacturer && peripheral.model) {
        pdf.text(truncateText(`${peripheral.manufacturer} ${peripheral.model}`, cardWidth - 18), x + 16, yPosition + 14);
      }
      if (peripheral.serial_number) {
        pdf.setFont('courier', 'normal');
        pdf.text(`S/N: ${truncateText(peripheral.serial_number, cardWidth - 22)}`, x + 16, yPosition + 18);
      }
    });

    yPosition += cardHeight + 10;
  }

  // ==================== BACKUPS ====================
  if (data.backups.length > 0) {
    checkPageBreak(50);
    drawSectionBox('Backups', 'backups');

    const cardsPerRow = 2;
    const cardWidth = (contentWidth - 4) / cardsPerRow;
    const cardHeight = 42;
    const cardGap = 4;

    data.backups.forEach((backup, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
        checkPageBreak(cardHeight + cardGap);
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card
      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.3);
      pdf.roundedRect(x, yPosition, cardWidth, cardHeight, 2, 2, 'FD');

      // Icon (database/disk shape)
      pdf.setFillColor(240, 240, 240);
      pdf.roundedRect(x + 3, yPosition + 3, 12, 12, 1, 1, 'F');
      pdf.setDrawColor(...grayColor);
      pdf.setLineWidth(0.3);
      // Draw disk/cylinder shape
      pdf.ellipse(x + 9, yPosition + 6, 4, 1.5, 'S');
      pdf.line(x + 5, yPosition + 6, x + 5, yPosition + 12);
      pdf.line(x + 13, yPosition + 6, x + 13, yPosition + 12);
      pdf.ellipse(x + 9, yPosition + 12, 4, 1.5, 'S');

      // Name
      pdf.setTextColor(...darkColor);
      pdf.setFontSize(7);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(backup.name, cardWidth - 35), x + 18, yPosition + 8);

      // Status badge
      if (backup.backup_status) {
        const statusColor = backup.backup_status === 'active' ? greenColor : grayColor;
        drawBadge(x + cardWidth - 18, yPosition + 6, backup.backup_status, statusColor);
      }

      // Type
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(5.5);
      pdf.setTextColor(...grayColor);
      pdf.text(`Type: ${backup.backup_type}`, x + 18, yPosition + 13);

      // Details
      let detailY = yPosition + 18;
      if (backup.vendor) {
        pdf.text(`Vendor: ${truncateText(backup.vendor, cardWidth - 22)}`, x + 3, detailY);
        detailY += 4;
      }
      if (backup.frequency) {
        pdf.text(`Frequency: ${truncateText(backup.frequency, cardWidth - 22)}`, x + 3, detailY);
        detailY += 4;
      }
      if (backup.storage_location) {
        pdf.text(`Storage: ${truncateText(backup.storage_location, cardWidth - 22)}`, x + 3, detailY);
        detailY += 4;
      }
      if (backup.target_systems) {
        pdf.text(`Targets: ${truncateText(backup.target_systems, cardWidth - 22)}`, x + 3, detailY);
      }
    });

    yPosition += cardHeight + 10;
  }

  // ==================== SOFTWARE ====================
  if (data.software.length > 0) {
    checkPageBreak(40);
    drawSectionBox('Software', 'software');

    const cardsPerRow = 3;
    const cardWidth = (contentWidth - 8) / cardsPerRow;
    const cardHeight = 30;
    const cardGap = 4;

    data.software.forEach((software, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
        checkPageBreak(cardHeight + cardGap);
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card
      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.3);
      pdf.roundedRect(x, yPosition, cardWidth, cardHeight, 2, 2, 'FD');

      // Icon (box/package shape)
      pdf.setFillColor(240, 240, 240);
      pdf.roundedRect(x + 3, yPosition + 3, 12, 12, 1, 1, 'F');
      pdf.setDrawColor(...grayColor);
      pdf.setLineWidth(0.3);
      // Draw a cube/box
      pdf.rect(x + 5, yPosition + 6, 6, 6, 'S');
      pdf.line(x + 5, yPosition + 6, x + 7, yPosition + 4);
      pdf.line(x + 11, yPosition + 6, x + 13, yPosition + 4);
      pdf.line(x + 7, yPosition + 4, x + 13, yPosition + 4);

      // Name
      pdf.setTextColor(...darkColor);
      pdf.setFontSize(7);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(software.name, cardWidth - 20), x + 18, yPosition + 8);

      // Type
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(5.5);
      pdf.setTextColor(...grayColor);
      pdf.text(software.software_type.replace(/_/g, ' '), x + 18, yPosition + 12);

      // Contacts
      let detailY = yPosition + 18;
      if (software.assigned_contacts && software.assigned_contacts.length > 0) {
        software.assigned_contacts.slice(0, 3).forEach(contact => {
          pdf.text(truncateText(contact.contact_name, cardWidth - 12), x + 3, detailY);
          detailY += 3.5;
        });
      }

      // Notes
      if (software.notes && detailY < yPosition + cardHeight - 2) {
        pdf.setFontSize(5);
        pdf.text(truncateText(software.notes, cardWidth - 8), x + 3, detailY);
      }
    });

    yPosition += cardHeight + 10;
  }

  // ==================== VOIP ====================
  if (data.voip.length > 0) {
    checkPageBreak(40);
    drawSectionBox('VoIP Services', 'voip');

    const cardsPerRow = 3;
    const cardWidth = (contentWidth - 8) / cardsPerRow;
    const cardHeight = 28;
    const cardGap = 4;

    data.voip.forEach((voip, index) => {
      const col = index % cardsPerRow;

      if (col === 0 && index > 0) {
        yPosition += cardHeight + cardGap;
        checkPageBreak(cardHeight + cardGap);
      }

      const x = margin + col * (cardWidth + cardGap);

      // Card
      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.3);
      pdf.roundedRect(x, yPosition, cardWidth, cardHeight, 2, 2, 'FD');

      // Phone icon (simple handset shape)
      pdf.setFillColor(240, 240, 240);
      pdf.roundedRect(x + 3, yPosition + 3, 12, 12, 1, 1, 'F');
      pdf.setDrawColor(...grayColor);
      pdf.setLineWidth(0.4);
      // Draw phone handset
      pdf.line(x + 5, yPosition + 6, x + 5, yPosition + 12);
      pdf.line(x + 5, yPosition + 6, x + 8, yPosition + 6);
      pdf.line(x + 8, yPosition + 6, x + 10, yPosition + 8);
      pdf.line(x + 10, yPosition + 8, x + 10, yPosition + 10);
      pdf.line(x + 10, yPosition + 10, x + 8, yPosition + 12);
      pdf.line(x + 8, yPosition + 12, x + 5, yPosition + 12);

      // Name
      pdf.setTextColor(...darkColor);
      pdf.setFontSize(7);
      pdf.setFont('helvetica', 'bold');
      pdf.text(truncateText(voip.name, cardWidth - 20), x + 18, yPosition + 8);

      // Type
      const voipTypeDisplay = voip.voip_type === 'teams' ? 'Microsoft Teams' :
                              voip.voip_type === '3cx' ? '3CX' :
                              voip.voip_type === 'yeastar' ? 'Yeastar' : 'Other';
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(5.5);
      pdf.setTextColor(...grayColor);
      pdf.text(voipTypeDisplay, x + 18, yPosition + 12);

      // Contacts and licenses
      let detailY = yPosition + 18;
      if (voip.assigned_contacts && voip.assigned_contacts.length > 0) {
        const contactNames = voip.assigned_contacts.slice(0, 2).map(c => c.contact_name).join(', ');
        pdf.text(truncateText(contactNames, cardWidth - 10), x + 3, detailY);
        detailY += 3.5;
      }
      if (voip.quantity) {
        pdf.text(`Licenses: ${voip.assigned_count || 0}/${voip.quantity}`, x + 3, detailY);
      }
    });

    yPosition += cardHeight + 10;
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