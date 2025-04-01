import { Table, Text } from "@mantine/core";

const PerformanceHeader = () => {
  const headers = [
    { key: "account", label: "Account" },
    { key: "sent", label: "Sent" },
    { key: "located", label: "Located" },
    { key: "excluded", label: "Excluded" },
    { key: "accepted", label: "Accepted" },
    { key: "replied", label: "Replied" },
    { key: "contactsShared", label: "Contacts Shared" },

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

export default PerformanceHeader;
