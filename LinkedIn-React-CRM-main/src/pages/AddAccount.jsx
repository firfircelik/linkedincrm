import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  TextInput,
  Button,
  Textarea,
  Select,
  Divider,
} from '@mantine/core';
import { showNotification } from '@mantine/notifications';
import axios from 'axios';

const AddAccount = () => {
  const [leadId, setLeadId] = useState('');
  const [leads, setLeads] = useState([]);
  const [linkedinUser, setLinkedinUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [cookies, setCookies] = useState('');
  const [scrapperIP, setScrapperIP] = useState('');
  const [scrapperPort, setScrapperPort] = useState('');

  useEffect(() => {
    axios.get('/api/settings/leads-list/')
      .then(response => {
        setLeads(Array.isArray(response.data) ? response.data : []);
      })
      .catch(error => {
        console.error('Error fetching leads:', error);
        setLeads([]);
      });

    axios.get('/api/settings/connect_linkedin_account/')
      .then(response => {
        setLinkedinUser(response.data);
      })
      .catch(error => {
        console.error('Error fetching LinkedIn user:', error);
        setLinkedinUser(null);
      });
  }, []);

  const handleDownloadLeads = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`/api/settings/download_leads/${leadId}/`);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'leads.csv');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Error downloading leads:', error);
      showNotification({
        title: 'Error',
        message: 'Failed to download leads',
        color: 'red',
      });
    }
  };

  const handleRemoveLinkedin = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/settings/connect_linkedin_account/', { linkedin_id: linkedinUser.id });
      setLinkedinUser(null);
      showNotification({
        title: 'Success',
        message: 'LinkedIn account removed successfully',
        color: 'green',
      });
    } catch (error) {
      console.error('Error removing LinkedIn account:', error);
      showNotification({
        title: 'Error',
        message: 'Failed to remove LinkedIn account',
        color: 'red',
      });
    }
  };

  const handleConnectLinkedin = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    formData.append('cookies', cookies);
    formData.append('scrapper_ip', scrapperIP);
    formData.append('scrapper_port', scrapperPort);

    try {
      await axios.post('/api/settings/connect_linkedin_account/', formData);
      showNotification({
        title: 'Success',
        message: 'LinkedIn account connected successfully',
        color: 'green',
      });
      // Refresh the LinkedIn user data
      const response = await axios.get('/api/settings/connect_linkedin_account/');
      setLinkedinUser(response.data);
    } catch (error) {
      console.error('Error connecting LinkedIn account:', error);
      showNotification({
        title: 'Error',
        message: 'Failed to connect LinkedIn account',
        color: 'red',
      });
    }
  };

  return (
    <Container>
      <form onSubmit={handleDownloadLeads}>
        <Grid>
          <Grid.Col span={12}>
            <h2>Download Leads File</h2>
          </Grid.Col>
          <Grid.Col span={6}>
            <Select
              label="Select a Lead"
              value={leadId}
              onChange={(e) => setLeadId(e.target.value)}
              data={leads.map(lead => ({
                value: lead.id,
                label: lead.name ? lead.name : `Uploaded ${lead.profile_link_count} leads on ${new Date(lead.created_at).toLocaleDateString()}`
              }))}
              required
            />
          </Grid.Col>
          <Grid.Col span={12} display="flex" justifyContent="flex-end">
            <Button type="submit" variant="outline" color="green">Download</Button>
          </Grid.Col>
        </Grid>
      </form>

      <Divider my="md" />

      {!linkedinUser ? (
        <form onSubmit={handleConnectLinkedin}>
          <Grid>
            <Grid.Col span={12}>
              <h2>Enter LinkedIn Credentials</h2>
            </Grid.Col>
            <Grid.Col span={6}>
              <TextInput
                label="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <TextInput
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Grid.Col>
            <Grid.Col span={12}>
              <Textarea
                label="Cookies"
                value={cookies}
                onChange={(e) => setCookies(e.target.value)}
                required
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <TextInput
                label="Scrapper IP"
                value={scrapperIP}
                onChange={(e) => setScrapperIP(e.target.value)}
                required
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <TextInput
                label="Scrapper Port"
                value={scrapperPort}
                onChange={(e) => setScrapperPort(e.target.value)}
                required
              />
            </Grid.Col>
            <Grid.Col span={12} display="flex" justifyContent="flex-end">
              <Button type="submit" variant="outline" color="blue">Connect</Button>
            </Grid.Col>
          </Grid>
        </form>
      ) : (
        <Grid>
          <Grid.Col span={12}>
            <h2>Connected LinkedIn Account</h2>
          </Grid.Col>
          <Grid.Col span={12}>
            <Button
              variant="outline"
              color="red"
              onClick={handleRemoveLinkedin}
            >
              Remove LinkedIn Account
            </Button>
          </Grid.Col>
        </Grid>
      )}
    </Container>
  );
};

export default AddAccount;
