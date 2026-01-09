/**
 * Choice Types - Auto-generated from backend constants
 *
 * These types represent the choices/enums fetched from /api/meta/choices/
 * This ensures frontend and backend stay in sync (Single Source of Truth).
 */

export interface Choice {
  value: string;
  label: string;
}

export interface Choices {
  documentation_category: Choice[];
  password_category: Choice[];
  configuration_type: Choice[];
  network_device_type: Choice[];
  endpoint_device_type: Choice[];
  server_type: Choice[];
  peripheral_type: Choice[];
  software_type: Choice[];
  license_type: Choice[];
  backup_type: Choice[];
  backup_status: Choice[];
  voip_type: Choice[];
}

// Type-safe choice value types (derived from backend constants)
export type DocumentationCategoryValue = 'procedure' | 'configuration' | 'guide' | 'troubleshooting' | 'policy' | 'other';
export type PasswordCategoryValue = 'account' | 'service' | 'device' | 'other';
export type ConfigurationTypeValue = 'network' | 'server' | 'application' | 'security' | 'backup' | 'other';
export type NetworkDeviceTypeValue = 'firewall' | 'router' | 'firewall_router' | 'switch' | 'wifi' | 'other';
export type EndpointDeviceTypeValue = 'desktop' | 'laptop' | 'workstation' | 'other';
export type ServerTypeValue = 'physical' | 'virtual' | 'cloud' | 'container' | 'other';
export type PeripheralTypeValue = 'printer' | 'scanner' | 'multifunction' | 'ups' | 'nas' | 'other';
export type SoftwareTypeValue = 'microsoft365' | 'endpoint_protection' | 'design' | 'development' | 'subscription' | 'other';
export type LicenseTypeValue = 'perpetual' | 'subscription' | 'trial' | 'free' | 'other';
export type BackupTypeValue = 'server' | 'microsoft365' | 'cloud' | 'endpoint' | 'database' | 'nas' | 'other';
export type BackupStatusValue = 'active' | 'inactive' | 'failed' | 'warning';
export type VoIPTypeValue = 'teams' | '3cx' | 'yeastar' | 'other';
