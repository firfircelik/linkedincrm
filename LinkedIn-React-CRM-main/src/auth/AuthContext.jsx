import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // Retrieve initial authentication state and user ID from session storage
  const [isAuthenticated, setIsAuthenticated] = useState(() => sessionStorage.getItem('isLoggedIn') === 'true');
  const [userId, setUserId] = useState(() => sessionStorage.getItem('userId'));

  const login = (userId, superuser) => {
    sessionStorage.setItem('isLoggedIn', 'true');
    sessionStorage.setItem('userId', userId); 
    sessionStorage.setItem('superuser', superuser);// Store user ID in session storage
    setIsAuthenticated(true);
    setUserId(userId);
  };

  const logout = () => {
    sessionStorage.removeItem('isLoggedIn');
    sessionStorage.removeItem('userId'); // Clear user ID from session storage
    setIsAuthenticated(false);
    setUserId(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, userId }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
