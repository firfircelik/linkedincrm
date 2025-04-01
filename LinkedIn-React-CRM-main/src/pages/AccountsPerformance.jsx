import React, { useState, useEffect } from "react";
import {
  Paper,
  Table,
  ScrollArea,
  Text,
  TextInput,
  Select,
  Button,
  Pagination,
  Divider,
} from "@mantine/core";
import PerformanceHeader from "../components/AccountsPerformance/PerformanceHeader";
import PerformanceRow from "../components/AccountsPerformance/PerformanceRow";
import { FaSearch } from "react-icons/fa";
import CustomDatePicker from "../utils/CustomDatePicker";
import axios from "axios";

export default function App() {
  const [performanceData, setPerformanceData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    const fetchPerformanceData = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(
          `https://mantisagency.ai/api/accounts_performance/?start_date=${startDate}&end_date=${endDate}`
        );
        if (response.status === 200 && Array.isArray(response.data.accounts)) {
          setPerformanceData(response.data.accounts);
        } else {
          throw new Error("Failed to fetch accounts");
        }
      } catch (err) {
        setError(err.message || "An error occurred");
        setPerformanceData([]); // Ensure it's always an array
      } finally {
        setIsLoading(false);
      }
    };

    fetchPerformanceData();
  }, [currentPage, startDate, endDate]);

  function handleDate(dates) {
    if (dates) {
      setCurrentPage(1);
      setStartDate(dates[0].toISOString().split("T")[0]);
      setEndDate(dates[1].toISOString().split("T")[0]);
    }
  }

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
          styles={{ input: { backgroundColor: "#323B49" } }}
        />
        <div className="flex gap-2">
          <CustomDatePicker onDateSelected={handleDate} />
        </div>
      </div>
      <ScrollArea>
        <Table verticalSpacing="md">
          <Table.Thead>
            <PerformanceHeader />
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
            ) : performanceData && performanceData.length > 0 ? (
              performanceData.map((campaign) => (
                <PerformanceRow key={campaign.id} {...campaign} />
              ))
            ) : (
              <Table.Tr>
                <Table.Td colSpan="100%" className="text-center text-white">
                  No accounts found.
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </ScrollArea>
      <Divider my="md" size="sm" style={{ borderColor: "#313a49" }} />
      
    </div>
  );
}
