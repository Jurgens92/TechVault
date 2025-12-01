export interface Organization {
  id: string;
  name: string;
  description: string;
  website: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  description: string;
  address: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
  phone: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Contact {
  id: string;
  organization: string;
  organization_name: string;
  location: string | null;
  location_name: string | null;
  first_name: string;
  last_name: string;
  full_name: string;
  title: string;
  email: string;
  phone: string;
  mobile: string;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Documentation {
  id: string;
  organization: string;
  organization_name: string;
  title: string;
  content: string;
  category: 'procedure' | 'configuration' | 'guide' | 'troubleshooting' | 'policy' | 'other';
  tags: string;
  is_published: boolean;
  version: number;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface PasswordEntry {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  username: string;
  password: string;
  url: string;
  notes: string;
  category: 'account' | 'service' | 'device' | 'other';
  is_encrypted: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Configuration {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  config_type: 'network' | 'server' | 'application' | 'security' | 'backup' | 'other';
  content: string;
  description: string;
  version: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface NetworkDevice {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  device_type: 'firewall' | 'router' | 'firewall_router' | 'switch' | 'wifi' | 'other';
  internet_provider: string;
  internet_speed: string;
  manufacturer: string;
  model: string;
  ip_address: string;
  mac_address: string;
  serial_number: string;
  firmware_version: string;
  location: string | null;
  location_name: string | null;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface EndpointUser {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  device_type: 'desktop' | 'laptop' | 'workstation' | 'other';
  assigned_to: string | null;
  assigned_to_name: string | null;
  manufacturer: string;
  model: string;
  cpu: string;
  ram: string;
  storage: string;
  gpu: string;
  operating_system: string;
  software_installed: string;
  ip_address: string;
  mac_address: string;
  hostname: string;
  serial_number: string;
  purchase_date: string | null;
  warranty_expiry: string | null;
  location: string | null;
  location_name: string | null;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Server {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  server_type: 'physical' | 'virtual' | 'cloud' | 'container' | 'other';
  role: string;
  manufacturer: string;
  model: string;
  cpu: string;
  ram: string;
  storage: string;
  operating_system: string;
  software_installed: string;
  ip_address: string;
  mac_address: string;
  hostname: string;
  serial_number: string;
  location: string | null;
  location_name: string | null;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Peripheral {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  device_type: 'printer' | 'scanner' | 'multifunction' | 'ups' | 'nas' | 'other';
  manufacturer: string;
  model: string;
  ip_address: string;
  mac_address: string;
  serial_number: string;
  location: string | null;
  location_name: string | null;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface SoftwareAssignment {
  id: string;
  contact_id: string;
  contact_name: string;
  contact_email: string;
  created_at: string;
}

export interface Software {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  software_type: 'microsoft365' | 'endpoint_protection' | 'design' | 'development' | 'subscription' | 'other';
  assigned_contact_ids: string[];
  assigned_contacts: SoftwareAssignment[];
  license_key: string;
  version: string;
  license_type: 'perpetual' | 'subscription' | 'trial' | 'free' | 'other';
  purchase_date: string | null;
  expiry_date: string | null;
  vendor: string;
  quantity: number;
  assigned_count: number;
  available_licenses: number;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Backup {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  backup_type: 'server' | 'microsoft365' | 'cloud' | 'endpoint' | 'database' | 'nas' | 'other';
  vendor: string;
  frequency: string;
  retention_period: string;
  storage_location: string;
  storage_capacity: string;
  target_systems: string;
  last_backup_date: string | null;
  next_backup_date: string | null;
  backup_status: 'active' | 'inactive' | 'failed' | 'warning';
  location: string | null;
  location_name: string | null;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface VoIPAssignment {
  id: string;
  contact_id: string;
  contact_name: string;
  contact_email: string;
  extension: string;
  phone_number: string;
  created_at: string;
}

export interface VoIP {
  id: string;
  organization: string;
  organization_name: string;
  name: string;
  voip_type: 'teams' | '3cx' | 'yeastar' | 'other';
  assigned_contact_ids: string[];
  assigned_contacts: VoIPAssignment[];
  license_key: string;
  version: string;
  license_type: 'perpetual' | 'subscription' | 'trial' | 'free' | 'other';
  purchase_date: string | null;
  expiry_date: string | null;
  vendor: string;
  quantity: number;
  phone_numbers: string;
  extensions: string;
  assigned_count: number;
  available_licenses: number;
  notes: string;
  is_active: boolean;
  created_by: {
    id: number;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface DiagramData {
  network_devices: NetworkDevice[];
  endpoint_users: EndpointUser[];
  servers: Server[];
  peripherals: Peripheral[];
  backups: Backup[];
  software: Software[];
  voip: VoIP[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
