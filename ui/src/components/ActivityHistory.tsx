import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Chip, IconButton, Collapse,
  List, ListItem, ListItemText, ListItemIcon, Button, Dialog,
  DialogTitle, DialogContent, DialogActions, Tab, Tabs, Paper,
  Table, TableHead, TableBody, TableRow, TableCell, TextField,
  InputAdornment, MenuItem, Select, FormControl, InputLabel,
  Avatar, Tooltip, LinearProgress, Accordion, AccordionSummary,
  AccordionDetails, Divider, Grid, Badge
} from '@mui/material';
import {
  ExpandMore, PlayArrow, CheckCircle, Error, Cancel, Warning,
  Schedule, BugReport, Security, Visibility, GetApp, Search,
  FilterList, AccessTime, Person, Computer, CloudDownload
} from '@mui/icons-material';

interface Activity {
  id: string;
  type: string;
  title: string;
  programId?: string;
  triggeredBy: string;
  status: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  conclusion?: string;
  artifacts: string[];
  runCount: number;
}

interface ActivityRun {
  id: string;
  activityId: string;
  jobName: string;
  stepName?: string;
  status: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  conclusion?: string;
}

interface ActivityLog {
  timestamp: string;
  level: string;
  message: string;
  runId?: string;
}

interface Artifact {
  id: string;
  name: string;
  type: string;
  content: string;
  size: number;
  createdAt: string;
  runId?: string;
}

