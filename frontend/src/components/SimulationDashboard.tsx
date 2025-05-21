import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Title,
  Paper,
  Group,
  NumberInput,
  Button,
  Slider,
  Text,
  Stack,
  Grid,
  useMantineColorScheme,
  Tabs,
  Card,
  Badge,
  RingProgress,
  Center,
  Divider,
  ActionIcon,
  Tooltip,
  Transition,
  Loader,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import Plot from 'react-plotly.js';
import axios from 'axios';
import { Layout } from 'plotly.js';
import { 
  IconVaccine, 
  IconMask, 
  IconUsers, 
  IconChartBar, 
  IconPlayerPlay,
  IconVirus,
  IconUsersGroup,
  IconShieldCheck,
  IconPlayerPause,
} from '@tabler/icons-react';
import { Data } from 'plotly.js';

interface SimulationParams {
  num_nodes: number;
  edges_per_node: number;
  initial_infected_percentage: number;
  simulation_days: number;
  vaccination_rate: number;
  mask_usage: number;
  transmission_rate: number;
  recovery_rate: number;
  mortality_rate: number;
  hospitalization_rate: number;
}

interface SimulationResults {
  timeline: {
    susceptible: number[];
    infected: number[];
    hospitalized: number[];
    recovered: number[];
    deceased: number[];
  };
  network_states: Array<Record<string, number>>;
  network_structure: {
    nodes: Array<{ id: string; x: number; y: number }>;
    edges: Array<{ source: string; target: string }>;
  };
  age_distribution: {
    data: Array<{
      type: 'histogram';
      x: number[];
      name: string;
      marker: { color: string };
      opacity: number;
      nbinsx: number;
    }>;
    layout: Partial<Layout>;
  };
  risk_distribution: {
    data: Array<{
      type: 'histogram';
      x: number[];
      name: string;
      marker: { color: string };
      opacity: number;
      nbinsx: number;
    }>;
    layout: Partial<Layout>;
  };
  infection_rates: {
    data: Array<{
      type: 'scatter';
      x: number[];
      y: number[];
      name: string;
      line: { color: string; width: number };
      fill: 'tozeroy';
      fillcolor: string;
    }>;
    layout: Partial<Layout>;
  };
  final_stats: {
    total_infected: number;
    total_recovered: number;
    total_deceased: number;
    peak_infected: number;
    peak_hospitalized: number;
    average_risk_factor: number;
    average_age: number;
  };
}

