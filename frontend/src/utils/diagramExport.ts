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
    console.error('Failed to export as PNG:', error);
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
  const margin = 15;
  const contentWidth = pageWidth - margin * 2;
  let yPosition = margin;

  // Colors
  const primaryColor: [number, number, number] = [59, 130, 246]; // Blue
  const darkColor: [number, number, number] = [30, 41, 59]; // Slate-800
  const grayColor: [number, number, number] = [100, 116, 139]; // Slate-500
  const lightGray: [number, number, number] = [241, 245, 249]; // Slate-100

  // Helper function to add a new page if needed
  const checkPageBreak = (requiredSpace: number): void => {
    if (yPosition + requiredSpace > pageHeight - margin) {
      pdf.addPage();
      yPosition = margin;
      addHeader();
    }
  };

  // Helper function to add header on each page
  const addHeader = (): void => {
    pdf.setFillColor(...primaryColor);
    pdf.rect(0, 0, pageWidth, 12, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'bold');
    pdf.text('TechVault', margin, 8);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`${orgName} - IT Infrastructure Diagram`, pageWidth - margin, 8, { align: 'right' });
    yPosition = 20;
  };

  // Helper function to add footer
  const addFooter = (): void => {
    const pageCount = pdf.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFontSize(8);
      pdf.setTextColor(...grayColor);
      pdf.text(
        `Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}`,
        margin,
        pageHeight - 8
      );
      pdf.text(`Page ${i} of ${pageCount}`, pageWidth - margin, pageHeight - 8, { align: 'right' });
    }
  };

  // Add first page header
  addHeader();

  // Title Section
  pdf.setTextColor(...darkColor);
  pdf.setFontSize(24);
  pdf.setFont('helvetica', 'bold');
  pdf.text(orgName, margin, yPosition + 10);
  yPosition += 15;

  pdf.setFontSize(14);
  pdf.setTextColor(...grayColor);
  pdf.setFont('helvetica', 'normal');
  pdf.text('IT Infrastructure Diagram', margin, yPosition + 5);
  yPosition += 15;

  // Summary Box
  pdf.setFillColor(...lightGray);
  pdf.roundedRect(margin, yPosition, contentWidth, 20, 3, 3, 'F');
  pdf.setFontSize(10);
  pdf.setTextColor(...darkColor);

  const summaryItems = [
    `Network Devices: ${data.network_devices.length}`,
    `Servers: ${data.servers.length}`,
    `Endpoints: ${data.endpoint_users.length}`,
    `Peripherals: ${data.peripherals.length}`,
  ];

  const summaryItemWidth = contentWidth / 4;
  summaryItems.forEach((item, index) => {
    pdf.text(item, margin + summaryItemWidth * index + summaryItemWidth / 2, yPosition + 12, {
      align: 'center',
    });
  });

  yPosition += 30;

  // Helper function to draw section header
  const drawSectionHeader = (title: string): void => {
    checkPageBreak(20);
    pdf.setFillColor(...primaryColor);
    pdf.roundedRect(margin, yPosition, contentWidth, 10, 2, 2, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'bold');
    pdf.text(title, margin + 5, yPosition + 7);
    yPosition += 15;
  };

  // Helper function to draw a device card
  const drawDeviceCard = (
    x: number,
    y: number,
    width: number,
    height: number,
    title: string,
    details: { label: string; value: string }[]
  ): void => {
    // Card background
    pdf.setFillColor(255, 255, 255);
    pdf.setDrawColor(200, 200, 200);
    pdf.roundedRect(x, y, width, height, 2, 2, 'FD');

    // Title with proper text wrapping
    pdf.setTextColor(...darkColor);
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'bold');

    // Split title into lines if too long
    const titleLines = pdf.splitTextToSize(title, width - 6);
    const titleHeight = titleLines.length * 4;
    let currentY = y + 6;

    // Only show first 2 lines of title to prevent overflow
    titleLines.slice(0, 2).forEach((line: string) => {
      pdf.text(line, x + 3, currentY);
      currentY += 4;
    });

    // Details
    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(8);
    pdf.setTextColor(...grayColor);

    let detailY = y + Math.min(titleHeight + 6, 14);
    details.forEach((detail) => {
      if (detail.value && detailY < y + height - 3) {
        const text = `${detail.label}: ${detail.value}`;
        // Truncate text if too long
        const lines = pdf.splitTextToSize(text, width - 6);
        if (lines[0]) {
          pdf.text(lines[0], x + 3, detailY);
          detailY += 4;
        }
      }
    });
  };

  // ==================== NETWORK DEVICES ====================
  if (data.network_devices.length > 0) {
    drawSectionHeader(`Network Infrastructure (${data.network_devices.length})`);

    const cardWidth = (contentWidth - 10) / 4;
    const cardHeight = 28;
    const cardsPerRow = 4;

    data.network_devices.forEach((device, index) => {
      const col = index % cardsPerRow;
      const row = Math.floor(index / cardsPerRow);

      if (col === 0 && index > 0) {
        checkPageBreak(cardHeight + 5);
      }

      const x = margin + col * (cardWidth + 3.33);
      const y = yPosition + row * (cardHeight + 3);

      drawDeviceCard(x, y, cardWidth, cardHeight, device.name, [
        { label: 'Type', value: device.device_type },
        { label: 'Manufacturer', value: device.manufacturer || '' },
        { label: 'Model', value: device.model || '' },
        { label: 'IP', value: device.ip_address || '' },
      ]);
    });

    const rows = Math.ceil(data.network_devices.length / cardsPerRow);
    yPosition += rows * (cardHeight + 3) + 10;
  }

  // ==================== SERVERS ====================
  if (data.servers.length > 0) {
    drawSectionHeader(`Servers (${data.servers.length})`);

    const cardWidth = (contentWidth - 10) / 3;
    const cardHeight = 35;
    const cardsPerRow = 3;

    data.servers.forEach((server, index) => {
      const col = index % cardsPerRow;
      const row = Math.floor(index / cardsPerRow);

      if (col === 0 && index > 0) {
        checkPageBreak(cardHeight + 5);
      }

      const x = margin + col * (cardWidth + 5);
      const y = yPosition + row * (cardHeight + 3);

      drawDeviceCard(x, y, cardWidth, cardHeight, server.name, [
        { label: 'Type', value: server.server_type },
        { label: 'Role', value: server.role || '' },
        { label: 'OS', value: server.operating_system || '' },
        { label: 'CPU', value: server.cpu || '' },
        { label: 'RAM', value: server.ram || '' },
        { label: 'IP', value: server.ip_address || '' },
      ]);
    });

    const rows = Math.ceil(data.servers.length / cardsPerRow);
    yPosition += rows * (cardHeight + 3) + 10;
  }

  // ==================== ENDPOINTS ====================
  if (data.endpoint_users.length > 0) {
    drawSectionHeader(`User Endpoints (${data.endpoint_users.length})`);

    const cardWidth = (contentWidth - 10) / 4;
    const cardHeight = 32;
    const cardsPerRow = 4;

    data.endpoint_users.forEach((endpoint, index) => {
      const col = index % cardsPerRow;
      const row = Math.floor(index / cardsPerRow);

      if (col === 0 && index > 0) {
        checkPageBreak(cardHeight + 5);
      }

      const x = margin + col * (cardWidth + 3.33);
      const y = yPosition + row * (cardHeight + 3);

      drawDeviceCard(x, y, cardWidth, cardHeight, endpoint.name, [
        { label: 'Type', value: endpoint.device_type },
        { label: 'User', value: endpoint.assigned_to_name || '' },
        { label: 'OS', value: endpoint.operating_system || '' },
        { label: 'CPU', value: endpoint.cpu || '' },
        { label: 'RAM', value: endpoint.ram || '' },
        { label: 'IP', value: endpoint.ip_address || '' },
      ]);
    });

    const rows = Math.ceil(data.endpoint_users.length / cardsPerRow);
    yPosition += rows * (cardHeight + 3) + 10;
  }

  // ==================== PERIPHERALS ====================
  if (data.peripherals.length > 0) {
    drawSectionHeader(`Peripherals (${data.peripherals.length})`);

    const cardWidth = (contentWidth - 10) / 4;
    const cardHeight = 24;
    const cardsPerRow = 4;

    data.peripherals.forEach((peripheral, index) => {
      const col = index % cardsPerRow;
      const row = Math.floor(index / cardsPerRow);

      if (col === 0 && index > 0) {
        checkPageBreak(cardHeight + 5);
      }

      const x = margin + col * (cardWidth + 3.33);
      const y = yPosition + row * (cardHeight + 3);

      drawDeviceCard(x, y, cardWidth, cardHeight, peripheral.name, [
        { label: 'Type', value: peripheral.device_type },
        { label: 'Manufacturer', value: peripheral.manufacturer || '' },
        { label: 'Model', value: peripheral.model || '' },
        { label: 'Serial', value: peripheral.serial_number || '' },
      ]);
    });
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
<svg width="${width}" height="2000" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title { font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; }
      .section-title { font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; }
      .label { font-family: Arial, sans-serif; font-size: 12px; }
      .device-box { fill: #f0f0f0; stroke: #333; stroke-width: 2; }
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
      const x = 50 + (idx % 3) * 350;
      const y = yOffset + Math.floor(idx / 3) * 120;

      svgContent += `
  <g>
    <rect x="${x}" y="${y}" width="300" height="100" class="device-box" rx="5"/>
    <text x="${x + 10}" y="${y + 25}" class="label" font-weight="bold">${escapeXml(device.name)}</text>
    <text x="${x + 10}" y="${y + 45}" class="label">Type: ${escapeXml(device.device_type)}</text>
    ${device.manufacturer ? `<text x="${x + 10}" y="${y + 60}" class="label">${escapeXml(device.manufacturer)} ${escapeXml(device.model || '')}</text>` : ''}
    ${device.ip_address ? `<text x="${x + 10}" y="${y + 75}" class="label">IP: ${escapeXml(device.ip_address)}</text>` : ''}
  </g>`;
    });

    yOffset += Math.ceil(data.network_devices.length / 3) * 120 + sectionGap;
  }

  // Servers Section
  if (data.servers.length > 0) {
    svgContent += `\n  <!-- Servers -->
  <text x="20" y="${yOffset}" class="section-title">Servers</text>`;
    yOffset += 30;

    data.servers.forEach((server, idx) => {
      const x = 50 + (idx % 3) * 350;
      const y = yOffset + Math.floor(idx / 3) * 120;

      svgContent += `
  <g>
    <rect x="${x}" y="${y}" width="300" height="100" class="device-box" rx="5"/>
    <text x="${x + 10}" y="${y + 25}" class="label" font-weight="bold">${escapeXml(server.name)}</text>
    <text x="${x + 10}" y="${y + 45}" class="label">Type: ${escapeXml(server.server_type)}</text>
    ${server.operating_system ? `<text x="${x + 10}" y="${y + 60}" class="label">OS: ${escapeXml(server.operating_system)}</text>` : ''}
    ${server.ip_address ? `<text x="${x + 10}" y="${y + 75}" class="label">IP: ${escapeXml(server.ip_address)}</text>` : ''}
  </g>`;
    });

    yOffset += Math.ceil(data.servers.length / 3) * 120 + sectionGap;
  }

  // Endpoints Section
  if (data.endpoint_users.length > 0) {
    svgContent += `\n  <!-- User Endpoints -->
  <text x="20" y="${yOffset}" class="section-title">User Endpoints</text>`;
    yOffset += 30;

    const maxEndpoints = Math.min(data.endpoint_users.length, 9);
    data.endpoint_users.slice(0, maxEndpoints).forEach((endpoint, idx) => {
      const x = 50 + (idx % 3) * 350;
      const y = yOffset + Math.floor(idx / 3) * 100;

      svgContent += `
  <g>
    <rect x="${x}" y="${y}" width="300" height="80" class="device-box" rx="5"/>
    <text x="${x + 10}" y="${y + 25}" class="label" font-weight="bold">${escapeXml(endpoint.name)}</text>
    <text x="${x + 10}" y="${y + 45}" class="label">Type: ${escapeXml(endpoint.device_type)}</text>
    ${endpoint.assigned_to_name ? `<text x="${x + 10}" y="${y + 60}" class="label">User: ${escapeXml(endpoint.assigned_to_name)}</text>` : ''}
  </g>`;
    });

    if (data.endpoint_users.length > maxEndpoints) {
      svgContent += `
  <text x="50" y="${yOffset + Math.ceil(maxEndpoints / 3) * 100 + 20}" class="label">... and ${data.endpoint_users.length - maxEndpoints} more endpoints</text>`;
    }

    yOffset += Math.ceil(maxEndpoints / 3) * 100 + sectionGap;
  }

  // Peripherals Section
  if (data.peripherals.length > 0) {
    svgContent += `\n  <!-- Peripherals -->
  <text x="20" y="${yOffset}" class="section-title">Peripherals (${data.peripherals.length})</text>`;
    yOffset += 30;

    const maxPeripherals = Math.min(data.peripherals.length, 6);
    data.peripherals.slice(0, maxPeripherals).forEach((peripheral, idx) => {
      const x = 50 + (idx % 3) * 350;
      const y = yOffset + Math.floor(idx / 3) * 80;

      svgContent += `
  <g>
    <rect x="${x}" y="${y}" width="300" height="60" class="device-box" rx="5"/>
    <text x="${x + 10}" y="${y + 25}" class="label" font-weight="bold">${escapeXml(peripheral.name)}</text>
    <text x="${x + 10}" y="${y + 45}" class="label">${escapeXml(peripheral.device_type)}</text>
  </g>`;
    });

    if (data.peripherals.length > maxPeripherals) {
      svgContent += `
  <text x="50" y="${yOffset + Math.ceil(maxPeripherals / 3) * 80 + 20}" class="label">... and ${data.peripherals.length - maxPeripherals} more peripherals</text>`;
    }
  }

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