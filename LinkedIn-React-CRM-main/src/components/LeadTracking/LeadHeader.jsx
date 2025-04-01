import { Table, Text } from "@mantine/core";

const LeadHeader = () => {
  const headers = [
    { key: "profile", label: "Profile" },
    { key: "status", label: "Status" },
    { key: "link", label: "Link" },
    { key: "company", label: "Company" },
    { key: "title", label: "Title" },
    { key: "email", label: "Email" },
    { key: "phone", label: "Phone" },
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

export default LeadHeader;
