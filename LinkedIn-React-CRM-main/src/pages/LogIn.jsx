import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Container, Paper, TextInput, Button, Title, Text, Group, PasswordInput } from '@mantine/core';
import axios from 'axios';

const LogIn = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post('https://mantisagency.ai/api/login/', {
        username, 
        password
      });
      console.log(response);
  
      if (response.status === 200) {
        const userid = response.data.user_id;  // Declare userid with const
        const superuser = response.data.is_superuser;  // Declare superuser with const
  
        login(userid, superuser);
        navigate('/');
      } else {
        throw new Error(response.data.message || 'Failed to log in');
      }
    } catch (err) {
      setError(err.response ? err.response.data.message : err.message);
    } finally {
      setIsLoading(false);
    }
  };
  

  return (
    <Container size={420} my={40} className='min-h-screen'>
      <Title align="center" mb="lg" c='white'>Log In to Your Account</Title>
      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <TextInput
          label="Username"
          placeholder="Enter your username"
          value={username}
          onChange={(event) => setUsername(event.currentTarget.value)}
          required
        />
        <PasswordInput
          label="Password"
          placeholder="Enter your password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.currentTarget.value)}
          required
          mt="md"
        />
        <Button fullWidth mt="xl" onClick={handleLogin} loading={isLoading} loaderProps={{ type: 'dots' }}>
          Log In
        </Button>
        {error && (
          <Text c="red" size="sm" mt="md">
            {error}
          </Text>
        )}
      </Paper>
    </Container>
  );
};

export default LogIn;
