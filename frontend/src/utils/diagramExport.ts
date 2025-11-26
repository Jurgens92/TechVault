import html2canvas from 'html2canvas';
import type { DiagramData } from '@/types/core';

export type ExportFormat = 'png' | 'json' | 'svg' | 'print';

/**
 * Export diagram as PNG image
 */
export async function exportAsPNG(elementId: string, filename: string): Promise<void> {
  const element = document.getElementById(elementId);
  if (!element) {
    throw new Error('Diagram element not found');
  }

  try {
    // Capture the element as canvas with high quality settings
    const canvas = await html2canvas(element, {
      scale: 2, // Higher resolution
      backgroundColor: '#ffffff',
      logging: false,
      useCORS: true,
      allowTaint: true,
    });

    // Convert canvas to blob and download
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

  // User Endpoints Section
  if (data.endpoint_users.length > 0) {
    svgContent += `\n  <!-- User Endpoints -->
  <text x="20" y="${yOffset}" class="section-title">User Endpoints (${data.endpoint_users.length})</text>`;
    yOffset += 30;

    const maxEndpoints = Math.min(data.endpoint_users.length, 9); // Limit for space
    data.endpoint_users.slice(0, maxEndpoints).forEach((endpoint, idx) => {
      const x = 50 + (idx % 3) * 350;
      const y = yOffset + Math.floor(idx / 3) * 100;

      svgContent += `
  <g>
    <rect x="${x}" y="${y}" width="300" height="80" class="device-box" rx="5"/>
    <text x="${x + 10}" y="${y + 25}" class="label" font-weight="bold">${escapeXml(endpoint.name)}</text>
    <text x="${x + 10}" y="${y + 45}" class="label">${escapeXml(endpoint.device_type)}</text>
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

/**
 * Trigger browser print dialog
 */
export function printDiagram(): void {
  window.print();
}
