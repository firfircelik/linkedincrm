import React, { useEffect, useState } from "react";
import { Button } from "@mantine/core";
import {
  DatePickerComponent,
  FileUploadComponent,
  InputComponent,
  NumberInputComponent,
  SelectComponent,
} from "./AutoComponents";

const LeadPanel = () => {
  const [files, setFiles] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccountId, setSelectedAccountId] = useState("");
  const [campaignName, setCampaignName] = useState("");
  const [dates, setDates] = useState([new Date(), new Date()]);
  const [dailyCount, setDailyCount] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const response = await fetch("https://mantisagency.ai/api/accounts/");
        if (!response.ok) throw new Error("Failed to fetch accounts");
        const data = await response.json();
        setAccounts(data);
      } catch (error) {
        console.error("Failed to fetch accounts", error);
        alert("Failed to load accounts data");
      }
    };
    fetchAccounts();
  }, []);

  const resetForm = () => {
    setFiles([]);
    setSelectedAccountId("");
    setCampaignName("");
    setDates([new Date(), new Date()]);
    setDailyCount("");
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    const formData = new FormData();
    formData.append("category_type", "New");
    formData.append("campaign_name", campaignName);
    formData.append("startDateTime", dates[0].toISOString());
    formData.append("endDateTime", dates[1].toISOString());
    formData.append("daily_count", dailyCount);
    formData.append("account_id", selectedAccountId);
    files.forEach((file) => formData.append("listfile", file));

    try {
      const response = await fetch(
        "https://mantisagency.ai/api/new_campaign/",
        {
          method: "POST",
          body: formData,
        }
      );
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create campaign: ${errorText}`);
      }
      resetForm();
      alert("Campaign created successfully!");
    } catch (error) {
      console.error("Failed to submit campaign", error);
      alert("Error submitting campaign: " + error.message);
    }
    setIsSubmitting(false);
  };

  return (
    <div className="space-y-5">
      <div className="flex gap-4 justify-between w-1/2">
        <InputComponent
          label="Campaign Name"
          placeholder="Campaign Name"
          value={campaignName}
          onChange={(event) => setCampaignName(event.target.value)}
          className="w-1/2"
        />
        <DatePickerComponent
          label="Campaign Duration"
          placeholder="Select Start and End Date"
          value={dates}
          onChange={setDates}
          range
          className="w-1/2"
        />
      </div>
      <div className="flex gap-4 justify-between w-1/2">
        <SelectComponent
          label="Select Account"
          placeholder="Choose an Account"
          data={accounts.map((account) => ({
            value: account.id.toString(),
            label: account.name,
          }))}
          value={selectedAccountId}
          onChange={setSelectedAccountId}
          className="w-1/2"
        />
        <NumberInputComponent
          label="Daily Count"
          placeholder="Enter Number"
          value={dailyCount}
          onChange={(value) => setDailyCount(value)}
          className="w-1/2"
        />
      </div>
      <FileUploadComponent files={files} setFiles={setFiles} />
      <Button
        style={{ marginTop: "30px" }}
        color="#0057E9"
        variant="filled"
        size="md"
        radius="md"
        onClick={handleSubmit}
        disabled={isSubmitting}
      >
        {isSubmitting ? "Submitting..." : "Send Now"}
      </Button>
    </div>
  );
};

export default LeadPanel;
