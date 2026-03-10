import { useEffect, useState, useRef } from 'react';
import { useOrganization } from '@/contexts/OrganizationContext';
import { diagramAPI, locationAPI } from '@/services/core';
import type { DiagramData, Location } from '@/types/core';
import { Loader2, Network, Monitor, HardDrive, Printer, Globe, Shield, Wifi, Cpu, MemoryStick, Database, FileDown, ChevronDown, Package, User, Phone, MapPin, Pencil, X } from 'lucide-react';
import { exportAsPNG, exportAsJSON, exportAsSVG, exportAsPDF, printDiagram } from '@/utils/diagramExport';
import { NetworkDeviceForm } from '@/pages/NetworkDeviceForm';
import { EndpointUserForm } from '@/pages/EndpointUserForm';
import { ServerForm } from '@/pages/ServerForm';
import { PeripheralForm } from '@/pages/PeripheralForm';
import { BackupForm } from '@/pages/BackupForm';
import { SoftwareForm } from '@/pages/SoftwareForm';
import { VoIPForm } from '@/pages/VoIPForm';

type QuickEditEntity = {
  type: 'network_device' | 'endpoint_user' | 'server' | 'peripheral' | 'backup' | 'software' | 'voip';
  id: string;
  name: string;
} | null;

function QuickEditModal({ entity, onClose, onSaved }: { entity: QuickEditEntity; onClose: () => void; onSaved: () => void }) {
  if (!entity) return null;

  const handleSave = () => {
    onSaved();
    onClose();
  };

  const formProps = {
    editId: entity.id,
    onSave: handleSave,
    onCancel: onClose,
    isModal: true,
  };

  const renderForm = () => {
    switch (entity.type) {
      case 'network_device': return <NetworkDeviceForm {...formProps} />;
      case 'endpoint_user': return <EndpointUserForm {...formProps} />;
      case 'server': return <ServerForm {...formProps} />;
      case 'peripheral': return <PeripheralForm {...formProps} />;
      case 'backup': return <BackupForm {...formProps} />;
      case 'software': return <SoftwareForm {...formProps} />;
      case 'voip': return <VoIPForm {...formProps} />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      {/* Slide-out panel */}
      <div className="relative w-full max-w-2xl bg-background shadow-xl border-l border-border overflow-y-auto animate-in slide-in-from-right duration-300">
        <div className="sticky top-0 z-10 bg-background border-b border-border px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Quick Edit: {entity.name}</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-md hover:bg-accent transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="p-6">
          {renderForm()}
        </div>
      </div>
    </div>
  );
}

function EditButton({ onClick }: { onClick: (e: React.MouseEvent) => void }) {
  return (
    <button
      onClick={onClick}
      className="p-1 rounded-md hover:bg-accent text-muted-foreground hover:text-primary transition-colors print:hidden"
      title="Quick Edit"
    >
      <Pencil className="h-3.5 w-3.5" />
    </button>
  );
}

export function Diagram() {
  const { selectedOrg } = useOrganization();
  const [data, setData] = useState<DiagramData | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null); // null = "All Sites"
  const [loading, setLoading] = useState(true);
  const [locationsLoading, setLocationsLoading] = useState(true);
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [quickEditEntity, setQuickEditEntity] = useState<QuickEditEntity>(null);
  const diagramRef = useRef<HTMLDivElement>(null);

  // Load locations when organization changes
  useEffect(() => {
    loadLocations();
  }, [selectedOrg]);

  // Load diagram data when organization or location changes
  useEffect(() => {
    loadDiagramData();
  }, [selectedOrg, selectedLocation]);

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

  const loadLocations = async () => {
    if (!selectedOrg) {
      setLocations([]);
      setSelectedLocation(null);
      setLocationsLoading(false);
      return;
    }

    try {
      setLocationsLoading(true);
      const response = await locationAPI.byOrganization(selectedOrg.id);
      // Sort by creation date (oldest first)
      const sortedLocations = response.data.sort((a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setLocations(sortedLocations);
      // Reset to "All Sites" when organization changes
      setSelectedLocation(null);
    } catch (error) {
      console.error('Failed to load locations:', error);
      setLocations([]);
    } finally {
      setLocationsLoading(false);
    }
  };

  const loadDiagramData = async (showLoader = true) => {
    if (!selectedOrg) return;

    try {
      if (showLoader) setLoading(true);
      const response = await diagramAPI.getData(
        selectedOrg.id,
        selectedLocation || undefined
      );
      setData(response.data);
    } catch (error) {
      console.error('Failed to load diagram data:', error);
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  const refreshDiagramData = () => loadDiagramData(false);

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
      // Build filename with organization and location name
      const locationName = selectedLocation
        ? locations.find(loc => loc.id === selectedLocation)?.name
        : 'all_sites';
      const sanitizedOrgName = selectedOrg.name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const sanitizedLocationName = locationName?.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const filename = `${sanitizedOrgName}_${sanitizedLocationName}_diagram`;

      // Build display name for PDF/exports
      const displayName = selectedLocation
        ? `${selectedOrg.name} - ${locationName}`
        : selectedOrg.name;

      switch (format) {
        case 'png':
          if (diagramRef.current) {
            await exportAsPNG('diagram-content', filename);
          }
          break;
        case 'json':
          exportAsJSON(data, displayName);
          break;
        case 'svg':
          exportAsSVG(data, displayName);
          break;
        case 'pdf':
          await exportAsPDF(data, displayName);
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
    <div className="p-6 space-y-6">
      {/* Organization name - only visible in print */}
      <div className="hidden print:block">
        <p className="text-sm text-muted-foreground mb-1">Organization:</p>
        <h1 className="text-3xl font-bold mb-2">{selectedOrg.name}</h1>
        <h2 className="text-xl font-semibold">IT Infrastructure Diagram</h2>
        {selectedLocation && (
          <p className="text-lg text-muted-foreground">
            Location: {locations.find(loc => loc.id === selectedLocation)?.name}
          </p>
        )}
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

      {/* Location Tabs - only show if there are locations */}
      {locationsLoading ? (
        <div className="flex justify-center py-4 print:hidden">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </div>
      ) : locations.length > 0 && (
        <div className="border-b border-border print:hidden">
          <div className="flex gap-1 overflow-x-auto">
            {/* All Sites Tab */}
            <button
              onClick={() => setSelectedLocation(null)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                selectedLocation === null
                  ? 'border-primary text-primary font-medium'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
              }`}
            >
              <Globe className="h-4 w-4" />
              All Sites
            </button>

            {/* Individual Location Tabs */}
            {locations.map((location) => (
              <button
                key={location.id}
                onClick={() => setSelectedLocation(location.id)}
                className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                  selectedLocation === location.id
                    ? 'border-primary text-primary font-medium'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                }`}
              >
                <MapPin className="h-4 w-4" />
                {location.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {data && (
        <div id="diagram-content" ref={diagramRef} className="space-y-8">
          {/* Network Infrastructure Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Network className="h-5 w-5" />
              Network Infrastructure
            </h2>
            <NetworkDiagram devices={data.network_devices} onEdit={setQuickEditEntity} />
          </div>

          {/* User Endpoints Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Monitor className="h-5 w-5" />
              User Endpoints
            </h2>
            <UserEndpointsDiagram endpoints={data.endpoint_users} onEdit={setQuickEditEntity} />
          </div>

          {/* Servers Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <HardDrive className="h-5 w-5" />
              Servers
            </h2>
            <ServersDiagram servers={data.servers} onEdit={setQuickEditEntity} />
          </div>

          {/* Peripherals Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Printer className="h-5 w-5" />
              Peripherals
            </h2>
            <PeripheralsDiagram peripherals={data.peripherals} onEdit={setQuickEditEntity} />
          </div>

          {/* Backups Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Database className="h-5 w-5" />
              Backups
            </h2>
            <BackupsDiagram backups={data.backups} onEdit={setQuickEditEntity} />
          </div>

          {/* Software Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Package className="h-5 w-5" />
              Software
            </h2>
            <SoftwareDiagram software={data.software} onEdit={setQuickEditEntity} />
          </div>

          {/* VoIP Diagram */}
          <div className="border border-border rounded-lg p-6 bg-card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Phone className="h-5 w-5" />
              VoIP Services
            </h2>
            <VoIPDiagram voip={data.voip} onEdit={setQuickEditEntity} />
          </div>
        </div>
      )}

      {/* Quick Edit Modal */}
      <QuickEditModal
        entity={quickEditEntity}
        onClose={() => setQuickEditEntity(null)}
        onSaved={refreshDiagramData}
      />
    </div>
  );
}

function NetworkDiagram({ devices, onEdit }: { devices: DiagramData['network_devices']; onEdit: (entity: QuickEditEntity) => void }) {
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
                className="relative flex flex-col items-center p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card min-w-[180px] group"
              >
                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'network_device', id: device.id, name: device.name }); }} />
                </div>
                <div className="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center">
                  <Shield className="h-6 w-6 text-red-500" />
                </div>
                <span className="mt-2 text-sm font-medium text-center">{device.name}</span>
                {device.manufacturer && (
                  <span className="text-xs text-muted-foreground">{device.manufacturer} {device.model}</span>
                )}
                {/* Display multiple ISP connections */}
                {device.internet_connections && device.internet_connections.length > 0 ? (
                  <div className="mt-1 space-y-1">
                    {device.internet_connections.map((conn, idx) => (
                      <div key={idx} className="text-center">
                        <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                          {conn.download_speed}/{conn.upload_speed} Mbps
                          {conn.is_primary && <span className="ml-1 text-green-500">●</span>}
                        </span>
                        <span className="block text-xs text-muted-foreground">
                          {conn.provider_name}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <>
                    {/* Fallback to legacy fields */}
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
                  </>
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
                className="relative flex flex-col items-center p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card min-w-[160px] group"
              >
                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'network_device', id: device.id, name: device.name }); }} />
                </div>
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
                    className="relative flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary transition-colors bg-card group"
                  >
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'network_device', id: wifi.id, name: wifi.name }); }} />
                    </div>
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

