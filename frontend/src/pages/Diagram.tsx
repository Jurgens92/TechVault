import { useEffect, useState } from 'react';
import { useOrganization } from '@/contexts/OrganizationContext';
import { diagramAPI } from '@/services/core';
import type { DiagramData } from '@/types/core';
import { Loader2, Network, Monitor, HardDrive, Printer, Globe, Shield, Wifi, Cpu, MemoryStick, Database, FileDown } from 'lucide-react';

export function Diagram() {
  const { selectedOrg } = useOrganization();
  const [data, setData] = useState<DiagramData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDiagramData();
  }, [selectedOrg]);

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

  const handlePrint = () => {
    window.print();
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
          <h1 className="text-3xl font-bold">Network Diagram</h1>
          <p className="text-muted-foreground mt-1">
            Visual representation of your IT infrastructure
          </p>
        </div>
        <button
          onClick={handlePrint}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          <FileDown className="h-4 w-4" />
          Print / Export PDF
        </button>
      </div>

      {data && (
        <div className="space-y-8">
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
        <div className="w-20 h-20 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center">
          <Globe className="h-10 w-10 text-primary" />
        </div>
        <p className="text-sm font-medium mt-2">Internet</p>
      </div>

      {/* Connection Line */}
      {firewalls.length > 0 && (
        <div className="w-0.5 h-12 bg-border"></div>
      )}

      {/* Firewall/Router */}
      {firewalls.length > 0 && (
        <div className="flex flex-col items-center">
          <div className="flex gap-4">
            {firewalls.map((firewall) => (
              <div key={firewall.id} className="flex flex-col items-center">
                <div className="w-24 h-24 rounded-lg bg-accent border-2 border-border flex items-center justify-center hover:border-primary transition-colors">
                  <Shield className="h-12 w-12 text-foreground" />
                </div>
                <div className="mt-2 text-center max-w-[180px]">
                  <p className="text-sm font-medium truncate">
                    {firewall.name}
                  </p>
                  <div className="text-xs space-y-0.5 mt-1">
                    {firewall.manufacturer && (
                      <p className="text-muted-foreground truncate">
                        {firewall.manufacturer} {firewall.model}
                      </p>
                    )}
                    {firewall.internet_provider && (
                      <p className="text-muted-foreground">
                        {firewall.internet_provider} - {firewall.internet_speed}
                      </p>
                    )}
                    {firewall.ip_address && (
                      <p className="font-mono text-muted-foreground">
                        {firewall.ip_address}
                      </p>
                    )}
                    {firewall.firmware_version && (
                      <p className="text-muted-foreground truncate">
                        FW: {firewall.firmware_version}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connection Lines */}
      {(switches.length > 0 || wifiDevices.length > 0) && firewalls.length > 0 && (
        <div className="flex items-center justify-center gap-8">
          <div className="w-0.5 h-12 bg-border"></div>
          <div className="w-0.5 h-12 bg-border"></div>
        </div>
      )}

      {/* Switches and WiFi */}
      <div className="flex gap-12">
        {switches.length > 0 && (
          <div className="flex flex-col items-center">
            <p className="text-sm font-semibold mb-3">Switches</p>
            <div className="grid grid-cols-2 gap-4">
              {switches.map((sw) => (
                <div key={sw.id} className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-lg bg-accent border border-border flex items-center justify-center hover:border-primary transition-colors">
                    <Network className="h-10 w-10 text-foreground" />
                  </div>
                  <div className="mt-1 text-center max-w-[140px]">
                    <p className="text-xs font-medium truncate">{sw.name}</p>
                    <div className="text-xs space-y-0.5 mt-1">
                      {sw.manufacturer && (
                        <p className="text-muted-foreground truncate">
                          {sw.manufacturer}
                        </p>
                      )}
                      {sw.model && (
                        <p className="text-muted-foreground truncate">
                          {sw.model}
                        </p>
                      )}
                      {sw.ip_address && (
                        <p className="font-mono text-muted-foreground text-[10px]">
                          {sw.ip_address}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {wifiDevices.length > 0 && (
          <div className="flex flex-col items-center">
            <p className="text-sm font-semibold mb-3">WiFi Access Points</p>
            <div className="grid grid-cols-2 gap-4">
              {wifiDevices.map((wifi) => (
                <div key={wifi.id} className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-lg bg-accent border border-border flex items-center justify-center hover:border-primary transition-colors">
                    <Wifi className="h-10 w-10 text-foreground" />
                  </div>
                  <div className="mt-1 text-center max-w-[140px]">
                    <p className="text-xs font-medium truncate">{wifi.name}</p>
                    <div className="text-xs space-y-0.5 mt-1">
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
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
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
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {peripherals.map((peripheral) => (
        <div
          key={peripheral.id}
          className="p-4 rounded-lg border border-border hover:border-primary transition-colors bg-card"
        >
          <div className="flex items-start gap-3 mb-3">
            <div className="w-12 h-12 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <Printer className="h-6 w-6 text-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{peripheral.name}</p>
              <div className="mt-1 px-2 py-0.5 rounded text-xs bg-primary/10 text-primary inline-block">
                {peripheral.device_type}
              </div>
            </div>
          </div>

          <div className="space-y-1 text-xs">
            {peripheral.manufacturer && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">Manufacturer:</span>
                <span className="truncate">{peripheral.manufacturer}</span>
              </div>
            )}
            {peripheral.model && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">Model:</span>
                <span className="truncate">{peripheral.model}</span>
              </div>
            )}
            {peripheral.ip_address && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">IP:</span>
                <span className="font-mono">{peripheral.ip_address}</span>
              </div>
            )}
            {peripheral.mac_address && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">MAC:</span>
                <span className="font-mono truncate">{peripheral.mac_address}</span>
              </div>
            )}
            {peripheral.serial_number && (
              <div className="flex items-center gap-1.5">
                <span className="text-muted-foreground">S/N:</span>
                <span className="truncate">{peripheral.serial_number}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
