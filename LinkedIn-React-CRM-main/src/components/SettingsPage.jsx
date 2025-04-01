import React, { useState, useEffect } from "react";
import { Button, Card, Grid, Select, TextInput, Textarea } from "@mantine/core";
import { IconDownload } from "@tabler/icons-react";

const SettingsPage = () => {
  const [downloadFiles, setDownloadFiles] = useState([]);
  const [DownloadFileId, setDownloadFile] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [linkedinUser, setLinkedinUser] = useState(null);
  const [scrapperDetails, setScrapperDetails] = useState(null);
  const userId = sessionStorage.getItem("userId");
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    linkedin_cookies: "",
    scrapper_ip: "",
    scrapper_port: "",
    scrapper_user: "",
    scrapper_pass: "",
    user_id: userId
  });

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const superuser = sessionStorage.getItem("superuser");
        const userId = sessionStorage.getItem("userId");
        let url = `https://mantisagency.ai/api/settings/leads-list/`;
        if (superuser !== "true") {
          url += `?user=${userId}`;
        }
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to fetch leads: ${response.statusText}`);
        const data = await response.json();
        setDownloadFiles(data.leads); // Extract the leads array
      } catch (error) {
        console.error("Failed to fetch download files", error);
        alert(`Failed to load download files: ${error.message}`);
      }
    };
    fetchLeads();
  }, []);

  useEffect(() => {
    const fetchUserDetails = async () => {
      // Fetch LinkedIn user and scrapper details from the API
      // Update the state with the fetched details
    };

    fetchUserDetails();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    console.log("Form submitted:", formData);
    try {
      const response = await fetch(`https://mantisagency.ai/api/settings/connect_linkedin_account/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      console.log("Response status:", response.status);
      const responseText = await response.text();
      console.log("Response text:", responseText);
      
      const result = JSON.parse(responseText);
      if (response.ok) {
        setLinkedinUser(result.linkedin_user);
        setScrapperDetails(result.scrapper_details);
        setFormData({
          email: "",
          password: "",
          linkedin_cookies: "",
          scrapper_ip: "",
          scrapper_port: "",
          scrapper_user: "",
          scrapper_pass: "",
          user_id: userId
        });
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error("Error submitting form:", error);
      alert(`Error submitting form: ${error.message}`);
    }
  };

  const handleRemove = async () => {
    // Remove LinkedIn account and scrapper proxy via API
    // Clear state after successful removal
    setLinkedinUser(null);
    setScrapperDetails(null);
  };

  const resetForm = () => {
    setDownloadFile("");
  };

  const handleDownloadSubmit = async () => {
    if (!DownloadFileId) {
      alert("Please select a file to download");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(`https://mantisagency.ai/api/settings/download_leads/${DownloadFileId}/`);
      if (!response.ok) throw new Error(`Failed to download file: ${response.statusText}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = `${DownloadFileId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      resetForm();
    } catch (error) {
      console.error("Failed to download file", error);
      alert(`Failed to download file: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="settings-page">
      <Card shadow="sm" padding="lg" className="settings-card">
        {!linkedinUser ? (
          <form onSubmit={handleFormSubmit}>
            <div className="form-container">
              <h2 className="mb-4">Enter LinkedIn Credentials</h2>
              <Grid>
                <Grid.Col span={12}>
                  <TextInput
                    label="Email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    fullWidth
                  />
                </Grid.Col>
                <Grid.Col span={12}>
                  <TextInput
                    label="Password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    fullWidth
                  />
                </Grid.Col>
                <Grid.Col span={12}>
                  <Textarea
                    label="Cookies"
                    name="linkedin_cookies"
                    value={formData.linkedin_cookies}
                    onChange={handleInputChange}
                    required
                    fullWidth
                  />
                </Grid.Col>
                <Grid.Col span={12}>
                  <TextInput
                    label="Scrapper IP"
                    name="scrapper_ip"
                    value={formData.scrapper_ip}
                    onChange={handleInputChange}
                    required
                    fullWidth
                  />
                </Grid.Col>
                <Grid.Col span={12}>
                  <TextInput
                    label="Scrapper Port"
                    name="scrapper_port"
                    value={formData.scrapper_port}
                    onChange={handleInputChange}
                    required
                    fullWidth
                  />
                </Grid.Col>
                <Grid.Col span={12}>
                  <TextInput
                    label="Scrapper User"
                    name="scrapper_user"
                    value={formData.scrapper_user}
                    onChange={handleInputChange}
                    required
                    fullWidth
                  />
                </Grid.Col>
                <Grid.Col span={12}>
                  <TextInput
                    label="Scrapper Password"
                    name="scrapper_pass"
                    value={formData.scrapper_pass}
                    onChange={handleInputChange}
                    required
                    fullWidth
                  />
                </Grid.Col>
              </Grid>
              <div className="d-flex justify-content-end mt-3">
                <Button type="submit" color="blue" variant="outline">Submit</Button>
              </div>
            </div>
          </form>
        ) : (
          <div className="form-container mt-5">
            <h2 className="mb-4">Connected LinkedIn Account</h2>
            <div className="details-container">
              <div className="detail-row">
                <span className="detail-key"><strong>Email:</strong></span>
                <span className="detail-value">{linkedinUser.email}</span>
              </div>
              <div className="detail-row">
                <span className="detail-key"><strong>Scrapper IP:</strong></span>
                <span className="detail-value">{scrapperDetails.proxyip}</span>
              </div>
              <div className="detail-row">
                <span class="detail-key"><strong>Scrapper PORT:</strong></span>
                <span class="detail-value">{scrapperDetails.proxyport}</span>
              </div>
              <div class="detail-row">
                <span class="detail-key"><strong>Scrapper Username:</strong></span>
                <span class="detail-value">{scrapperDetails.proxyuser}</span>
              </div>
              <div class="detail-row">
                <span class="detail-key"><strong>Scrapper Password:</strong></span>
                <span class="detail-value">{scrapperDetails.proxypass}</span>
              </div>
            </div>
            <div class="d-flex justify-content-end mt-3">
              <Button onClick={handleRemove} color="red" variant="outline">Remove</Button>
            </div>
          </div>
        )}
      </Card>
      
      <Card shadow="sm" padding="lg" className="settings-card mt-4">
        <Grid>
          <Grid.Col span={12}>
            <Select
              label="Select File to Download"
              placeholder="Choose File"
              data={downloadFiles.map((file) => ({
                value: file.id.toString(),
                label: file.name,
              }))}
              value={DownloadFileId}
              onChange={setDownloadFile}
              style={{ marginBottom: '20px' }}
            />
          </Grid.Col>
          <Grid.Col span={12}>
            <Button
              color="blue"
              variant="filled"
              size="md"
              radius="md"
              onClick={handleDownloadSubmit}
              disabled={isSubmitting}
              leftIcon={<IconDownload size={18} />}
              fullWidth
            >
              {isSubmitting ? "Downloading..." : "Download Now"}
            </Button>
          </Grid.Col>
        </Grid>
      </Card>

      <style jsx>{`
        .settings-page {
          padding: 20px;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
          align-items: center;
          background-color: #141A26; /* Matching background color */
        }
        .settings-card {
          max-width: 600px;
          width: 100%;
          padding: 20px;
          background-color: #ffffff; /* Card background */
        }
        .form-container {
          width: 100%;
        }
        @media (max-width: 600px) {
          .settings-card {
            padding: 10px;
          }
          .form-container {
            padding: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default SettingsPage;
