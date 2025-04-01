import { Table, Text } from "@mantine/core";

const CampaignHeader = () => {
  const headers = [
    { key: "campaigns", label: "Campaigns" },
    { key: "totalLeads", label: "Total leads" },
    { key: "connectionsSent", label: "Connections Sent" },
    { key: "excluded", label: "Excluded" },
    { key: "accepted", label: "Accepted" },
    { key: "acceptanceRate", label: "Acceptance Rate" },
    { key: "Scrapped", label: "Scrapped" },
    { key: "active", label: "Active" },
  ];
  return (
    <Table.Tr
      className="text-[#718096]"
      style={{
        borderColor: "#313a49",
        borderBottomWidth: "2px",
        borderTopWidth: "2px",
      }}
    >
      {headers.map((header) => (
        <Table.Th key={header.key}>
          <Text fw={500} style={{ padding: "10px", textAlign: "center" }}>
            {header.label}
          </Text>
        </Table.Th>
      ))}
    </Table.Tr>
  );
};

export default CampaignHeader;
