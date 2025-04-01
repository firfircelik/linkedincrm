import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import routesPath from './utils/routesPath';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import { AuthProvider } from './auth/AuthContext';

const routerConfig = createBrowserRouter([
  {
    path: '/',
    element:(  <AuthProvider> 
    <App />
  </AuthProvider>),
    children: routesPath
  }
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={routerConfig} />
  </React.StrictMode>
);
