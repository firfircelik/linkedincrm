import { Progress, Switch, Table, RingProgress, Text } from "@mantine/core";

const CampaignRow = ({
  name,
  campaign_completion_percentage,
  total_profile_count,
  connects_sent,
  connects_sent_percentage,
  excluded_profiles,
  excluded_profiles_percentage,
  connect_accepted,
  connect_accepted_percentage,
  status,
  scrapped_profiles_percentage,
  scrapped_profiles, 
  autoscrapper
}) => {
  const isActive = status === "pending"

  return (
    <Table.Tr
      style={{
        borderColor: "#313a49",
        borderBottomWidth: "2px",
        borderTopWidth: "2px",
      }}
    >
      <Table.Td>
        {name}
        <Progress
          value={campaign_completion_percentage}
          style={{
            marginTop: "10px",
            marginBottom: "4px",
            backgroundColor: "#313a49",
          }}
          color="#0057E9"
        />
        <Text c="#0057E9" fw={700} ta="left" size="xs">
        {campaign_completion_percentage || 0}% 
        </Text>
      </Table.Td>
      <Table.Td style={{ textAlign: "center", opacity: autoscrapper ? 0.5 : 1 }}>{total_profile_count}</Table.Td>
      <Table.Td style={autoscrapper ? { opacity: 0.5 } : {}}>
        <div className="flex justify-center items-center gap-2">
          <RingProgress
            size={60}
            thickness={5}
            roundCaps
            sections={[
              { value: connects_sent_percentage, color: "#0057E9" },
              { value: 100 - connects_sent_percentage, color: "#313a49" },
            ]}
            label={
              <Text c="white" weight={700} align="center" size="xs">
                {connects_sent_percentage}%
              </Text>
            }
          />
          {connects_sent}
        </div>
      </Table.Td>
      <Table.Td style={autoscrapper ? { opacity: 0.5 } : {}}>
        <div className="flex justify-center items-center gap-2">
          <RingProgress
            size={60}
            thickness={5}
            roundCaps
            sections={[
              { value: excluded_profiles_percentage, color: "#0057E9" },
              { value: 100 - excluded_profiles_percentage, color: "#313a49" },
            ]}
            label={
              <Text c="white" weight={700} align="center" size="xs">
                {excluded_profiles_percentage}%
              </Text>
            }
          />
          {excluded_profiles}
        </div>
      </Table.Td>
      <Table.Td style={{ textAlign: "center", opacity: autoscrapper ? 0.5 : 1 }}>{connect_accepted}</Table.Td>
      <Table.Td style={autoscrapper ? { opacity: 0.5 } : {}}>
        <div className="flex justify-center items-center">
          <RingProgress
            size={60}
            thickness={5}
            roundCaps
            sections={[
              { value: connect_accepted_percentage, color: "#0057E9" },
              { value: 100 - connect_accepted_percentage, color: "#313a49" },
            ]}
            label={
              <Text c="white" weight={700} align="center" size="xs">
                {connect_accepted_percentage}%
              </Text>
            }
          />
        </div>
      </Table.Td>
      <Table.Td style={!autoscrapper ? { opacity: 0.5 } : {}}>
        <div className="flex justify-center items-center">
          <RingProgress
            size={60}
            thickness={5}
            roundCaps
            sections={[
              { value: scrapped_profiles_percentage, color: "#0057E9" },
              { value: 100 - scrapped_profiles_percentage, color: "#313a49" },
            ]}
            label={
              <Text c="white" weight={700} align="center" size="xs">
                {scrapped_profiles_percentage}%
              </Text>
            }
          />
          {scrapped_profiles}
        </div>
      </Table.Td>

      <Table.Td>
        <div className="flex justify-center items-center">
          <Switch
          color="#0057E9"
            checked={isActive}
            styles={{
              track: {
                backgroundColor: isActive ? undefined : "#313a49",
              },
            }}
          />
        </div>
      </Table.Td>
    </Table.Tr>
  );
};

export default CampaignRow;
