import React from 'react';
import { Text, Stack } from '@mantine/core';
import { NavLink, useNavigate } from 'react-router-dom';
import { MdCampaign } from 'react-icons/md';
import { Logout, Prompt, Settings } from 'tabler-icons-react';
import { RiUserFill } from 'react-icons/ri';
import { TbFilterFilled } from 'react-icons/tb';
import { BsDatabaseFillGear, BsFileBarGraphFill } from 'react-icons/bs';
import { AiFillAccountBook } from 'react-icons/ai';
import { useAuth } from '../../auth/AuthContext';

export default () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  // Modify logout function to navigate to login page and ensure user interface updates
  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true }); // Ensures navigation does not create history entry
  };
  const superuser = sessionStorage.getItem("superuser");
  let navItems = [];
  if (superuser === "true") 
{
  navItems = [
    { icon: MdCampaign, label: 'Campaigns', path: '/campaign' },
    { icon: TbFilterFilled, label: 'Pipeline', path: '/pipeline' },
    { icon: AiFillAccountBook, label: 'Accounts', path: '/accounts' },
    { icon: Prompt, label: 'Prompts', path: '/prompts' },
    { icon: BsFileBarGraphFill, label: 'Analytics', path: '/analytics' },
    { icon: BsDatabaseFillGear, label: 'Leads', path: '/lead' },
    { icon: MdCampaign, label: 'Automation Campaigns', path: '/autocampaign' },
    { icon: BsDatabaseFillGear, label: 'Accounts Performance', path: '/accounts_performance' },
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: RiUserFill, label: 'User Metrics', path: '/user' },
    { icon: Logout, label: 'Logout', path: '/login', action: handleLogout },
  ];
}
else
{
  navItems = [
    { icon: MdCampaign, label: 'Campaigns', path: '/campaign' },
    { icon: BsDatabaseFillGear, label: 'Tracking Leads', path: '/lead' },
    { icon: MdCampaign, label: 'Automation Campaigns', path: '/autocampaign' },
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: Logout, label: 'Logout', path: '/login', action: handleLogout },
  ];
}

  return (
    <nav className="bg-[#1f2937] w-56 flex flex-col p-5 space-y-16">
      <Text
        component="p"
        style={{
          fontFamily: 'Poppins, sans-serif',
          fontSize: '18.86px',
          fontWeight: '700',
          lineHeight: '18.86px',
          textAlign: 'left',
          color: '#76A8FF',
        }}
      >
        LinkedIn Automation CRM
      </Text>
      
      <Stack align="flex-start" justify="center" gap="sm">
        {navItems.map((item) => (
          <NavLink
            to={isAuthenticated || item.label === 'Logout' ? item.path : '#'}
            key={item.label}
            onClick={(e) => {
              if (!isAuthenticated && item.label !== 'Logout') {
                e.preventDefault();  // Prevent navigation for non-logout items when not authenticated
              } else {
                item.action?.();
              }
            }}
            className={({ isActive }) =>
              `flex items-center p-2 rounded-md text-sm font-medium w-full hover:bg-[#76a8ff] hover:text-[#1352bf] ${
                isActive && isAuthenticated ? 'text-[#1352bf]' : 'text-[#718096]'
              } ${!isAuthenticated ? 'opacity-50 cursor-not-allowed' : ''}`
            }
            style={({ isActive }) => ({
              backgroundColor: isActive && isAuthenticated ? '#76a8ff' : undefined,
            })}
          >
            {({ isActive }) => (
              <>
                <item.icon color={isActive && isAuthenticated ? '#1352bf' : '#718096'} size={22} />
                <span className="ml-3">{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </Stack>
      
    </nav>
  );
}
