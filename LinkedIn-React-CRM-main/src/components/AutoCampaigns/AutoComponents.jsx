import {
  TextInput,
  RangeSlider,
  Text,
  Group,
  Button,
  List,
  FileButton,
  NumberInput,
  Select,
} from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";
import { FaCalendar, FaUpload } from "react-icons/fa";

const InputComponent = ({ label, placeholder, className, onChange }) => (
  <TextInput
    label={label}
    placeholder={placeholder}
    className={className}
    onChange={onChange}
    styles={{
      input: {
        color: "white",
        backgroundColor: "transparent",
        borderWidth: "1px",
        borderColor: "#313a49",
        borderStyle: "solid",
        "::placeholder": {
          color: "white",
        },
      },
      label: {
        color: "#718096",
      },
    }}
  />
);

const NumberInputComponent = ({ label, placeholder, className, onChange }) => (
  <NumberInput
    label={label}
    placeholder={placeholder}
    className={className}
    onChange={onChange}
    min={1}
    classNames={{
      control: 'mantine-control-number'
    }}
    styles={{
      input: {
        color: "white",
        backgroundColor: "transparent",
        borderWidth: "1px",
        borderColor: "#313a49",
        borderStyle: "solid",
        "::placeholder": {
          color: "white",
        },
      },
      label: {
        color: "#718096",
      },
      control: {
        color: "white",
      },
    }}
  />
);

const DatePickerComponent = ({ label, placeholder, className, onChange }) => (
  <DatePickerInput
    type="range"
    label={label}
    placeholder={placeholder}
    rightSection={<FaCalendar />}
    allowDeselect={true}
    className={className}
    onChange={onChange}
    styles={{
      input: {
        color: "white",
        backgroundColor: "transparent",
        borderWidth: "1px",
        borderColor: "#313a49",
        borderStyle: "solid",
        "::placeholder": {
          color: "white",
        },
      },
      label: {
        color: "#718096",
      },
    }}
  />
);

const RangeSliderComponent = ({ title, color, marks, defaultValue, onChange }) => (
  <div className="flex flex-col w-full">
    <Text c="#718096" size="sm" mb={2}>
      {title}
    </Text>
    <RangeSlider
      color={color}
      minRange={1}
      min={1}
      max={1000}
      step={1}
      marks={marks}
      onChange={onChange}
      className="w-full"
      defaultValue={defaultValue}
      styles={{
        track: {
          backgroundColor: "#313a49",
        },
        thumb: {
          backgroundColor: "#1f2937",
          border: "2px solid #0057E9",
        },
        mark: {
          color: "white",
        },
      }}
    />
  </div>
);

const FileUploadComponent = ({ files, setFiles }) => (
  <div className="flex flex-col">
    <Group justify="start">
      <Text c="#718096" size="sm">
        Select List File
      </Text>
      <FileButton onChange={setFiles} multiple>
        {(props) => (
          <Button color="#0057E9" {...props}>
            <FaUpload />
          </Button>
        )}
      </FileButton>
    </Group>
    {files.length > 0 && (
      <Text c="#718096" size="sm" mt="sm">
        Picked files:
      </Text>
    )}
    <List c="#718096" size="sm" withPadding>
      {files.map((file, index) => (
        <List.Item key={index}>• {file.name}</List.Item>
      ))}
    </List>
  </div>
);

const SelectComponent = ({ label, placeholder, data, className, onChange }) => (
    <Select
      label={label}
      placeholder={placeholder}
      data={data}
      className={className}
      onChange={onChange}
      classNames={{
        option: 'mantine-select-option'
      }}
      styles={{
        input: {
          color: "white",
          backgroundColor: "transparent",
          borderWidth: "1px",
          borderColor: "#313a49",
          borderStyle: "solid",
        },
        label: {
          color: "#718096",
        },
        dropdown: {
          backgroundColor: "#1f2937",
          borderColor: "#313a49",
          color: "white",
        },
      }}
    />
  );

export {
  InputComponent,
  NumberInputComponent,
  DatePickerComponent,
  RangeSliderComponent,
  FileUploadComponent,
  SelectComponent
};
