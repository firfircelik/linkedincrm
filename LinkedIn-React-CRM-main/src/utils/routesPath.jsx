import React from 'react';
import Campaigns from '../pages/Campaigns';
import Pipeline from '../pages/Pipeline';
import Accounts from '../pages/Accounts';
import Prompts from '../pages/Prompts';
import Analytics from '../pages/Analytics';
import Settings from '../pages/Settings';
import User from '../pages/User';
import LeadTracking from '../pages/LeadTracking';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import LogIn from '../pages/LogIn';
import AccountsPerformance from '../pages/AccountsPerformance';
import AutoCampaigns from '../pages/AutoCampaigns';
import AddAccount from '../pages/AddAccount';


const routesPath = [
  {
    path: '/',
    element: <ProtectedRoute><User /></ProtectedRoute>,
  },
  {
    path: '/campaign',
    element: <ProtectedRoute><Campaigns /></ProtectedRoute>,
  },
  {
    path: '/pipeline',
    element: <ProtectedRoute><Pipeline /></ProtectedRoute>,
  },
  {
    path: '/accounts',
    element: <ProtectedRoute><Accounts /></ProtectedRoute>,
  },
  {
    path: '/prompts',
    element: <ProtectedRoute><Prompts /></ProtectedRoute>,
  },
  {
    path: '/analytics',
    element: <ProtectedRoute><Analytics /></ProtectedRoute>,
  },
  {
    path: '/lead',
    element: <ProtectedRoute><LeadTracking /></ProtectedRoute>,
  },
  {
    path: '/autocampaign',
    element: <ProtectedRoute><AutoCampaigns /></ProtectedRoute>,
  },
  {
    path: '/accounts_performance',
    element: <ProtectedRoute><AccountsPerformance /></ProtectedRoute>,
  },
  {
    path: '/settings',
    element: <ProtectedRoute><Settings /></ProtectedRoute>,
  },
  {
    path: '/user',
    element: <ProtectedRoute><User /></ProtectedRoute>,
  },
  {
    path: '/login',
    element: <LogIn />,
  },
  // {
  //   path: '/',
  //   element: <Logout />,
  // }
];

export default routesPath;
