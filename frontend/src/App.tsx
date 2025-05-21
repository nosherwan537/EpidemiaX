import React, { useState } from 'react';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { SimulationDashboard } from './components/SimulationDashboard';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import './index.css';

function App() {
  const [colorScheme, setColorScheme] = useState<'light' | 'dark'>('light');
  const toggleColorScheme = (value?: 'light' | 'dark') =>
    setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));

  return (
    <MantineProvider
      defaultColorScheme={colorScheme}
      theme={{
        primaryColor: 'blue',
        fontFamily: 'Inter var, sans-serif',
        components: {
          Paper: {
            defaultProps: {
              className: 'glass-morphism',
            },
          },
          Button: {
            defaultProps: {
              className: 'gradient-border',
            },
          },
        },
      }}
    >
      <Notifications />
      <div className={`${colorScheme === 'dark' ? 'dark-theme' : 'light-theme'}`}>
        {/* Glass Background */}
        <div className="glass-background">
          <div className="blob blob-1" />
          <div className="blob blob-2" />
          <div className="blob blob-3" />
          <div className="blob blob-4" />
          <div className="blob blob-5" />
          <div className="blob blob-6" />
          <div className="blob blob-7" />
          <div className="blob blob-8" />
        </div>
        
        {/* Floating Orbs */}
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        
        {/* Main Content */}
        <div className="min-h-screen relative">
          <header className="p-4 border-b border-white/10">
            <div className="container mx-auto flex justify-between items-center">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">
                EpidemiaX
              </h1>
            </div>
          </header>
          <main className="container mx-auto py-8">
            <SimulationDashboard />
          </main>
        </div>
      </div>
    </MantineProvider>
  );
}

export default App; 