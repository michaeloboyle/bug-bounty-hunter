import React, { useState, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Container, Grid, Paper, Box,
  Card, CardContent, CardHeader, Button, Chip, LinearProgress,
  List, ListItem, ListItemText, ListItemSecondaryAction,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Table, TableHead, TableBody, TableRow, TableCell,
  IconButton, Tooltip, Tabs, Tab
} from '@mui/material';
import {
  Dashboard, Security, BugReport, PlayArrow, Stop, 
  Visibility, CheckCircle, Warning, Error,
  TrendingUp, AttachMoney, Speed, History
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import io from 'socket.io-client';
import ActivityHistory from './components/ActivityHistory';

interface Program {
  id: string;
  name: string;
  platform: string;
  payoutMax: number;
  rps: number;
  autoOK: boolean;
  triageDays: number;
  assetCount: number;
  tags: string[];
}

interface Finding {
  id: string;
  programId: string;
  type: string;
  severity: number;
  status: string;
  payoutEst: number;
  timestamp?: string;
  evidence?: string[];
}

interface ScanStatus {
  programId: string;
  status: 'queued' | 'scanning' | 'analyzing' | 'exploiting' | 'reporting' | 'completed';
  progress: number;
  assetsFound: number;
  vulnerabilitiesFound: number;
  startTime: string;
}

const SEVERITY_COLORS = {
  critical: '#f44336',
  high: '#ff9800',
  medium: '#ff5722',
  low: '#4caf50',
  info: '#2196f3'
};

export default function App() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [scanStatuses, setScanStatuses] = useState<ScanStatus[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [socket, setSocket] = useState<any>(null);
  const [currentTab, setCurrentTab] = useState(0);

  useEffect(() => {
    // Fetch initial data
    fetch('/api/programs').then(r => r.json()).then(setPrograms);
    fetch('/api/findings').then(r => r.json()).then(setFindings);
    
    // Setup WebSocket for real-time updates
    const newSocket = io();
    setSocket(newSocket);
    
    newSocket.on('scan_update', (status: ScanStatus) => {
      setScanStatuses(prev => {
        const index = prev.findIndex(s => s.programId === status.programId);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = status;
          return updated;
        }
        return [...prev, status];
      });
    });
    
    newSocket.on('new_finding', (finding: Finding) => {
      setFindings(prev => [...prev, finding]);
    });
    
    return () => newSocket.close();
  }, []);

  const startScan = async (programId: string, priority: string = 'fast_pay') => {
    await fetch('/api/queue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ program_id: programId, priority })
    });
  };

  const approveFinding = async (findingId: string) => {
    await fetch(`/api/findings/${findingId}/approve`, { method: 'POST' });
    setFindings(prev => prev.map(f => 
      f.id === findingId ? { ...f, status: 'approved' } : f
    ));
  };

  const getSeverityColor = (severity: number): string => {
    if (severity >= 9.0) return SEVERITY_COLORS.critical;
    if (severity >= 7.0) return SEVERITY_COLORS.high;
    if (severity >= 4.0) return SEVERITY_COLORS.medium;
    if (severity >= 0.1) return SEVERITY_COLORS.low;
    return SEVERITY_COLORS.info;
  };

  const getSeverityLabel = (severity: number): string => {
    if (severity >= 9.0) return 'Critical';
    if (severity >= 7.0) return 'High';
    if (severity >= 4.0) return 'Medium';
    if (severity >= 0.1) return 'Low';
    return 'Info';
  };

  // Analytics data
  const revenueData = [
    { month: 'Jan', revenue: 15000, submissions: 45 },
    { month: 'Feb', revenue: 22000, submissions: 67 },
    { month: 'Mar', revenue: 31000, submissions: 89 },
    { month: 'Apr', revenue: 28000, submissions: 76 },
    { month: 'May', revenue: 35000, submissions: 95 }
  ];

  const vulnerabilityTypes = [
    { name: 'SSRF', value: 12, payout: 45000 },
    { name: 'IDOR', value: 8, payout: 23000 },
    { name: 'XSS', value: 15, payout: 15000 },
    { name: 'AuthZ', value: 6, payout: 32000 },
    { name: 'Other', value: 9, payout: 8000 }
  ];

  const totalRevenue = findings.reduce((sum, f) => sum + f.payoutEst, 0);
  const avgSeverity = findings.reduce((sum, f) => sum + f.severity, 0) / findings.length || 0;
  const activeScans = scanStatuses.filter(s => s.status !== 'completed').length;

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Security sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Bug Bounty Operations Center
          </Typography>
          <Chip 
            label={`${activeScans} Active Scans`} 
            color={activeScans > 0 ? 'warning' : 'default'}
            variant="outlined"
          />
        </Toolbar>
      </AppBar>

      {/* Navigation Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)} centered>
          <Tab icon={<Dashboard />} label="Dashboard" />
          <Tab icon={<History />} label="Activity History" />
        </Tabs>
      </Box>

      {/* Dashboard Tab */}
      {currentTab === 0 && (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          {/* Key Metrics */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <AttachMoney color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Total Revenue
                    </Typography>
                    <Typography variant="h4">
                      ${totalRevenue.toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <BugReport color="error" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Findings
                    </Typography>
                    <Typography variant="h4">
                      {findings.length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Speed color="warning" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Avg Severity
                    </Typography>
                    <Typography variant="h4">
                      {avgSeverity.toFixed(1)}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUp color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Success Rate
                    </Typography>
                    <Typography variant="h4">
                      {((findings.filter(f => f.status === 'approved').length / findings.length) * 100 || 0).toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Active Scans */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Active Scans" />
              <CardContent>
                {scanStatuses.length === 0 ? (
                  <Typography color="textSecondary">No active scans</Typography>
                ) : (
                  <List>
                    {scanStatuses.map(scan => (
                      <ListItem key={scan.programId}>
                        <ListItemText
                          primary={programs.find(p => p.id === scan.programId)?.name || scan.programId}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                Status: {scan.status} • Assets: {scan.assetsFound} • Vulns: {scan.vulnerabilitiesFound}
                              </Typography>
                              <LinearProgress variant="determinate" value={scan.progress} sx={{ mt: 1 }} />
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Programs */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Bug Bounty Programs" />
              <CardContent>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Program</TableCell>
                      <TableCell>Max Payout</TableCell>
                      <TableCell>Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {programs.map(program => (
                      <TableRow key={program.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {program.name}
                            </Typography>
                            <Box>
                              {program.tags.map(tag => (
                                <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5, mt: 0.5 }} />
                              ))}
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>${program.payoutMax.toLocaleString()}</TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            startIcon={<PlayArrow />}
                            onClick={() => startScan(program.id)}
                            disabled={scanStatuses.some(s => s.programId === program.id && s.status !== 'completed')}
                          >
                            Scan
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </Grid>

          {/* Findings Requiring Human Review */}
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Findings Requiring Review" />
              <CardContent>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Program</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Severity</TableCell>
                      <TableCell>Est. Payout</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {findings.filter(f => f.status === 'needs_human').map(finding => (
                      <TableRow key={finding.id}>
                        <TableCell>
                          {programs.find(p => p.id === finding.programId)?.name || finding.programId}
                        </TableCell>
                        <TableCell>{finding.type}</TableCell>
                        <TableCell>
                          <Chip
                            label={getSeverityLabel(finding.severity)}
                            sx={{ 
                              backgroundColor: getSeverityColor(finding.severity),
                              color: 'white'
                            }}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>${finding.payoutEst.toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip
                            label={finding.status}
                            color={finding.status === 'needs_human' ? 'warning' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Details">
                            <IconButton onClick={() => setSelectedFinding(finding)}>
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Approve">
                            <IconButton onClick={() => approveFinding(finding.id)} color="success">
                              <CheckCircle />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </Grid>

          {/* Analytics Charts */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Revenue Trend" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Vulnerability Types" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={vulnerabilityTypes}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {vulnerabilityTypes.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={Object.values(SEVERITY_COLORS)[index % Object.values(SEVERITY_COLORS).length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        </Container>
      )}

      {/* Activity History Tab */}
      {currentTab === 1 && (
        <ActivityHistory />
      )}

      {/* Finding Details Modal */}
      <Dialog
        open={selectedFinding !== null}
        onClose={() => setSelectedFinding(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Finding Details: {selectedFinding?.type}
        </DialogTitle>
        <DialogContent>
          {selectedFinding && (
            <Box>
              <Typography variant="body1" gutterBottom>
                <strong>Program:</strong> {programs.find(p => p.id === selectedFinding.programId)?.name}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Severity:</strong> {selectedFinding.severity} ({getSeverityLabel(selectedFinding.severity)})
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Estimated Payout:</strong> ${selectedFinding.payoutEst.toLocaleString()}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Status:</strong> {selectedFinding.status}
              </Typography>
              
              {selectedFinding.evidence && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Evidence:</Typography>
                  <List>
                    {selectedFinding.evidence.map((item, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={item} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedFinding(null)}>Close</Button>
          {selectedFinding?.status === 'needs_human' && (
            <Button
              onClick={() => {
                approveFinding(selectedFinding.id);
                setSelectedFinding(null);
              }}
              variant="contained"
              color="primary"
            >
              Approve & Submit
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}