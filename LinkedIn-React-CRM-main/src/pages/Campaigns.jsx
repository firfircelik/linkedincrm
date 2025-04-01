import React, { useState, useEffect } from "react";
import {
  Table,
  ScrollArea,
  TextInput,
  Select,
  Button,
  Divider,
} from "@mantine/core";
import CampaignRow from "../components/Campaigns/CampaignRow";
import CampaignHeader from "../components/Campaigns/CampaignHeader";
import { FaSearch } from "react-icons/fa";
import CustomDatePicker from "../utils/CustomDatePicker";
import axios from "axios";
import CustomPagination from "../utils/CustomPagination";
import CustomSelect from "../utils/CustomSelect";
import { useDebouncedValue } from "@mantine/hooks";

export default () => {
  const [campaignData, setCampaignData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [searchQuery, setSearchQuery] = useState('');
  const [status, setStatus] = useState('All Status');
  const [debounced] = useDebouncedValue(searchQuery, 500);

  useEffect(() => {
    const fetchCampaignData = async () => {
      setIsLoading(true);
      let statusParam = '';
      if (status === 'Active') {
        statusParam = 'pending';
      } else if (status === 'No Active') {
        statusParam = 'finished';
      }
    
      try {
        const superuser = sessionStorage.getItem("superuser");
        const userId = sessionStorage.getItem("userId");
    
        let url = `https://mantisagency.ai/api/campaigns/?page=${currentPage}&start_date=${startDate}&end_date=${endDate}&query=${debounced}&status=${statusParam}`;
        if (superuser !== "true") {
          url += `&user=${userId}`;
        }
    
        const response = await axios.get(url);
    
        if (response.status === 200) {
          setCampaignData(response.data.campaigns);
          setTotalPages(response.data.total_pages);
        } else {
          throw new Error("Failed to fetch campaigns");
        }
      } catch (err) {
        setError(err.message || "An error occurred");
      } finally {
        setIsLoading(false);
      }
    };
    

    fetchCampaignData();
  }, [currentPage, startDate, endDate, debounced, status]);

  const handleSearchChange = (event) => {
    setCurrentPage(1);
    setSearchQuery(event.target.value);
  };

  function handleDate(dates) {
    if (dates) {
      setCurrentPage(1);
      setStartDate(dates[0].toISOString().split("T")[0]);
      setEndDate(dates[1].toISOString().split("T")[0]);
    }
  }

  const handleStatusChange = (value) => {
    setCurrentPage(1);
    setStatus(value);
  };

  return (
    <div className="bg-[#1f2937] my-5 mx-8 rounded-lg min-h-screen">
      <div className="flex p-5 justify-between gap-32">
        <TextInput
          className="flex-grow"
          variant="filled"
          size="md"
          radius="md"
          placeholder="Search by name or others..."
          leftSectionPointerEvents="none"
          leftSection={<FaSearch />}
          styles={{ input: { backgroundColor: "#323B49",color: "#ffffff" } }}
          value={searchQuery}
          onChange={handleSearchChange}
        />
        <div className="flex gap-2">
        <CustomSelect
            placeholder="Pick value"
            data={["All Status", "Active", "No Active"]}
            onChange={handleStatusChange}
            value={status}
          />
          <CustomDatePicker onDateSelected={handleDate} />
          <Button color="#0057E9" variant="filled" size="md" radius="md">
            New Campaign
          </Button>
        </div>
      </div>
      <ScrollArea>
        <Table verticalSpacing="md">
          <Table.Thead>
            <CampaignHeader />
          </Table.Thead>
          <Table.Tbody className="text-white">
            {isLoading ? (
              <Table.Tr>
                <Table.Td colSpan="100%" className="text-center text-white">
                  Loading...
                </Table.Td>
              </Table.Tr>
            ) : error ? (
              <Table.Tr>
                <Table.Td colSpan="100%" className="text-center text-white">
                  Error: {error}
                </Table.Td>
              </Table.Tr>
            ) : campaignData.length > 0 ? (
              campaignData.map((campaign) => (
                <CampaignRow key={campaign.id} {...campaign} />
              ))
            ) : (
              <Table.Tr>
                <Table.Td colSpan="100%" className="text-center text-white">
                  No campaigns found.
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </ScrollArea>
      <Divider my="md" size="sm" style={{ borderColor: "#313a49" }} />
      <CustomPagination
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        totalPages={totalPages}
        data={campaignData}
        error={error}
      />
    </div>
  );
};
