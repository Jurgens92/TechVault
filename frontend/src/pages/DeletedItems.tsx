import { useState, useEffect } from 'react';
import {
  Container, Paper, Typography, Box, Tabs, Tab,
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Button, Alert, CircularProgress, Chip
} from '@mui/material';
import { RestoreFromTrash, DeleteForever } from '@mui/icons-material';
import {
  organizationAPI, locationAPI, contactAPI, documentationAPI,
  passwordAPI, configurationAPI, networkDeviceAPI, endpointUserAPI,
  serverAPI, peripheralAPI
} from '../services/core';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DeletedItems = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // State for each entity type
  const [deletedOrganizations, setDeletedOrganizations] = useState<any[]>([]);
  const [deletedLocations, setDeletedLocations] = useState<any[]>([]);
  const [deletedContacts, setDeletedContacts] = useState<any[]>([]);
  const [deletedDocumentations, setDeletedDocumentations] = useState<any[]>([]);
  const [deletedPasswords, setDeletedPasswords] = useState<any[]>([]);
  const [deletedConfigurations, setDeletedConfigurations] = useState<any[]>([]);
  const [deletedNetworkDevices, setDeletedNetworkDevices] = useState<any[]>([]);
  const [deletedEndpoints, setDeletedEndpoints] = useState<any[]>([]);
  const [deletedServers, setDeletedServers] = useState<any[]>([]);
  const [deletedPeripherals, setDeletedPeripherals] = useState<any[]>([]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const loadDeletedItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const [orgs, locs, conts, docs, pass, confs, netdevs, endpts, servs, periphs] = await Promise.all([
        organizationAPI.getDeleted(),
        locationAPI.getDeleted(),
        contactAPI.getDeleted(),
        documentationAPI.getDeleted(),
        passwordAPI.getDeleted(),
        configurationAPI.getDeleted(),
        networkDeviceAPI.getDeleted(),
        endpointUserAPI.getDeleted(),
        serverAPI.getDeleted(),
        peripheralAPI.getDeleted(),
      ]);

      setDeletedOrganizations(orgs.data.results || []);
      setDeletedLocations(locs.data.results || []);
      setDeletedContacts(conts.data.results || []);
      setDeletedDocumentations(docs.data.results || []);
      setDeletedPasswords(pass.data.results || []);
      setDeletedConfigurations(confs.data.results || []);
      setDeletedNetworkDevices(netdevs.data.results || []);
      setDeletedEndpoints(endpts.data.results || []);
      setDeletedServers(servs.data.results || []);
      setDeletedPeripherals(periphs.data.results || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load deleted items');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeletedItems();
  }, []);

  const handleRestore = async (id: string, api: any, entityType: string) => {
    try {
      await api.restore(id);
      setSuccess(`${entityType} restored successfully!`);
      setTimeout(() => setSuccess(null), 3000);
      loadDeletedItems();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to restore ${entityType}`);
    }
  };

  const handleHardDelete = async (id: string, api: any, entityType: string) => {
    if (!window.confirm(`Are you sure you want to permanently delete this ${entityType}? This action cannot be undone!`)) {
      return;
    }
    try {
      await api.hardDelete(id);
      setSuccess(`${entityType} permanently deleted!`);
      setTimeout(() => setSuccess(null), 3000);
      loadDeletedItems();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to permanently delete ${entityType}`);
    }
  };

  const renderTable = (items: any[], api: any, entityType: string, nameField: string = 'name') => {
    if (items.length === 0) {
      return <Typography variant="body2" color="text.secondary">No deleted items</Typography>;
    }

    return (
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Deleted At</TableCell>
              <TableCell>Deleted By</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item[nameField] || item.title || 'N/A'}</TableCell>
                <TableCell>
                  {item.deleted_at ? new Date(item.deleted_at).toLocaleString() : 'N/A'}
                </TableCell>
                <TableCell>
                  {item.deleted_by ? `${item.deleted_by.first_name} ${item.deleted_by.last_name}` : 'N/A'}
                </TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<RestoreFromTrash />}
                    onClick={() => handleRestore(item.id, api, entityType)}
                    sx={{ mr: 1 }}
                  >
                    Restore
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<DeleteForever />}
                    onClick={() => handleHardDelete(item.id, api, entityType)}
                  >
                    Permanent Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Deleted Items
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          View and restore deleted items. Items can be permanently deleted by administrators.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mt: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        <Paper sx={{ mt: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
            <Tab label={`Organizations (${deletedOrganizations.length})`} />
            <Tab label={`Locations (${deletedLocations.length})`} />
            <Tab label={`Contacts (${deletedContacts.length})`} />
            <Tab label={`Documentation (${deletedDocumentations.length})`} />
            <Tab label={`Passwords (${deletedPasswords.length})`} />
            <Tab label={`Configurations (${deletedConfigurations.length})`} />
            <Tab label={`Network Devices (${deletedNetworkDevices.length})`} />
            <Tab label={`Endpoints (${deletedEndpoints.length})`} />
            <Tab label={`Servers (${deletedServers.length})`} />
            <Tab label={`Peripherals (${deletedPeripherals.length})`} />
          </Tabs>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <TabPanel value={tabValue} index={0}>
                {renderTable(deletedOrganizations, organizationAPI, 'Organization')}
              </TabPanel>
              <TabPanel value={tabValue} index={1}>
                {renderTable(deletedLocations, locationAPI, 'Location')}
              </TabPanel>
              <TabPanel value={tabValue} index={2}>
                {renderTable(deletedContacts, contactAPI, 'Contact', 'full_name')}
              </TabPanel>
              <TabPanel value={tabValue} index={3}>
                {renderTable(deletedDocumentations, documentationAPI, 'Documentation')}
              </TabPanel>
              <TabPanel value={tabValue} index={4}>
                {renderTable(deletedPasswords, passwordAPI, 'Password')}
              </TabPanel>
              <TabPanel value={tabValue} index={5}>
                {renderTable(deletedConfigurations, configurationAPI, 'Configuration')}
              </TabPanel>
              <TabPanel value={tabValue} index={6}>
                {renderTable(deletedNetworkDevices, networkDeviceAPI, 'Network Device')}
              </TabPanel>
              <TabPanel value={tabValue} index={7}>
                {renderTable(deletedEndpoints, endpointUserAPI, 'Endpoint')}
              </TabPanel>
              <TabPanel value={tabValue} index={8}>
                {renderTable(deletedServers, serverAPI, 'Server')}
              </TabPanel>
              <TabPanel value={tabValue} index={9}>
                {renderTable(deletedPeripherals, peripheralAPI, 'Peripheral')}
              </TabPanel>
            </>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default DeletedItems;