const ActivityHistory: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [activityDetails, setActivityDetails] = useState<{
    runs: ActivityRun[];
    logs: ActivityLog[];
    artifacts: Artifact[];
  } | null>(null);
  const [expandedActivities, setExpandedActivities] = useState<Set<string>>(new Set());
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState(0);

  useEffect(() => {
    fetchActivities();
  }, [filterType, filterStatus]);

  const fetchActivities = async () => {
    try {
      const params = new URLSearchParams();
      if (filterType) params.append('activity_type', filterType);
      if (filterStatus) params.append('status', filterStatus);
      
      const response = await fetch(`/api/activities?${params}`);
      const data = await response.json();
      setActivities(data.activities);
    } catch (error) {
      console.error('Failed to fetch activities:', error);
    }
  };

  const fetchActivityDetails = async (activityId: string) => {
    try {
      const response = await fetch(`/api/activities/${activityId}`);
      const data = await response.json();
      setActivityDetails({
        runs: data.runs,
        logs: data.logs,
        artifacts: data.artifacts
      });
    } catch (error) {
      console.error('Failed to fetch activity details:', error);
    }
  };

  const handleActivityClick = async (activity: Activity) => {
    setSelectedActivity(activity);
    await fetchActivityDetails(activity.id);
  };

  const handleToggleExpand = (activityId: string) => {
    const newExpanded = new Set(expandedActivities);
    if (newExpanded.has(activityId)) {
      newExpanded.delete(activityId);
    } else {
      newExpanded.add(activityId);
    }
    setExpandedActivities(newExpanded);
  };

  const getStatusIcon = (status: string, conclusion?: string) => {
    if (status === 'completed') {
      if (conclusion === 'success') return <CheckCircle color="success" />;
      if (conclusion === 'failure') return <Error color="error" />;
    }
    if (status === 'cancelled') return <Cancel color="action" />;
    if (status === 'in_progress') return <Schedule color="primary" />;
    if (status === 'failed') return <Error color="error" />;
    return <Schedule color="action" />;
  };

  const getStatusColor = (status: string, conclusion?: string): "default" | "primary" | "success" | "error" | "warning" => {
    if (status === 'completed' && conclusion === 'success') return 'success';
    if (status === 'failed' || conclusion === 'failure') return 'error';
    if (status === 'cancelled') return 'default';
    if (status === 'in_progress') return 'primary';
    return 'default';
  };

  const getActivityTypeIcon = (type: string) => {
    switch (type) {
      case 'scan': return <BugReport />;
      case 'submission': return <CloudDownload />;
      case 'analysis': return <Security />;
      default: return <Computer />;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const filteredActivities = activities.filter(activity =>
    activity.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    activity.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Activity History
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            size="small"
            placeholder="Search activities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              )
            }}
            sx={{ width: 250 }}
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              label="Type"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="scan">Scans</MenuItem>
              <MenuItem value="submission">Submissions</MenuItem>
              <MenuItem value="analysis">Analysis</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Activity List */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Activities</Typography>
            {filteredActivities.map((activity) => (
              <Card key={activity.id} sx={{ mb: 2, cursor: 'pointer' }} onClick={() => handleActivityClick(activity)}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                      {getActivityTypeIcon(activity.type)}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" component="div">
                        {activity.title}
                      </Typography>
                      <Typography color="text.secondary" variant="body2">
                        Started {formatDate(activity.startTime)}
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Chip
                        icon={getStatusIcon(activity.status, activity.conclusion)}
                        label={activity.status.replace('_', ' ')}
                        color={getStatusColor(activity.status, activity.conclusion)}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption" display="block">
                        {formatDuration(activity.duration)}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      <Person fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                      {activity.triggeredBy}
                    </Typography>
                    <Badge badgeContent={activity.runCount} color="primary">
                      <Typography variant="body2" color="text.secondary">
                        Jobs
                      </Typography>
                    </Badge>
                    <Badge badgeContent={activity.artifacts.length} color="secondary">
                      <Typography variant="body2" color="text.secondary">
                        Artifacts
                      </Typography>
                    </Badge>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>

        {/* Activity Details */}
        <Grid item xs={12} md={6}>
          {selectedActivity && activityDetails && (
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  {selectedActivity.title}
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setSelectedActivity(null)}
                >
                  Close
                </Button>
              </Box>

              <Tabs value={selectedTab} onChange={(_, v) => setSelectedTab(v)} sx={{ mb: 2 }}>
                <Tab label="Jobs" />
                <Tab label="Logs" />
                <Tab label="Artifacts" />
              </Tabs>

              {/* Jobs Tab */}
              {selectedTab === 0 && (
                <Box>
                  {activityDetails.runs.map((run) => (
                    <Accordion key={run.id}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                          {getStatusIcon(run.status, run.conclusion)}
                          <Typography sx={{ ml: 1, flexGrow: 1 }}>
                            {run.jobName} {run.stepName && `- ${run.stepName}`}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatDuration(run.duration)}
                          </Typography>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Table size="small">
                          <TableBody>
                            <TableRow>
                              <TableCell><strong>Started</strong></TableCell>
                              <TableCell>{formatDate(run.startTime)}</TableCell>
                            </TableRow>
                            {run.endTime && (
                              <TableRow>
                                <TableCell><strong>Completed</strong></TableCell>
                                <TableCell>{formatDate(run.endTime)}</TableCell>
                              </TableRow>
                            )}
                            <TableRow>
                              <TableCell><strong>Status</strong></TableCell>
                              <TableCell>
                                <Chip
                                  label={run.status}
                                  color={getStatusColor(run.status, run.conclusion)}
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                        
                        {/* Run-specific logs */}
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>Logs</Typography>
                          <Box sx={{ maxHeight: 200, overflow: 'auto', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                            {activityDetails.logs
                              .filter(log => log.runId === run.id)
                              .map((log, index) => (
                                <Typography
                                  key={index}
                                  variant="caption"
                                  component="div"
                                  sx={{
                                    fontFamily: 'monospace',
                                    color: log.level === 'error' ? 'error.main' : 
                                           log.level === 'warning' ? 'warning.main' :
                                           log.level === 'success' ? 'success.main' : 'text.primary'
                                  }}
                                >
                                  [{new Date(log.timestamp).toLocaleTimeString()}] {log.message}
                                </Typography>
                              ))}
                          </Box>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}

              {/* Logs Tab */}
              {selectedTab === 1 && (
                <Box sx={{ maxHeight: 600, overflow: 'auto', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                  {activityDetails.logs.map((log, index) => (
                    <Typography
                      key={index}
                      variant="body2"
                      component="div"
                      sx={{
                        fontFamily: 'monospace',
                        mb: 0.5,
                        color: log.level === 'error' ? 'error.main' : 
                               log.level === 'warning' ? 'warning.main' :
                               log.level === 'success' ? 'success.main' : 'text.primary'
                      }}
                    >
                      <strong>[{new Date(log.timestamp).toLocaleTimeString()}]</strong> {log.message}
                    </Typography>
                  ))}
                </Box>
              )}

              {/* Artifacts Tab */}
              {selectedTab === 2 && (
                <Box>
                  {activityDetails.artifacts.map((artifact) => (
                    <Card key={artifact.id} sx={{ mb: 2 }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <GetApp sx={{ mr: 1 }} />
                          <Typography variant="h6" sx={{ flexGrow: 1 }}>
                            {artifact.name}
                          </Typography>
                          <Chip
                            label={artifact.type}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {artifact.size} bytes • Created {formatDate(artifact.createdAt)}
                        </Typography>
                        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1, maxHeight: 200, overflow: 'auto' }}>
                          <Typography
                            variant="body2"
                            component="pre"
                            sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', margin: 0 }}
                          >
                            {artifact.content}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              )}
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ActivityHistory;