export function SimulationDashboard() {
  const { colorScheme } = useMantineColorScheme();
  const isDark = colorScheme === 'dark';

  const [params, setParams] = useState<SimulationParams>({
    num_nodes: 1000,
    edges_per_node: 5,
    initial_infected_percentage: 1,
    simulation_days: 100,
    vaccination_rate: 0,
    mask_usage: 0,
    transmission_rate: 0.3,
    recovery_rate: 0.1,
    mortality_rate: 0.02,
    hospitalization_rate: 0.15,
  });

  const [results, setResults] = useState<SimulationResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingDynamic, setLoadingDynamic] = useState(false);
  const [activeTab, setActiveTab] = useState<string | null>('timeline');
  const [visibleCards, setVisibleCards] = useState({
    population: false,
    intervention: false,
    disease: false,
  });
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const animationRef = useRef<number | undefined>(undefined);
  const [playbackSpeed, setPlaybackSpeed] = useState(500); // ms per frame

  const toggleCard = (card: keyof typeof visibleCards) => {
    setVisibleCards(prev => ({
      ...prev,
      [card]: !prev[card]
    }));
  };

  const runSimulation = async () => {
    try {
      setLoading(true);
      setLoadingDynamic(true);
      
      // Convert parameters to match backend expectations
      const simulationParams = {
        num_nodes: params.num_nodes,
        edges_per_node: params.edges_per_node,
        initial_infected_percentage: params.initial_infected_percentage / 100,
        simulation_days: params.simulation_days,
        vaccination_rate: params.vaccination_rate / 100,
        mask_usage: params.mask_usage / 100,
        transmission_rate: params.transmission_rate,
        recovery_rate: params.recovery_rate,
        mortality_rate: params.mortality_rate,
        hospitalization_rate: params.hospitalization_rate
      };

      // Send parameters as URL parameters instead of JSON body
      const queryParams = new URLSearchParams();
      Object.entries(simulationParams).forEach(([key, value]) => {
        queryParams.append(key, value.toString());
      });

      const response = await axios.post(`http://localhost:8000/simulate?${queryParams.toString()}`);
      setResults(response.data as SimulationResults);
      setLoadingDynamic(false);
      notifications.show({
        title: 'Success',
        message: 'Simulation completed successfully',
        color: 'green',
      });
    } catch (error: any) {
      console.error('Simulation error:', error.response?.data || error.message);
      const errorMessage = error.response?.data?.detail || 'Failed to run simulation';
      notifications.show({
        title: 'Error',
        message: errorMessage,
        color: 'red',
      });
      setLoadingDynamic(false);
    } finally {
      setLoading(false);
    }
  };

  // Animation control
  useEffect(() => {
    if (isPlaying && results) {
      const animate = () => {
        setCurrentFrame((prev) => {
          const next = (prev + 1) % results.network_states.length;
          return next;
        });
        animationRef.current = requestAnimationFrame(animate);
      };
      animationRef.current = requestAnimationFrame(animate);
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, results]);

  return (
    <Container size="xl">
      <Stack gap="xl">
        {/* Floating Navigation Bar */}
        <Paper 
          withBorder 
          p="md" 
          radius="xl" 
          className="floating-nav glass-morphism"
          style={{ width: '600px', maxWidth: '90vw', margin: '0 auto', backdropFilter: 'blur(24px)', background: 'rgba(255,255,255,0.25)' }}
        >
          <Group gap="xl" justify="center">
            <Tooltip label="Population Parameters">
              <ActionIcon
                variant="light"
                size="xl"
                radius="xl"
                color={visibleCards.population ? "blue" : "gray"}
                onClick={() => toggleCard('population')}
                className={`nav-icon ${visibleCards.population ? 'nav-icon-active' : ''}`}
              >
                <IconUsersGroup size={24} />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Intervention Parameters">
              <ActionIcon
                variant="light"
                size="xl"
                radius="xl"
                color={visibleCards.intervention ? "blue" : "gray"}
                onClick={() => toggleCard('intervention')}
                className={`nav-icon ${visibleCards.intervention ? 'nav-icon-active' : ''}`}
              >
                <IconShieldCheck size={24} />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Disease Parameters">
              <ActionIcon
                variant="light"
                size="xl"
                radius="xl"
                color={visibleCards.disease ? "blue" : "gray"}
                onClick={() => toggleCard('disease')}
                className={`nav-icon ${visibleCards.disease ? 'nav-icon-active' : ''}`}
              >
                <IconVirus size={24} />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Paper>

        {/* Parameter Cards */}
        <Grid style={{ marginTop: '80px' }}>
          <Transition mounted={visibleCards.population} transition="slide-down" duration={400}>
            {(styles) => (
              <Grid.Col span={4} style={styles}>
                <Card withBorder p="md" radius="md" className="parameter-card">
                  <Stack>
                    <Title order={4} className="gradient-text">Population Parameters</Title>
                    <Divider />
                    <NumberInput
                      label={
                        <Group gap="xs">
                          <IconUsers size={16} />
                          Population Size
                        </Group>
                      }
                      value={params.num_nodes}
                      onChange={(val) => setParams({ ...params, num_nodes: Number(val) || 1000 })}
                      min={100}
                      max={10000}
                    />
                    <NumberInput
                      label="Connections per Person"
                      value={params.edges_per_node}
                      onChange={(val) => setParams({ ...params, edges_per_node: Number(val) || 5 })}
                      min={1}
                      max={20}
                    />
                    <Text size="sm">Initial Infected Percentage</Text>
                    <Slider
                      value={params.initial_infected_percentage}
                      onChange={(val) => setParams({ ...params, initial_infected_percentage: val })}
                      min={0}
                      max={100}
                      label={(val) => `${val}%`}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' },
                      ]}
                    />
                  </Stack>
                </Card>
              </Grid.Col>
            )}
          </Transition>

          <Transition mounted={visibleCards.intervention} transition="slide-down" duration={400}>
            {(styles) => (
              <Grid.Col span={4} style={styles}>
                <Card withBorder p="md" radius="md" className="parameter-card">
                  <Stack>
                    <Title order={4} className="gradient-text">Intervention Parameters</Title>
                    <Divider />
                    <Text size="sm">
                      <Group gap="xs">
                        <IconVaccine size={16} />
                        Vaccination Rate
                      </Group>
                    </Text>
                    <Slider
                      value={params.vaccination_rate}
                      onChange={(val) => setParams({ ...params, vaccination_rate: val })}
                      min={0}
                      max={100}
                      label={(val) => `${val}%`}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' },
                      ]}
                    />
                    <Text size="sm">
                      <Group gap="xs">
                        <IconMask size={16} />
                        Mask Usage
                      </Group>
                    </Text>
                    <Slider
                      value={params.mask_usage}
                      onChange={(val) => setParams({ ...params, mask_usage: val })}
                      min={0}
                      max={100}
                      label={(val) => `${val}%`}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' },
                      ]}
                    />
                  </Stack>
                </Card>
              </Grid.Col>
            )}
          </Transition>

          <Transition mounted={visibleCards.disease} transition="slide-down" duration={400}>
            {(styles) => (
              <Grid.Col span={4} style={styles}>
                <Card withBorder p="md" radius="md" className="parameter-card">
                  <Stack>
                    <Title order={4} className="gradient-text">Disease Parameters</Title>
                    <Divider />
                    <Text size="sm">Transmission Rate</Text>
                    <Slider
                      value={params.transmission_rate}
                      onChange={(val) => setParams({ ...params, transmission_rate: val })}
                      min={0}
                      max={1}
                      step={0.01}
                      label={(val) => `${(val * 100).toFixed(0)}%`}
                    />
                    <Text size="sm">Recovery Rate</Text>
                    <Slider
                      value={params.recovery_rate}
                      onChange={(val) => setParams({ ...params, recovery_rate: val })}
                      min={0}
                      max={1}
                      step={0.01}
                      label={(val) => `${(val * 100).toFixed(0)}%`}
                    />
                    <Text size="sm">Mortality Rate</Text>
                    <Slider
                      value={params.mortality_rate}
                      onChange={(val) => setParams({ ...params, mortality_rate: val })}
                      min={0}
                      max={1}
                      step={0.01}
                      label={(val) => `${(val * 100).toFixed(0)}%`}
                    />
                    <Text size="sm">Hospitalization Rate</Text>
                    <Slider
                      value={params.hospitalization_rate}
                      onChange={(val) => setParams({ ...params, hospitalization_rate: val })}
                      min={0}
                      max={1}
                      step={0.01}
                      label={(val) => `${(val * 100).toFixed(0)}%`}
                    />
                  </Stack>
                </Card>
              </Grid.Col>
            )}
          </Transition>
        </Grid>

        {/* Simulation Days and Run Button */}
        <Group justify="center" gap="xl">
          <NumberInput
            label={
              <Group gap="xs">
                <IconChartBar size={16} />
                Simulation Days
              </Group>
            }
            value={params.simulation_days}
            onChange={(val) => setParams({ ...params, simulation_days: Number(val) || 100 })}
            min={10}
            max={365}
            style={{ width: '200px' }}
          />
          <Button
            onClick={runSimulation}
            loading={loading}
            className="simulation-button"
            size="xl"
          >
            <IconPlayerPlay size={24} />
          </Button>
        </Group>

        {/* Results Section */}
        {results && (
          <Paper withBorder p="md" radius="md" className="glass-morphism">
            <Stack>
              <Title order={3} className="gradient-text">Simulation Results</Title>
              
              <Tabs value={activeTab} onChange={setActiveTab}>
                <Tabs.List>
                  <Tabs.Tab value="timeline">Timeline</Tabs.Tab>
                  <Tabs.Tab value="network">Network</Tabs.Tab>
                  <Tabs.Tab value="stats">Statistics</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="timeline" className="tab-content">
                  {results && (
                    <Stack>
                      <Plot
                        data={[
                          {
                            x: Array.from({ length: results.timeline.susceptible.length }, (_, i) => i),
                            y: results.timeline.susceptible,
                            name: 'Susceptible',
                            type: 'scatter',
                            mode: 'lines',
                            line: { color: '#2ecc71' },
                          },
                          {
                            x: Array.from({ length: results.timeline.infected.length }, (_, i) => i),
                            y: results.timeline.infected,
                            name: 'Infected',
                            type: 'scatter',
                            mode: 'lines',
                            line: { color: '#e74c3c' },
                          },
                          {
                            x: Array.from({ length: results.timeline.hospitalized.length }, (_, i) => i),
                            y: results.timeline.hospitalized,
                            name: 'Hospitalized',
                            type: 'scatter',
                            mode: 'lines',
                            line: { color: '#f1c40f' },
                          },
                          {
                            x: Array.from({ length: results.timeline.recovered.length }, (_, i) => i),
                            y: results.timeline.recovered,
                            name: 'Recovered',
                            type: 'scatter',
                            mode: 'lines',
                            line: { color: '#3498db' },
                          },
                          {
                            x: Array.from({ length: results.timeline.deceased.length }, (_, i) => i),
                            y: results.timeline.deceased,
                            name: 'Deceased',
                            type: 'scatter',
                            mode: 'lines',
                            line: { color: '#95a5a6' },
                          },
                        ]}
                        layout={{
                          title: { text: 'Disease Spread Timeline' },
                          xaxis: { title: { text: 'Days' } },
                          yaxis: { title: { text: 'Population' } },
                          paper_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                          plot_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                          font: { color: isDark ? '#ffffff' : '#000000' },
                          showlegend: true,
                          legend: { x: 0, y: 1, bgcolor: 'rgba(0,0,0,0)' },
                        }}
                        style={{ width: '100%', height: '400px' }}
                        config={{ responsive: true }}
                      />
                      <Grid>
                        <Grid.Col span={6}>
                          <Plot
                            data={results.age_distribution.data}
                            layout={{
                              ...results.age_distribution.layout,
                              paper_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                              plot_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                              font: { color: isDark ? '#ffffff' : '#000000' },
                            }}
                            style={{ width: '100%', height: '300px' }}
                            config={{ responsive: true }}
                          />
                        </Grid.Col>
                        <Grid.Col span={6}>
                          <Plot
                            data={results.risk_distribution.data}
                            layout={{
                              ...results.risk_distribution.layout,
                              paper_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                              plot_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                              font: { color: isDark ? '#ffffff' : '#000000' },
                            }}
                            style={{ width: '100%', height: '300px' }}
                            config={{ responsive: true }}
                          />
                        </Grid.Col>
                      </Grid>
                      <Plot
                        data={results.infection_rates.data}
                        layout={{
                          ...results.infection_rates.layout,
                          paper_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                          plot_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                          font: { color: isDark ? '#ffffff' : '#000000' },
                        }}
                        style={{ width: '100%', height: '300px' }}
                        config={{ responsive: true }}
                      />
                    </Stack>
                  )}
                </Tabs.Panel>

                <Tabs.Panel value="network" className="tab-content">
                  {loadingDynamic ? (
                    <Center style={{ height: '500px' }}>
                      <Stack align="center" gap="md">
                        <Loader size="xl" />
                        <Text>Generating dynamic visualization...</Text>
                      </Stack>
                    </Center>
                  ) : (
                    <Stack>
                      <Group justify="space-between" align="center">
                        <Group>
                          <Button
                            variant="light"
                            onClick={() => setIsPlaying(!isPlaying)}
                            leftSection={isPlaying ? <IconPlayerPause size={16} /> : <IconPlayerPlay size={16} />}
                          >
                            {isPlaying ? 'Pause' : 'Play'}
                          </Button>
                          <Slider
                            value={currentFrame}
                            onChange={setCurrentFrame}
                            min={0}
                            max={results.network_states.length - 1}
                            style={{ width: '300px' }}
                            label={(val) => `Day ${val}`}
                          />
                        </Group>
                        <Group>
                          <Text size="sm">Playback Speed:</Text>
                          <Slider
                            value={playbackSpeed}
                            onChange={setPlaybackSpeed}
                            min={100}
                            max={1000}
                            step={100}
                            style={{ width: '200px' }}
                            label={(val) => `${val}ms`}
                          />
                        </Group>
                      </Group>

                      <Plot
                        data={[
                          // Draw edges as lines between node positions
                          (() => {
                            // Precompute a map for fast lookup
                            const nodeMap = Object.fromEntries(results.network_structure.nodes.map(n => [n.id, n]));
                            // Only include edges where both source and target exist
                            const validEdges = results.network_structure.edges.filter(edge => nodeMap[edge.source] && nodeMap[edge.target]);
                            return {
                              type: 'scatter',
                              mode: 'lines',
                              x: validEdges.map(edge => [nodeMap[edge.source].x, nodeMap[edge.target].x, null]).flat(),
                              y: validEdges.map(edge => [nodeMap[edge.source].y, nodeMap[edge.target].y, null]).flat(),
                              line: {
                                color: 'rgba(0, 0, 0, 0.1)',
                                width: 1
                              },
                              hoverinfo: 'none',
                              showlegend: false
                            };
                          })(),
                          // Draw nodes at their (x, y) positions
                          {
                            type: 'scatter',
                            mode: 'markers',
                            x: results.network_structure.nodes.map(node => node.x),
                            y: results.network_structure.nodes.map(node => node.y),
                            marker: {
                              size: 10,
                              color: results.network_structure.nodes.map(node => {
                                const status = results.network_states[currentFrame][node.id];
                                return status === 0 ? '#3498db' : // Susceptible
                                       status === 1 ? '#e74c3c' : // Infected
                                       status === 2 ? '#f1c40f' : // Hospitalized
                                       status === 3 ? '#2ecc71' : // Recovered
                                       '#7f8c8d'; // Deceased
                              }),
                              line: {
                                color: 'rgba(0, 0, 0, 0.1)',
                                width: 1
                              }
                            },
                            text: results.network_structure.nodes.map(node => {
                              const status = results.network_states[currentFrame][node.id];
                              return `Node ${node.id}: ${
                                status === 0 ? 'Susceptible' :
                                status === 1 ? 'Infected' :
                                status === 2 ? 'Hospitalized' :
                                status === 3 ? 'Recovered' :
                                'Deceased'
                              }`;
                            }),
                            hoverinfo: 'text',
                            showlegend: false
                          }
                        ]}
                        layout={{
                          title: { text: 'Disease Spread Network' },
                          xaxis: {
                            showgrid: false,
                            zeroline: false,
                            showticklabels: false
                          },
                          yaxis: {
                            showgrid: false,
                            zeroline: false,
                            showticklabels: false
                          },
                          paper_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                          plot_bgcolor: isDark ? '#1A1B1E' : '#ffffff',
                          font: { color: isDark ? '#ffffff' : '#000000' },
                          margin: { b: 20, l: 5, r: 5, t: 40 },
                          hovermode: 'closest',
                        }}
                        style={{ width: '100%', height: '500px' }}
                        config={{ responsive: true }}
                      />
                      <Group justify="center">
                        <Text>Day {currentFrame}</Text>
                      </Group>
                    </Stack>
                  )}
                </Tabs.Panel>

                <Tabs.Panel value="stats" className="tab-content">
                  <Grid>
                    <Grid.Col span={6}>
                      <Card withBorder p="md" radius="md" className="stats-card">
                        <Stack>
                          <Text size="lg" fw={500}>Peak Statistics</Text>
                          <Group>
                            <Badge color="red" size="lg">
                              Peak Infected: {results.final_stats.peak_infected}
                            </Badge>
                            <Badge color="yellow" size="lg">
                              Peak Hospitalized: {results.final_stats.peak_hospitalized}
                            </Badge>
                          </Group>
                        </Stack>
                      </Card>
                    </Grid.Col>
                    <Grid.Col span={6}>
                      <Card withBorder p="md" radius="md" className="stats-card">
                        <Stack>
                          <Text size="lg" fw={500}>Final Statistics</Text>
                          <Group>
                            <Badge color="red" size="lg">
                              Total Infected: {results.final_stats.total_infected}
                            </Badge>
                            <Badge color="blue" size="lg">
                              Total Recovered: {results.final_stats.total_recovered}
                            </Badge>
                            <Badge color="gray" size="lg">
                              Total Deceased: {results.final_stats.total_deceased}
                            </Badge>
                          </Group>
                        </Stack>
                      </Card>
                    </Grid.Col>
                  </Grid>
                </Tabs.Panel>
              </Tabs>
            </Stack>
          </Paper>
        )}
      </Stack>
    </Container>
  );
} 