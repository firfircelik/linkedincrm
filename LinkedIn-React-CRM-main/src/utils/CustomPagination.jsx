import React from 'react';
import { Pagination } from '@mantine/core';

const CustomPagination = ({ currentPage, setCurrentPage, totalPages, data, error }) => {
  return (
    <Pagination
      value={currentPage}
      onChange={setCurrentPage}
      total={totalPages}
      radius="md"
      style={{
        display: data.length > 0 && !error ? "flex" : "none",
        justifyContent: "end",
        padding: "20px",
      }}
      styles={{
        control: {
          color:'#a0aec0',
          backgroundColor: 'transparent',
          border: 'none'
        },
        dots: {
          color: 'white',
        },
      }}
    />
  );
};

export default CustomPagination;
