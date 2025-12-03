import api from './api';

export interface ReportRequest {
  organization_id?: string;
  location_id?: string;
  include_sections?: string[];
  format: 'json' | 'excel' | 'csv' | 'pdf';
}

export interface ReportData {
  report_type: string;
  generated_at: string;
  generated_by: string;
  organization?: {
    id: string;
    name: string;
    [key: string]: any;
  };
  location?: {
    id: string;
    name: string;
    [key: string]: any;
  };
  sections?: Record<string, any[]>;
  summary?: Record<string, number>;
  assets?: Record<string, any[]>;
  licenses?: any[];
  totals?: Record<string, number>;
}

export const reportsAPI = {
  /**
   * Generate an organization report
   */
  generateOrganizationReport: (data: ReportRequest) => {
    if (data.format === 'json') {
      return api.post<ReportData>('/api/reports/organization/', data);
    } else {
      return api.post('/api/reports/organization/', data, {
        responseType: 'blob'
      });
    }
  },

  /**
   * Generate a location report
   */
  generateLocationReport: (data: ReportRequest) => {
    if (data.format === 'json') {
      return api.post<ReportData>('/api/reports/location/', data);
    } else {
      return api.post('/api/reports/location/', data, {
        responseType: 'blob'
      });
    }
  },

  /**
   * Generate an asset inventory report
   */
  generateAssetInventoryReport: (data: ReportRequest) => {
    if (data.format === 'json') {
      return api.post<ReportData>('/api/reports/asset-inventory/', data);
    } else {
      return api.post('/api/reports/asset-inventory/', data, {
        responseType: 'blob'
      });
    }
  },

  /**
   * Generate a software license report
   */
  generateSoftwareLicenseReport: (data: ReportRequest) => {
    if (data.format === 'json') {
      return api.post<ReportData>('/api/reports/software-licenses/', data);
    } else {
      return api.post('/api/reports/software-licenses/', data, {
        responseType: 'blob'
      });
    }
  },
};

/**
 * Helper function to download a blob as a file
 */
export const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
