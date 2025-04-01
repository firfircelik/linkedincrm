import { useState, useEffect } from "react";
import { Button, MultiSelect, Select } from "@mantine/core";
import {
  DatePickerComponent,
  InputComponent,
  NumberInputComponent,
  RangeSliderComponent,
  SelectComponent,
} from "./AutoComponents";

const ScrapPanel = () => {
  const [category, setCategory] = useState("");
  const [options, setOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState("");
  const [campaignName, setCampaignName] = useState("");
  const [schedule, setSchedule] = useState([new Date(), new Date()]);
  const [batchSize, setBatchSize] = useState(0);
  const [booleanSearch, setBooleanSearch] = useState("");
  const [surBooleanSearch, setSurBooleanSearch] = useState("");
  const [pageRange, setPageRange] = useState([20, 80]);
  const [nationality, setNationality] = useState("");
  const [excludedNationalities, setExcludedNationalities] = useState([]);
  const [firstNames, setFirstNames] = useState([]);
  const [firstNamesExclude, setFirstNamesExclude] = useState([]);
  const [batchOptions, setBatchOptions] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState("");

  const userId = sessionStorage.getItem("userId");

  const pageMarks = [
    { value: 100, label: "100" },
    { value: 200, label: "200" },
    { value: 300, label: "300" },
    { value: 400, label: "400" },
    { value: 500, label: "500" },
    { value: 600, label: "600" },
    { value: 700, label: "700" },
    { value: 800, label: "800" },
    { value: 900, label: "900" },
  ];

  // Data mapping from the previous result
  const nationalityCountMap = {
    "Abkhazia": 254,
    "Afghanistan": 1000,
    "Albania": 446,
    "Algeria": 0,
    "Andorra": 1001,
    "Angola": 155,
    "Austria": 699,
    "Azerbaijan": 1001,
    "Bangladesh": 444,
    "Benin": 999,
    "Bhutan": 1089,
    "Bolivia": 910,
    "Brazil": 1000,
    "Brunei": 340,
    "Bulgaria": 1002,
    "Burkina Faso": 1021,
    "Burundi": 47,
    "Cambodia": 999,
    "Cameroon": 999,
    "China": 268,
    "Czech Republic": 518,
    "Djibouti": 25,
    "Eastern Africa": 53,
    "England": 14672,
    "Ethiopia": 76,
    "France": 273,
    "Ghana": 50,
    "Germany": 718,
    "Greece": 203,
    "Hong Kong": 1000,
    "Hungary": 1000,
    "India": 1000,
    "Indonesia": 1000,
    "Iran": 1000,
    "Iraq": 597,
    "Ireland": 1234,
    "Isreal": 903,
    "Ivory Coast": 1000,
    "Japan": 1000,
    "Jordan": 886,
    "Kazakhstan": 1000,
    "Kenya": 1012,
    "Korea": 94,
    "Kosovo": 1004,
    "Kuwait": 248,
    "Kyrgyzstan": 1000,
    "Laos": 400,
    "Latvia": 253,
    "Lebanon": 1000,
    "Lesotho": 999,
    "Libya": 0,
    "Liechtenstein": 1079,
    "Lithuania": 279,
    "Madagascar": 52,
    "Malawi": 256,
    "Malaysia": 1001,
    "Maldives": 1012,
    "Mali": 195,
    "Malta": 171,
    "Mauritania": 1001,
    "Mauritius": 1003,
    "Mexico": 1003,
    "Middle East": 2000,
    "Moldova": 419,
    "Mongolia": 419,
    "Montenegro": 1002,
    "Morocco": 279,
    "Mozambique": 54,
    "Myanmar": 171,
    "Namibia": 593,
    "Nepal": 1000,
    "Netherlands": 983,
    "Niger": 78,
    "Nigeria": 168,
    "Poland": 139,
    "Portugal": 73,
    "Russia": 9384,
    "Saudi Arabia": 1000,
    "Scottland": 100,
    "Sierra Leone": 59,
    "Singapore": 1000,
    "Somalia": 25,
    "South Africa": 48,
    "South East Asia": 0,
    "Spain": 1000,
    "Swaziland": 140,
    "Sweden": 1013,
    "Switzerland": 620,
    "Taiwan": 1001,
    "Tajikistan": 1000,
    "Tanzania": 1000,
    "Thailand": 1000,
    "Togo": 45,
    "Tunisia": 1008,
    "Turkey": 1000,
    "Turkmenistan": 162,
    "Uganda": 1000,
    "United Arab Emirates": 1000,
    "Uruguay": 1000,
    "Uzbekistan": 233,
    "Venezuela": 1006,
    "Vietnam": 1000,
    "Zambia": 985,
    "Zimbabwe": 1000
  };

  const firstNamesData = [
    { value: 'English', label: 'English' },
    { value: 'Afrikaans', label: 'Afrikaans' },
    { value: 'Hispanic', label: 'Hispanic' },
  ];

  useEffect(() => {
    if (nationality) {
      const totalNames = nationalityCountMap[nationality];
      const batches = Math.ceil(totalNames / 100);
      const batchOptions = Array.from({ length: batches }, (_, i) => ({
        value: `${i + 1}`,
        label: `Batch ${i + 1}`,
      }));
      setBatchOptions(batchOptions);
      setSelectedBatch(""); // Reset batch selection on nationality change
    }
  }, [nationality]);

  useEffect(() => {
    const apiUrl =
      category === "leads_list"
        ? `https://mantisagency.ai/api/leadslist/${userId}/`
        : `https://mantisagency.ai/api/savedsearches/${userId}/`;

    const fetchOptions = async () => {
      const response = await fetch(apiUrl);
      const data = await response.json();
      setOptions(
        data.map((option) => ({
          value: option.id.toString(),
          label: option.name,
        }))
      );
    };

    if (userId && category) {
      fetchOptions();
    }
  }, [category]);

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("campaign_name", campaignName);
    formData.append("startDateTime", schedule[0].toISOString());
    formData.append("endDateTime", schedule[1].toISOString());
    formData.append("category_type", "AutoScrapper");
    formData.append("batch_size", batchSize.toString());
    formData.append("acategory", category);
    formData.append("minpage", pageRange[0].toString());
    formData.append("maxpage", pageRange[1].toString());
    formData.append("includeNationality", nationality);
    formData.append("excludeNationality", excludedNationalities.join(','));
    formData.append("firstNames", firstNames.join(','));
    formData.append("firstNamesExclude", firstNamesExclude.join(','));
    formData.append("nationalityBatch", selectedBatch); // Include batch in form data

    if (category === "leads_list") {
      formData.append("lead_list", selectedOption);
    } else {
      formData.append("saved_search", selectedOption);
      formData.append("booleanSearch", booleanSearch);
      formData.append("SurBooleanSearch", surBooleanSearch);
    }

    const response = await fetch("https://mantisagency.ai/api/new_campaign/", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const responseData = await response.json();
      console.log("Campaign created successfully:", responseData);
      alert("Campaign created successfully!");
    } else {
      console.error("Failed to create campaign");
      alert("Failed to create campaign");
    }
  };

  const nationalitiesData = Object.keys(nationalityCountMap).map(nationality => ({
    value: nationality,
    label: nationality
  }));

  return (
    <div className="space-y-5">
      <div className="flex gap-4 justify-between w-1/2">
        <InputComponent
          label="Campaign Name"
          placeholder="Campaign Name"
          value={campaignName}
          onChange={(e) => setCampaignName(e.target.value)}
          className="w-1/2"
        />
        <DatePickerComponent
          label="Start and End Date"
          placeholder="Select Date Range"
          value={schedule}
          onChange={setSchedule}
          className="w-1/2"
        />
      </div>
      <div className="flex gap-4 justify-between w-1/2">
        <SelectComponent
          label="Category"
          placeholder="Select category"
          className={category === "leads_list" ? "w-[49%]" : "w-1/2"}
          data={[
            { value: "saved_search", label: "Saved searches" },
            { value: "leads_list", label: "Leads List" },
          ]}
          value={category}
          onChange={(value) => setCategory(value)}
        />
        {category !== "leads_list" && (
          <InputComponent
            label="Boolean Search"
            placeholder="Boolean Search"
            value={booleanSearch}
            onChange={(e) => setBooleanSearch(e.target.value)}
            className="w-1/2"
          />
        )}
        {category !== "leads_list" && (
          <InputComponent
            label="Surname Boolean Search"
            placeholder="Surname Boolean Search"
            value={surBooleanSearch}
            onChange={(e) => setSurBooleanSearch(e.target.value)}
            className="w-1/2"
          />
        )}
      </div>
      <div className="flex gap-4 justify-between w-1/2">
        <NumberInputComponent
          label="Batch Size"
          placeholder="Enter Batch Size"
          value={batchSize}
          onChange={(value) => setBatchSize(value)}
          className="w-1/2"
        />
        <SelectComponent
          label={
            category === "leads_list" ? "Category Options" : "Saved Searches"
          }
          placeholder={
            category === "leads_list"
              ? "Select Category Option"
              : "Choose saved search"
          }
          className="w-1/2"
          data={options}
          value={selectedOption}
          onChange={(value) => setSelectedOption(value)}
        />
      </div>
      <div className="flex gap-4 justify-between w-1/2">
        <SelectComponent
          label="Include Nationality"
          placeholder="Select nationality"
          data={nationalitiesData}
          value={nationality}
          onChange={setNationality}
          className="w-1/2"
        />
        <SelectComponent
          label="Select Batch"
          placeholder="Select batch"
          data={batchOptions}
          value={selectedBatch}
          onChange={setSelectedBatch}
          className="w-1/2"
          disabled={!nationality} // Disable until nationality is selected
        />
      </div>
      <MultiSelect
      data={nationalitiesData}
      placeholder="Select nationalities to exclude"
      label="Exclude Nationalities"
      value={excludedNationalities}
      onChange={setExcludedNationalities}
      className="w-1/2"
      styles={{
        input: {
          color: "white",
          backgroundColor: "transparent",
          borderWidth: "1px",
          borderColor: "#313a49",
          borderStyle: "solid",
        },
        label: {
          color: "#718096",
        },
      }}
    />
    <MultiSelect
      data={firstNamesData}
      placeholder="Select First Names Group"
      label="Include First Names"
      value={firstNames}
      onChange={setFirstNames}
      className="w-1/2"
      styles={{
        input: {
          color: "white",
          backgroundColor: "transparent",
          borderWidth: "1px",
          borderColor: "#313a49",
          borderStyle: "solid",
        },
        label: {
          color: "#718096",
        },
      }}
    />
    <MultiSelect
      data={firstNamesData}
      placeholder="Select First Names Group"
      label="Exclude First Names"
      value={firstNamesExclude}
      onChange={setFirstNamesExclude}
      className="w-1/2"
      styles={{
        input: {
          color: "white",
          backgroundColor: "transparent",
          borderWidth: "1px",
          borderColor: "#313a49",
          borderStyle: "solid",
        },
        label: {
          color: "#718096",
        },
      }}
    />

      <Button
        style={{ marginTop: "30px" }}
        color="#0057E9"
        variant="filled"
        size="md"
        radius="md"
        onClick={handleSubmit}
      >
        Send Now
      </Button>
    </div>
  );
};

export default ScrapPanel;
