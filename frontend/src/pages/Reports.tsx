import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Checkbox } from '@/components/ui/Checkbox';
import {
  FileText,
  Download,
  Building2,
  MapPin,
  Package,
  Key,
  FileSpreadsheet,
  FileType,
  File
} from 'lucide-react';
import { organizationAPI, locationAPI } from '@/services/core';
import { reportsAPI, downloadBlob, ReportData, ReportRequest } from '@/services/reports';
import { Organization, Location } from '@/types/core';

type ReportType = 'organization' | 'location' | 'asset_inventory' | 'software_licenses';
type ExportFormat = 'json' | 'excel' | 'csv' | 'pdf';

const Reports: React.FC = () => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedOrganization, setSelectedOrganization] = useState<string>('');
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [reportType, setReportType] = useState<ReportType>('organization');
  const [exportFormat, setExportFormat] = useState<ExportFormat>('excel');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState<ReportData | null>(null);

  // Section checkboxes for organization/location reports
  const [selectedSections, setSelectedSections] = useState<Record<string, boolean>>({
    locations: true,
    contacts: true,
    network_devices: true,
    servers: true,
    endpoints: true,
    peripherals: true,
    software: true,
    voip: true,
    backups: true,
    documentation: true,
    configurations: true,
    passwords: true,
  });

  useEffect(() => {
    fetchOrganizations();
  }, []);

  useEffect(() => {
    if (selectedOrganization) {
      fetchLocations(selectedOrganization);
    } else {
      setLocations([]);
      setSelectedLocation('');
    }
  }, [selectedOrganization]);

  const fetchOrganizations = async () => {
    try {
      const response = await organizationAPI.getAll({ page_size: 1000 });
      setOrganizations(response.data.results);
    } catch (error) {
      console.error('Error fetching organizations:', error);
    }
  };

  const fetchLocations = async (orgId: string) => {
    try {
      const response = await locationAPI.byOrganization(orgId);
      setLocations(response.data);
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
  };

  const handleSectionToggle = (section: string) => {
    setSelectedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getSelectedSections = () => {
    return Object.keys(selectedSections).filter(key => selectedSections[key]);
  };

  const generateReport = async () => {
    setLoading(true);
    setReportData(null);

    try {
      let request: ReportRequest = {
        format: exportFormat,
      };

      let response: any;

      switch (reportType) {
        case 'organization':
          if (!selectedOrganization) {
            alert('Please select an organization');
            return;
          }
          request.organization_id = selectedOrganization;
          request.include_sections = getSelectedSections();
          response = await reportsAPI.generateOrganizationReport(request);
          break;

        case 'location':
          if (!selectedLocation) {
            alert('Please select a location');
            return;
          }
          request.location_id = selectedLocation;
          request.include_sections = getSelectedSections();
          response = await reportsAPI.generateLocationReport(request);
          break;

        case 'asset_inventory':
          request.organization_id = selectedOrganization || undefined;
          request.location_id = selectedLocation || undefined;
          response = await reportsAPI.generateAssetInventoryReport(request);
          break;

        case 'software_licenses':
          request.organization_id = selectedOrganization || undefined;
          response = await reportsAPI.generateSoftwareLicenseReport(request);
          break;
      }

      // Handle different response types
      if (exportFormat === 'json') {
        setReportData(response.data);
      } else {
        // For file downloads (excel, csv, pdf)
        const blob = new Blob([response.data], {
          type: response.headers['content-type']
        });
        const filename = `${reportType}_report_${new Date().toISOString()}.${exportFormat === 'excel' ? 'xlsx' : exportFormat}`;
        downloadBlob(blob, filename);
      }
    } catch (error: any) {
      console.error('Error generating report:', error);
      alert(`Error generating report: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const reportTypes = [
    {
      value: 'organization',
      label: 'Organization Report',
      description: 'Comprehensive report for an entire organization',
      icon: Building2,
      requiresOrg: true,
      requiresLoc: false
    },
    {
      value: 'location',
      label: 'Location Report',
      description: 'Detailed report for a specific location',
      icon: MapPin,
      requiresOrg: false,
      requiresLoc: true
    },
    {
      value: 'asset_inventory',
      label: 'Asset Inventory',
      description: 'Complete inventory of all IT assets',
      icon: Package,
      requiresOrg: false,
      requiresLoc: false
    },
    {
      value: 'software_licenses',
      label: 'Software Licenses',
      description: 'License tracking and expiration report',
      icon: Key,
      requiresOrg: false,
      requiresLoc: false
    },
  ];

  const exportFormats = [
    { value: 'excel', label: 'Excel (.xlsx)', icon: FileSpreadsheet },
    { value: 'csv', label: 'CSV (.csv)', icon: FileType },
    { value: 'pdf', label: 'PDF (.pdf)', icon: File },
    { value: 'json', label: 'JSON (Preview)', icon: FileText },
  ];

  const selectedReportType = reportTypes.find(rt => rt.value === reportType);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Reports</h1>
            <p className="text-muted-foreground">
              Generate and export comprehensive reports for clients and internal use
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Configuration */}
        <div className="lg:col-span-2 space-y-6">
          {/* Report Type Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Report Type</CardTitle>
              <CardDescription>Select the type of report you want to generate</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {reportTypes.map((type) => {
                  const Icon = type.icon;
                  return (
                    <button
                      key={type.value}
                      onClick={() => setReportType(type.value as ReportType)}
                      className={`
                        p-4 rounded-lg border-2 text-left transition-all
                        ${reportType === type.value
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50 hover:bg-muted/50'
                        }
                      `}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className={`h-6 w-6 mt-0.5 ${reportType === type.value ? 'text-primary' : 'text-muted-foreground'}`} />
                        <div>
                          <div className="font-semibold">{type.label}</div>
                          <div className="text-sm text-muted-foreground mt-1">{type.description}</div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Filters</CardTitle>
              <CardDescription>Select the scope of your report</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Organization Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Organization {selectedReportType?.requiresOrg && <span className="text-red-500">*</span>}
                </label>
                <select
                  value={selectedOrganization}
                  onChange={(e) => setSelectedOrganization(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                >
                  <option value="">Select an organization...</option>
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>{org.name}</option>
                  ))}
                </select>
              </div>

              {/* Location Selection */}
              {selectedOrganization && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Location {selectedReportType?.requiresLoc && <span className="text-red-500">*</span>}
                  </label>
                  <select
                    value={selectedLocation}
                    onChange={(e) => setSelectedLocation(e.target.value)}
                    className="w-full px-3 py-2 border border-border rounded-md bg-background"
                    disabled={locations.length === 0}
                  >
                    <option value="">All locations...</option>
                    {locations.map((loc) => (
                      <option key={loc.id} value={loc.id}>{loc.name}</option>
                    ))}
                  </select>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Section Selection (for organization and location reports) */}
          {(reportType === 'organization' || reportType === 'location') && (
            <Card>
              <CardHeader>
                <CardTitle>Report Sections</CardTitle>
                <CardDescription>Choose which sections to include in the report</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.keys(selectedSections).map((section) => (
                    <label key={section} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedSections[section]}
                        onChange={() => handleSectionToggle(section)}
                        className="w-4 h-4 text-primary border-border rounded focus:ring-primary"
                      />
                      <span className="text-sm">{section.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                    </label>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Export Options */}
        <div className="space-y-6">
          {/* Export Format */}
          <Card>
            <CardHeader>
              <CardTitle>Export Format</CardTitle>
              <CardDescription>Choose how to export your report</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {exportFormats.map((format) => {
                const Icon = format.icon;
                return (
                  <button
                    key={format.value}
                    onClick={() => setExportFormat(format.value as ExportFormat)}
                    className={`
                      w-full p-3 rounded-lg border text-left transition-all flex items-center gap-3
                      ${exportFormat === format.value
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50 hover:bg-muted/50'
                      }
                    `}
                  >
                    <Icon className={`h-5 w-5 ${exportFormat === format.value ? 'text-primary' : 'text-muted-foreground'}`} />
                    <span className="font-medium">{format.label}</span>
                  </button>
                );
              })}
            </CardContent>
          </Card>

          {/* Generate Button */}
          <Button
            onClick={generateReport}
            disabled={loading}
            className="w-full py-6 text-lg"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Generating...
              </>
            ) : (
              <>
                <Download className="mr-2 h-5 w-5" />
                Generate Report
              </>
            )}
          </Button>
        </div>
      </div>

      {/* JSON Preview */}
      {reportData && exportFormat === 'json' && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Report Preview</CardTitle>
            <CardDescription>JSON representation of the generated report</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-96 text-sm">
              {JSON.stringify(reportData, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Reports;
