import { Avatar, Select, Table } from "@mantine/core";
import axios from "axios";
import dayjs from "dayjs";
import { useCallback, useState } from "react";
import { FaLinkedin } from 'react-icons/fa';  
import CustomSelect from "../../utils/CustomSelect";
import EditableText from "../../utils/EditableText";


const LeadRow = ({
  id,
  name,
  lead_status,
  link,
  contact_number,
  onStatusChange,
}) => {
  const formatDate = (dateString) => {
    if (!dateString) return "";
    return dayjs(dateString).format("MMMM D, YYYY, h:mm:ss A");
  };

  const statusColors = {
    "New": "#B6D7A8",
    "ATC": "#F9CB9C",
    "Call Back": "#FFE599",
    "Booked": "#A4C2F4",
    "1st Sat": "#D9D2E9",
    "2nd Sat": "#EAD1DC",
    "3rd Sat": "#E06666",
    "Shouted": "#C9DAF8",
    "Issued": "#B4A7D6",
    "Parked": "#D5A6BD",
    "Lost": "#999999",
    "Wrong Contact": "#434343",
  };

  const [selectedStatus, setSelectedStatus] = useState(lead_status);

  const handleStatusChange = useCallback(
    async (value) => {
      try {
        const response = await axios.get(
          `https://mantisagency.ai/api/profiles/update-lead-status/${id}/?lead_status=${value}`
        );
        if (response.status === 200) {
          onStatusChange();
          setSelectedStatus(value);
        } else {
          console.error("Failed to update lead status");
        }
      } catch (error) {
        console.error("Error updating lead status:", error);
      }
    },
    [onStatusChange, id]
  );

  const saveContactNumber = async (updatedNumber) => {
    try {
      const response = await axios.patch(`https://mantisagency.ai/api/profile/${id}/`, {
  contact_number: updatedNumber
});
      if (response.status !== 200) {
        console.error("Failed to update contact number");
      }
    } catch (error) {
      console.error("Error updating contact number:", error);
    }
  };

  return (
    <Table.Tr
      style={{
        borderColor: "#313a49",
        borderBottomWidth: "2px",
        borderTopWidth: "2px",
      }}
    >
      <Table.Td style={{ textAlign: "center" }}>
        <div className="flex justify-start items-center gap-2">
          <Avatar radius="xl" />
          {name}
        </div>
      </Table.Td>
      <Table.Td style={{ textAlign: "center", minWidth: "fit-content" }}>
      <CustomSelect
          placeholder="Pick value"
          data={Object.keys(statusColors).map((status) => ({
            value: status,
            label: status,
            style: { backgroundColor: statusColors[status], color: 'white' },
          }))}
          onChange={handleStatusChange}
          value={selectedStatus || 'New'}
          statusColors={statusColors}
          />
      </Table.Td>
      <Table.Td style={{ textAlign: "center", position: 'relative' }}>
        <a href={link} target="_blank" rel="noopener noreferrer" title="LinkedIn Profile" style={{ position: 'absolute', left: '40px' }}>
          <FaLinkedin size={20} style={{ color: '#0e76a8' }} />
        </a>
      </Table.Td>

      <Table.Td style={{ textAlign: "center" }}></Table.Td>
      <Table.Td style={{ textAlign: "center" }}></Table.Td>
      <Table.Td style={{ textAlign: "center" }}></Table.Td>
      <Table.Td style={{ textAlign: "center" }}>
      <EditableText initialText={contact_number} save={saveContactNumber} />
        </Table.Td>
    </Table.Tr>
  );
};

export default LeadRow;
