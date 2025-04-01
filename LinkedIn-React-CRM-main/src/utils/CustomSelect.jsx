import { Select } from '@mantine/core';
import React from 'react';

const CustomSelect = ({ placeholder, data, onChange, value, statusColors }) => {
  return (
    <Select
            variant="filled"
            size="md"
            radius="md"
            placeholder={placeholder}
            data={data}
            onChange={onChange}
            value={value}
            allowDeselect={false}
            classNames={{
              option: 'mantine-select-option'
            }}
            styles={{
              input: {
                backgroundColor: "#323B49",
                color:"white",
              },
              dropdown: {
                color: "white",
                backgroundColor: "#323B49",
              }
            }}
          />
  );
};

export default CustomSelect;