function UserEndpointsDiagram({ endpoints, onEdit }: { endpoints: DiagramData['endpoint_users']; onEdit: (entity: QuickEditEntity) => void }) {
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
      className="relative p-3 rounded-lg border border-border hover:border-primary transition-colors bg-card group"
    >
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'endpoint_user', id: endpoint.id, name: endpoint.name }); }} />
      </div>
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
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {laptops.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Laptops ({laptops.length})</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {laptops.map(renderEndpoint)}
          </div>
        </div>
      )}

      {desktops.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Desktops ({desktops.length})</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {desktops.map(renderEndpoint)}
          </div>
        </div>
      )}

      {workstations.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Workstations ({workstations.length})</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {workstations.map(renderEndpoint)}
          </div>
        </div>
      )}
    </div>
  );
}

function ServersDiagram({ servers, onEdit }: { servers: DiagramData['servers']; onEdit: (entity: QuickEditEntity) => void }) {
  if (servers.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No servers configured
      </div>
    );
  }

  // Group servers: physical hosts with their VMs
  const physicalServers = servers.filter(s => s.server_type === 'physical');
  const virtualServers = servers.filter(s => s.server_type === 'virtual' || s.server_type === 'container');
  const otherServers = servers.filter(s => s.server_type !== 'physical' && s.server_type !== 'virtual' && s.server_type !== 'container');

  const renderServerCard = (server: DiagramData['servers'][0], isVm = false) => (
    <div
      key={server.id}
      className={`relative p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card group ${isVm ? 'ml-6 border-l-2 border-l-blue-500' : ''}`}
    >
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'server', id: server.id, name: server.name }); }} />
      </div>
      <div className="flex items-start gap-3 mb-3">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${
          server.server_type === 'physical' ? 'bg-green-500/10' :
          server.server_type === 'virtual' ? 'bg-blue-500/10' : 'bg-accent'
        }`}>
          <HardDrive className={`h-6 w-6 ${
            server.server_type === 'physical' ? 'text-green-500' :
            server.server_type === 'virtual' ? 'text-blue-500' : 'text-foreground'
          }`} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium truncate">{server.name}</p>
          {server.role && (
            <p className="text-xs text-muted-foreground truncate">{server.role}</p>
          )}
          <div className="mt-1 flex flex-wrap gap-1">
            <span className={`px-2 py-0.5 rounded text-xs inline-block ${
              server.server_type === 'physical' ? 'bg-green-500/10 text-green-600 dark:text-green-400' :
              server.server_type === 'virtual' ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400' :
              'bg-primary/10 text-primary'
            }`}>
              {server.server_type}
            </span>
            {server.host_server_name && (
              <span className="px-2 py-0.5 rounded text-xs bg-purple-500/10 text-purple-600 dark:text-purple-400 inline-block">
                Host: {server.host_server_name}
              </span>
            )}
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
        {(server.storage_drives || server.storage) && (
          <div className="flex items-center gap-1.5">
            <Database className="h-3 w-3 text-muted-foreground" />
            <span className="truncate">
              {server.storage_drives || server.storage}
              {server.raid_configuration && ` (${server.raid_configuration})`}
            </span>
          </div>
        )}
        {server.ip_address && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">IP:</span>
            <span className="font-mono">{server.ip_address}</span>
          </div>
        )}
      </div>
    </div>
  );

  // Get VMs that belong to a specific physical host
  const getVmsForHost = (hostId: string) =>
    virtualServers.filter(vm => vm.host_server === hostId);

  // VMs without a host assigned
  const orphanVms = virtualServers.filter(vm => !vm.host_server);

  return (
    <div className="space-y-6">
      {/* Physical Servers with their VMs */}
      {physicalServers.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3 text-green-600 dark:text-green-400">
            Physical Servers ({physicalServers.length})
          </h3>
          <div className="space-y-4">
            {physicalServers.map((server) => {
              const hostedVms = getVmsForHost(server.id);
              return (
                <div key={server.id} className="space-y-2">
                  {renderServerCard(server)}
                  {hostedVms.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs text-muted-foreground ml-6">
                        Virtual Machines ({hostedVms.length})
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {hostedVms.map((vm) => renderServerCard(vm, true))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Orphan VMs (no host assigned) */}
      {orphanVms.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3 text-blue-600 dark:text-blue-400">
            Virtual Servers ({orphanVms.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {orphanVms.map((server) => renderServerCard(server))}
          </div>
        </div>
      )}

      {/* Other servers (cloud, other) */}
      {otherServers.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">
            Other Servers ({otherServers.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {otherServers.map((server) => renderServerCard(server))}
          </div>
        </div>
      )}
    </div>
  );
}

function PeripheralsDiagram({ peripherals, onEdit }: { peripherals: DiagramData['peripherals']; onEdit: (entity: QuickEditEntity) => void }) {
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
          className="relative p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card group"
        >
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'peripheral', id: peripheral.id, name: peripheral.name }); }} />
          </div>
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
function BackupsDiagram({ backups, onEdit }: { backups: DiagramData['backups']; onEdit: (entity: QuickEditEntity) => void }) {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (backups.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No backups configured
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
      {backups.map((backup) => (
        <div
          key={backup.id}
          className="relative p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card group"
        >
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
            <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'backup', id: backup.id, name: backup.name }); }} />
          </div>
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <Database className="h-6 w-6 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-start justify-between gap-2 mb-2">
                <p className="text-sm font-semibold">{backup.name}</p>
                <span className={`text-xs px-2 py-0.5 rounded font-medium whitespace-nowrap ${
                  backup.backup_status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                  backup.backup_status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                  backup.backup_status === 'warning' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                }`}>
                  {backup.backup_status}
                </span>
              </div>

              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">
                  <span className="font-medium">Type:</span> <span className="capitalize">{backup.backup_type.replace(/_/g, ' ')}</span>
                </p>
                {backup.vendor && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Vendor:</span> {backup.vendor}
                  </p>
                )}
                {backup.frequency && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Frequency:</span> {backup.frequency}
                  </p>
                )}
                {backup.retention_period && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Retention:</span> {backup.retention_period}
                  </p>
                )}
                {backup.storage_location && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Storage:</span> {backup.storage_location}
                  </p>
                )}
                {backup.storage_capacity && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Capacity:</span> {backup.storage_capacity}
                  </p>
                )}
                {backup.last_backup_date && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Last Backup:</span> {formatDate(backup.last_backup_date)}
                  </p>
                )}
                {backup.target_systems && (
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    <span className="font-medium">Targets:</span> {backup.target_systems}
                  </p>
                )}
     
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Software Diagram Component
function SoftwareDiagram({ software, onEdit }: { software: DiagramData['software']; onEdit: (entity: QuickEditEntity) => void }) {
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
          className="relative p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card group"
        >
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'software', id: item.id, name: item.name }); }} />
          </div>
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <Package className="h-5 w-5 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{item.name}</p>
              <p className="text-xs text-muted-foreground capitalize">
                {item.software_type.replace(/_/g, ' ')}
              </p>

              {item.assigned_contacts && (
                <div className="mt-1 space-y-1">
                  {item.assigned_contacts.map((c, idx) => (
                    <div key={idx} className="flex items-center gap-1">
                      <User className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                      <p className="text-xs text-muted-foreground truncate">
                        {c.contact_name}
                      </p>
                    </div>
                  ))}
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

// VoIP Diagram Component
function VoIPDiagram({ voip, onEdit }: { voip: DiagramData['voip']; onEdit: (entity: QuickEditEntity) => void }) {
  if (voip.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No VoIP services configured
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {voip.map((item) => (
        <div
          key={item.id}
          className="relative p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card group"
        >
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <EditButton onClick={(e) => { e.stopPropagation(); onEdit({ type: 'voip', id: item.id, name: item.name }); }} />
          </div>
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <Phone className="h-5 w-5 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{item.name}</p>
              <p className="text-xs text-muted-foreground capitalize">
                {item.voip_type === 'teams' ? 'Microsoft Teams' :
                 item.voip_type === '3cx' ? '3CX' :
                 item.voip_type === 'yeastar' ? 'Yeastar' :
                 'Other'}
              </p>

              {item.assigned_contacts && item.assigned_contacts.length > 0 && (
                <div className="mt-2 space-y-1">
                  {item.assigned_contacts.map((c, idx) => (
                    <div key={idx} className="flex items-center gap-1">
                      <User className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                      <p className="text-xs text-muted-foreground truncate">
                        {c.contact_name}
                        {c.extension && ` • Ext: ${c.extension}`}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {item.phone_numbers && (
                <p className="text-xs text-muted-foreground mt-2">
                  <span className="font-medium">Numbers:</span> {item.phone_numbers}
                </p>
              )}

              {item.quantity && (
                <p className="text-xs text-muted-foreground mt-1">
                  <span className="font-medium">Licenses:</span> {item.assigned_count || 0}/{item.quantity}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}