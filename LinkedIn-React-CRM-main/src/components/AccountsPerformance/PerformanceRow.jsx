import { Table, RingProgress, Text, Avatar } from "@mantine/core";

const PerformanceRow = ({
  name,
  total_profiles,
  sent_profiles,
  excluded_profiles,
  accepted_profiles,
  replied_profiles,
  contact_shared_profiles,
  accepted_rate,
  replied_rate,
  contact_shared_rate
}) => {

  return (
    <Table.Tr
      style={{
        borderColor: "#313a49",
        borderBottomWidth: "2px",
        borderTopWidth: "2px",
      }}
    >
      <Table.Td>
      <div className="flex justify-start items-center gap-2"><Avatar radius="xl" />{name}</div>
      </Table.Td>
      <Table.Td style={{ textAlign: "center" }}>{total_profiles}</Table.Td>
      <Table.Td style={{ textAlign: "center" }}>{sent_profiles}</Table.Td>
      <Table.Td style={{ textAlign: "center" }}>{excluded_profiles}</Table.Td>
      <Table.Td>
        <div className="flex justify-center items-center gap-2">
          <RingProgress
            size={60}
            thickness={5}
            roundCaps
            sections={[
              { value: accepted_rate, color: "blue" },
              { value: 100 - accepted_rate, color: "#313a49" },
            ]}
            label={
              <Text c="white" weight={700} align="center" size="xs">
                {accepted_rate}%
              </Text>
            }
          />
          {accepted_profiles}
        </div>
      </Table.Td>
      <Table.Td>
        <div className="flex justify-center items-center gap-2">
          <RingProgress
            size={60}
            thickness={5}
            roundCaps
            sections={[
              { value: replied_rate, color: "blue" },
              { value: 100 - replied_rate, color: "#313a49" },
            ]}
            label={
              <Text c="white" weight={700} align="center" size="xs">
                {replied_rate}%
              </Text>
            }
          />
          {replied_profiles}
        </div>
      </Table.Td>
      <Table.Td>
        <div className="flex justify-center items-center">
          <RingProgress
            size={60}
            thickness={5}
            roundCaps
            sections={[
              { value: contact_shared_rate, color: "blue" },
              { value: 100 - contact_shared_rate, color: "#313a49" },
            ]}
            label={
              <Text c="white" weight={700} align="center" size="xs">
                {contact_shared_rate}%
              </Text>
            }
          />
          {contact_shared_profiles}
        </div>
      </Table.Td>
    </Table.Tr>
  );
};

export default PerformanceRow;
