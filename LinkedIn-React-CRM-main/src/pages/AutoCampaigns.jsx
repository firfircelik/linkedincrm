import { Tabs, Text } from "@mantine/core";
import LeadPanel from "../components/AutoCampaigns/LeadPanel";
import ScrapPanel from "../components/AutoCampaigns/ScrapPanel";

export default () => {
  return (
    <div className="bg-[#1f2937] my-5 mx-8 rounded-lg min-h-screen">
      <div className="flex p-5 justify-between gap-32">
        <Tabs
          color="#0057e9"
          variant="pills"
          defaultValue="lead"
          className="w-full space-y-5"
          classNames={{
            tab: "mantine-tab-option",
          }}
          styles={{
            tab: {
              color: "white",
              borderWidth: "1px",
              borderColor: "#313a49",
              borderStyle: "solid",
            },
          }}
        >
          <Tabs.List>
            <div className="flex flex-col gap-5">
              <Text c="#718096">Campaign Type</Text>
              <div className="flex gap-5">
                <Tabs.Tab value="lead">Lead Generation</Tabs.Tab>
                <Tabs.Tab value="scrap">Scraper</Tabs.Tab>
              </div>
            </div>
          </Tabs.List>

          <Tabs.Panel value="lead" className="space-y-5">
            <LeadPanel />
          </Tabs.Panel>
          <Tabs.Panel value="scrap" className="space-y-5">
            <ScrapPanel />
          </Tabs.Panel>
        </Tabs>
      </div>
    </div>
  );
};
