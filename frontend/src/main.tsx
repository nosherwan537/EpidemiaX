import React from 'react'
import ReactDOM from 'react-dom/client'
import { MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MantineProvider
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
      <App />
    </MantineProvider>
  </React.StrictMode>
) 