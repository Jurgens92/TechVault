import { useEffect, useState, useRef } from 'react';
import { useOrganization } from '@/contexts/OrganizationContext';
import { diagramAPI } from '@/services/core';
import type { DiagramData } from '@/types/core';
import { Loader2, Network, Monitor, HardDrive, Printer, Globe, Shield, Wifi, Cpu, MemoryStick, Database, FileDown, ChevronDown, Package, User } from 'lucide-react';
import { exportAsPNG, exportAsJSON, exportAsSVG, exportAsPDF, printDiagram } from '@/utils/diagramExport';

export function Diagram() {
  const { selectedOrg } = useOrganization();
  const [data, setData] = useState<DiagramData | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const diagramRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadDiagramData();
  }, [selectedOrg]);

  useEffect(() => {
    // Close export menu when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (exportMenuOpen && !target.closest('.relative')) {
        setExportMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [exportMenuOpen]);

  const loadDiagramData = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const response = await diagramAPI.getData(selectedOrg.id);
      setData(response.data);
    } catch (error) {
      console.error('Failed to load diagram data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedOrg) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-muted-foreground">Please select an organization to view diagram</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  const handleExport = async (format: 'png' | 'json' | 'svg' | 'pdf' | 'print') => {
    if (!data || !selectedOrg) return;

    setExporting(true);
    setExportMenuOpen(false);

    try {
      const filename = `${selectedOrg.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_diagram`;

      switch (format) {
        case 'png':
          if (diagramRef.current) {
            await exportAsPNG('diagram-content', filename);
          }
          break;
        case 'json':
          exportAsJSON(data, selectedOrg.name);
          break;
        case 'svg':
          exportAsSVG(data, selectedOrg.name);
          break;
        case 'pdf':
          await exportAsPDF(data, selectedOrg.name);
          break;
        case 'print':
          printDiagram();
          break;
      }
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export diagram. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="p-6 space-y-8">
      {/* Organization name - only visible in print */}
      <div className="hidden print:block">
        <p className="text-sm text-muted-foreground mb-1">Organization:</p>
        <h1 className="text-3xl font-bold mb-2">{selectedOrg.name}</h1>
        <h2 className="text-xl font-semibold">IT Infrastructure Diagram</h2>
      </div>

      {/* Screen header */}
      <div className="flex justify-between items-start print:hidden">
        <div>
          <h1 className="text-3xl font-bold">Infrastructure Diagram</h1>
          <p className="text-muted-foreground mt-1">
            Visual representation of your IT infrastructure
          </p>
        </div>

        {/* Export Menu */}
        <div className="relative">
          <button
            onClick={() => setExportMenuOpen(!exportMenuOpen)}
            disabled={exporting}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {exporting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <FileDown className="h-4 w-4" />
                Export
                <ChevronDown className="h-4 w-4" />
              </>
            )}
          </button>

          {/* Dropdown Menu */}
          {exportMenuOpen && !exporting && (
            <div className="absolute right-0 mt-2 w-56 bg-card border border-border rounded-lg shadow-lg z-10">
              <div className="py-1">
                <button
                  onClick={() => handleExport('pdf')}
                  className="w-full text-left px-4 py-2 hover:bg-accent transition-colors flex items-center gap-3"
                >
                  <FileDown className="h-4 w-4" />
                  <div>
                    <div className="font-medium">Export as PDF</div>
                    <div className="text-xs text-muted-foreground">Professional document</div>
                  </div>
                </button>


                <button
                  onClick={() => handleExport('json')}
                  className="w-full text-left px-4 py-2 hover:bg-accent transition-colors flex items-center gap-3"
                >
                  <FileDown className="h-4 w-4" />
                  <div>
                    <div className="font-medium">Export as JSON</div>
                    <div className="text-xs text-muted-foreground">Raw data export</div>
                  </div>
                </button>

              </div>
            </div>
          )}
        </div>
      </div>

      {data && (
        <div id="diagram-content" ref={diagramRef} className="space-y-8">
          {/* Network Infrastructure Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Network className="h-5 w-5" />
              Network Infrastructure
            </h2>
            <NetworkDiagram devices={data.network_devices} />
          </div>

          {/* User Endpoints Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Monitor className="h-5 w-5" />
              User Endpoints
            </h2>
            <UserEndpointsDiagram endpoints={data.endpoint_users} />
          </div>

          {/* Servers Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <HardDrive className="h-5 w-5" />
              Servers
            </h2>
            <ServersDiagram servers={data.servers} />
          </div>

          {/* Peripherals Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Printer className="h-5 w-5" />
              Peripherals
            </h2>
            <PeripheralsDiagram peripherals={data.peripherals} />
          </div>

          {/* Backups Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Database className="h-5 w-5" />
              Backups
            </h2>
            <BackupsDiagram backups={data.backups} />
          </div>

          {/* Software Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Package className="h-5 w-5" />
              Software
            </h2>
            <SoftwareDiagram software={data.software} />
          </div>
        </div>
      )}
    </div>
  );
}

function NetworkDiagram({ devices }: { devices: DiagramData['network_devices'] }) {
  const firewalls = devices.filter((d) => d.device_type === 'firewall' || d.device_type === 'firewall_router' || d.device_type === 'router');
  const switches = devices.filter((d) => d.device_type === 'switch');
  const wifiDevices = devices.filter((d) => d.device_type === 'wifi');

  if (devices.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No network devices configured
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center space-y-6">
      {/* Internet */}
      <div className="flex flex-col items-center">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
          <Globe className="h-10 w-10 text-white" />
        </div>
        <span className="mt-2 text-sm font-medium">Internet</span>
      </div>

      {/* Connection line */}
      <div className="w-0.5 h-8 bg-border" />

      {/* Firewalls/Routers Layer */}
      {firewalls.length > 0 && (
        <div className="flex flex-col items-center w-full">
          <div className="flex flex-wrap justify-center gap-4">
            {firewalls.map((device) => (
              <div
                key={device.id}
                className="flex flex-col items-center p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card min-w-[180px]"
              >
                <div className="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center">
                  <Shield className="h-6 w-6 text-red-500" />
                </div>
                <span className="mt-2 text-sm font-medium text-center">{device.name}</span>
                {device.manufacturer && (
                  <span className="text-xs text-muted-foreground">{device.manufacturer}</span>
                )}
                {device.internet_speed && (
                  <span className="text-xs font-medium text-blue-600 dark:text-blue-400 mt-1">
                    {device.internet_speed}
                  </span>
                )}
                {device.internet_provider && (
                  <span className="text-xs text-muted-foreground">
                    {device.internet_provider}
                  </span>
                )}
                {device.ip_address && (
                  <span className="text-xs font-mono text-muted-foreground mt-1">{device.ip_address}</span>
                )}
              </div>
            ))}
          </div>
          <div className="w-0.5 h-8 bg-border mt-4" />
        </div>
      )}

      {/* Switches Layer */}
      {switches.length > 0 && (
        <div className="flex flex-col items-center w-full">
          <div className="flex flex-wrap justify-center gap-4">
            {switches.map((device) => (
              <div
                key={device.id}
                className="flex flex-col items-center p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card min-w-[160px]"
              >
                <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
                  <Network className="h-6 w-6 text-green-500" />
                </div>
                <span className="mt-2 text-sm font-medium text-center">{device.name}</span>
                {device.manufacturer && (
                  <span className="text-xs text-muted-foreground">{device.manufacturer}</span>
                )}
                {device.ip_address && (
                  <span className="text-xs font-mono text-muted-foreground mt-1">{device.ip_address}</span>
                )}
              </div>
            ))}
          </div>

          {/* WiFi Devices */}
          {wifiDevices.length > 0 && (
            <div className="mt-6 w-full">
              <div className="flex flex-wrap justify-center gap-4">
                {wifiDevices.map((wifi) => (
                  <div
                    key={wifi.id}
                    className="flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary transition-colors bg-card"
                  >
                    <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center flex-shrink-0">
                      <Wifi className="h-5 w-5 text-purple-500" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{wifi.name}</p>
                      {wifi.manufacturer && (
                        <p className="text-muted-foreground truncate">
                          {wifi.manufacturer}
                        </p>
                      )}
                      {wifi.model && (
                        <p className="text-muted-foreground truncate">
                          {wifi.model}
                        </p>
                      )}
                      {wifi.ip_address && (
                        <p className="font-mono text-muted-foreground text-[10px]">
                          {wifi.ip_address}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function UserEndpointsDiagram({ endpoints }: { endpoints: DiagramData['endpoint_users'] }) {
  const desktops = endpoints.filter((e) => e.device_type === 'desktop');
  const laptops = endpoints.filter((e) => e.device_type === 'laptop');
  const workstations = endpoints.filter((e) => e.device_type === 'workstation');

  if (endpoints.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No user endpoints configured
      </div>
    );
  }

  const renderEndpoint = (endpoint: DiagramData['endpoint_users'][0]) => (
    <div
      key={endpoint.id}
      className="p-3 rounded-lg border border-border hover:border-primary transition-colors bg-card"
    >
      <div className="flex items-start gap-2 mb-2">
        <Monitor className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium truncate">{endpoint.name}</p>
          {endpoint.assigned_to_name && (
            <p className="text-xs text-muted-foreground truncate">
              👤 {endpoint.assigned_to_name}
            </p>
          )}
        </div>
      </div>

      <div className="space-y-1 text-xs">
        {endpoint.operating_system && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">OS:</span>
            <span className="font-medium">{endpoint.operating_system}</span>
          </div>
        )}
        {endpoint.cpu && (
          <div className="flex items-center gap-1.5">
            <Cpu className="h-3 w-3 text-muted-foreground" />
            <span className="truncate">{endpoint.cpu}</span>
          </div>
        )}
        {endpoint.ram && (
          <div className="flex items-center gap-1.5">
            <MemoryStick className="h-3 w-3 text-muted-foreground" />
            <span className="truncate">{endpoint.ram}</span>
          </div>
        )}
        {endpoint.storage && (
          <div className="flex items-center gap-1.5">
            <Database className="h-3 w-3 text-muted-foreground" />
            <span className="truncate">{endpoint.storage}</span>
          </div>
        )}
        {endpoint.gpu && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">GPU:</span>
            <span className="truncate">{endpoint.gpu}</span>
          </div>
        )}
        {endpoint.ip_address && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">IP:</span>
            <span className="font-mono">{endpoint.ip_address}</span>
          </div>
        )}
        {endpoint.hostname && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">Host:</span>
            <span className="font-mono truncate">{endpoint.hostname}</span>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {desktops.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Desktops ({desktops.length})</h3>
          <div className="space-y-3">
            {desktops.map(renderEndpoint)}
          </div>
        </div>
      )}

      {laptops.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Laptops ({laptops.length})</h3>
          <div className="space-y-3">
            {laptops.map(renderEndpoint)}
          </div>
        </div>
      )}

      {workstations.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Workstations ({workstations.length})</h3>
          <div className="space-y-3">
            {workstations.map(renderEndpoint)}
          </div>
        </div>
      )}
    </div>
  );
}

function ServersDiagram({ servers }: { servers: DiagramData['servers'] }) {
  if (servers.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No servers configured
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {servers.map((server) => (
        <div
          key={server.id}
          className="p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card"
        >
          <div className="flex items-start gap-3 mb-3">
            <div className="w-12 h-12 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <HardDrive className="h-6 w-6 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{server.name}</p>
              {server.role && (
                <p className="text-xs text-muted-foreground truncate">{server.role}</p>
              )}
              <div className="mt-1 px-2 py-0.5 rounded text-xs bg-primary/10 text-primary inline-block">
                {server.server_type}
              </div>
            </div>
          </div>

          <div className="space-y-1 text-xs">
            {server.operating_system && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">OS:</span>
                <span className="font-medium">{server.operating_system}</span>
              </div>
            )}
            {server.cpu && (
              <div className="flex items-center gap-1.5">
                <Cpu className="h-3 w-3 text-muted-foreground" />
                <span className="truncate">{server.cpu}</span>
              </div>
            )}
            {server.ram && (
              <div className="flex items-center gap-1.5">
                <MemoryStick className="h-3 w-3 text-muted-foreground" />
                <span className="truncate">{server.ram}</span>
              </div>
            )}
            {server.storage && (
              <div className="flex items-center gap-1.5">
                <Database className="h-3 w-3 text-muted-foreground" />
                <span className="truncate">{server.storage}</span>
              </div>
            )}
            {server.ip_address && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">IP:</span>
                <span className="font-mono">{server.ip_address}</span>
              </div>
            )}
            {server.hostname && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">Host:</span>
                <span className="font-mono truncate">{server.hostname}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function PeripheralsDiagram({ peripherals }: { peripherals: DiagramData['peripherals'] }) {
  if (peripherals.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No peripherals configured
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {peripherals.map((peripheral) => (
        <div
          key={peripheral.id}
          className="p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card"
        >
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <Printer className="h-5 w-5 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{peripheral.name}</p>
              <p className="text-xs text-muted-foreground">{peripheral.device_type}</p>
              {peripheral.manufacturer && (
                <p className="text-xs text-muted-foreground truncate">
                  {peripheral.manufacturer} {peripheral.model || ''}
                </p>
              )}
              {peripheral.serial_number && (
                <p className="text-xs font-mono text-muted-foreground mt-1">
                  S/N: {peripheral.serial_number}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Backups Diagram Component
function BackupsDiagram({ backups }: { backups: DiagramData['backups'] }) {
  if (backups.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No backups configured
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {backups.map((backup) => (
        <div
          key={backup.id}
          className="p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card"
        >
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <Database className="h-5 w-5 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{backup.name}</p>
              <p className="text-xs text-muted-foreground capitalize">
                {backup.backup_type.replace(/_/g, ' ')}
              </p>
              {backup.vendor && (
                <p className="text-xs text-muted-foreground truncate mt-1">
                  {backup.vendor}
                </p>
              )}
              {backup.frequency && (
                <p className="text-xs text-muted-foreground mt-1">
                  {backup.frequency}
                </p>
              )}
              {backup.storage_location && (
                <p className="text-xs text-muted-foreground truncate mt-1">
                  {backup.storage_location}
                </p>
              )}
              {backup.backup_status && (
                <div className="mt-2">
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    backup.backup_status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    backup.backup_status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                    backup.backup_status === 'warning' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                  }`}>
                    {backup.backup_status}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Software Diagram Component
function SoftwareDiagram({ software }: { software: DiagramData['software'] }) {
  if (software.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No software configured
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {software.map((item) => (
        <div
          key={item.id}
          className="p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card"
        >
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <Package className="h-5 w-5 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{item.name}</p>
              <p className="text-xs text-muted-foreground capitalize">
                {item.software_type.replace(/_/g, ' ')}
              </p>
              {item.assigned_to_name && (
                <div className="flex items-center gap-1 mt-1">
                  <User className="h-3 w-3 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground truncate">
                    {item.assigned_to_name}
                  </p>
                </div>
              )}
              {item.notes && (
                <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                  {item.notes}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}