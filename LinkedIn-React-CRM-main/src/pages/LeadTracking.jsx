import React, { useState, useEffect } from "react";
import { Table, ScrollArea, TextInput } from "@mantine/core";
import { FaPlusCircle, FaSearch } from "react-icons/fa";
import LeadHeader from "../components/LeadTracking/LeadHeader";
import LeadRow from "../components/LeadTracking/LeadRow";
import axios from "axios";
import { IoSettingsSharp } from "react-icons/io5";
import { BsQuestionCircleFill } from "react-icons/bs";
import { RiMessage2Fill } from "react-icons/ri";
import { Star } from "tabler-icons-react";
import { IoMdConstruct } from "react-icons/io";
import CustomPagination from "../utils/CustomPagination";
import { useDebouncedValue } from "@mantine/hooks";
import CustomSelect from "../utils/CustomSelect";

export default () => {
  const [leads, setLeads] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [status, setStatus] = useState('All Status');
  const [debounced] = useDebouncedValue(searchQuery, 500);

  const fetchLeadData = async () => {
    setIsLoading(true);
    setError(null);
    const statusQuery = status !== 'All Status' ? `${status}` : '';
    try {
      const userId = sessionStorage.getItem("userId");
      if (!userId) {
        throw new Error("Userid not found in session storage");
      }
      const response = await axios.get(
        `https://mantisagency.ai/api/cold_leads/${userId}/?page=${currentPage}&query=${debounced}&lead_status=${statusQuery}`
      );
      console.log(response);
      if (response.status === 200) {
        setLeads(response.data.leads);
        setTotalPages(response.data.total_pages);
      } else {
        throw new Error("Failed to fetch leads");
      }
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLeadData();
  }, [currentPage, debounced, status]);

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleStatusChange = (selectedStatus) => {
    setCurrentPage(1);
    setStatus(selectedStatus);
  };

  const refreshLeads = () => {
    fetchLeadData();
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
          styles={{ input: { backgroundColor: "#323B49", color: "#ffffff" } }}
          value={searchQuery}
          onChange={handleSearchChange}
        />
        <div className="flex items-center justify-between gap-5">
          <CustomSelect
            placeholder="Pick value"
            data={[
              "All Status",
              "New",
              "ATC",
              "Call Back",
              "Booked",
              "1st Sat",
              "2nd Sat",
              "3rd Sat",
              "Shouted",
              "Issued",
              "Parked",
              "Lost",
              "Wrong Contact",
            ]}
            onChange={handleStatusChange}
            value={status}
          />
          <RiMessage2Fill size={30} color="#718096" />
          <Star size={30} color="#718096" />
          <IoMdConstruct size={30} color="#718096" />
          <BsQuestionCircleFill size={30} color="#718096" />
          <IoSettingsSharp size={30} color="#718096" />
          <FaPlusCircle size={30} color="#718096" />
        </div>
      </div>
      <ScrollArea>
        <Table verticalSpacing="md">
          <Table.Thead>
            <LeadHeader />
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
            ) : leads.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan="100%" className="text-center text-white">
                  No leads found.
                </Table.Td>
              </Table.Tr>
            ) : (
              leads.map((lead) => (
                <LeadRow
                  key={lead.id}
                  {...lead}
                  onStatusChange={refreshLeads}
                />
              ))
            )}
          </Table.Tbody>
        </Table>
      </ScrollArea>
      <CustomPagination
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        totalPages={totalPages}
        data={leads}
        error={error}
      />
    </div>
  );
};
