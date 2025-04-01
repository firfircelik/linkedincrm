import React from 'react';
import { MantineProvider } from '@mantine/core';
import { Outlet } from 'react-router-dom';
import Header from './components/Header';
import Navbar from './components/Navbar';
import { AuthProvider } from './auth/AuthContext';

function App() {
  return (
    <AuthProvider>
    <MantineProvider>
      <div className='flex bg-[#111827]'>
        <Navbar />
        <div className='flex flex-col w-full'>
          <Header />
          <Outlet />
        </div>
      </div>
    </MantineProvider>
    </AuthProvider>
  );
}

export default App;