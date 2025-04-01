import React from 'react';
import { Text } from '@mantine/core';

export default () => {
  return  (
    <header className="flex items-center bg-[#1f2937] w-full h-24 px-12">
      <Text
        component="p"
        style={{
          fontSize: 24,
          fontWeight: 700,
          lineHeight: '31.2px',
          textAlign: 'left',
          color: 'white',
        }}
      >
        Campaigns Overview
      </Text>
    </header>
  );
};
