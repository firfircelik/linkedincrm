import React, { useState } from "react";
import { Popover, Button, Group } from "@mantine/core";
import { DatePicker } from "@mantine/dates";
import { FaCalendarAlt } from "react-icons/fa";
import dayjs from "dayjs";

const CustomDatePicker = ({ onDateSelected }) => {
  const [selectedDate, setSelectedDate] = useState([null, null]);
  const [isDatePickerOpen, setDatePickerOpen] = useState(false);

  const handleDateChange = (dates) => {
    setSelectedDate(dates);
    if (dates[0] && dates[1]) {
      onDateSelected(dates);
      setDatePickerOpen(false); 
    }
  };

  const handleToday = () => {
    const today = new Date();
    handleDateChange([today, today]);
  };

  const handleYesterday = () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    handleDateChange([yesterday, yesterday]);
  };

  const handleThisWeek = () => {
    const startOfWeek = dayjs().startOf("week").toDate();
    const endOfWeek = dayjs().endOf("week").toDate();
    handleDateChange([startOfWeek, endOfWeek]);
  };

  const handleLastWeek = () => {
    const startOfLastWeek = dayjs()
      .subtract(1, "week")
      .startOf("week")
      .toDate();
    const endOfLastWeek = dayjs().subtract(1, "week").endOf("week").toDate();
    handleDateChange([startOfLastWeek, endOfLastWeek]);
  };

  const handleThisMonth = () => {
    const startOfMonth = dayjs().startOf("month").toDate();
    const endOfMonth = dayjs().endOf("month").toDate();
    handleDateChange([startOfMonth, endOfMonth]);
  };

  const handleLastMonth = () => {
    const startOfLastMonth = dayjs()
      .subtract(1, "month")
      .startOf("month")
      .toDate();
    const endOfLastMonth = dayjs().subtract(1, "month").endOf("month").toDate();
    handleDateChange([startOfLastMonth, endOfLastMonth]);
  };

  const handleThisYear = () => {
    const startOfYear = dayjs().startOf("year").toDate();
    const endOfYear = dayjs().endOf("year").toDate();
    handleDateChange([startOfYear, endOfYear]);
  };

  const handleLastYear = () => {
    const startOfLastYear = dayjs()
      .subtract(1, "year")
      .startOf("year")
      .toDate();
    const endOfLastYear = dayjs().subtract(1, "year").endOf("year").toDate();
    handleDateChange([startOfLastYear, endOfLastYear]);
  };

  const handleCustomRange = (dates) => {
    handleDateChange(dates); // directly use the dates selected from DatePicker
  };

  return (
    <Popover
      opened={isDatePickerOpen}
      onClose={() => setDatePickerOpen(false)}
      position="bottom"
      transition="pop"
    >
      <Popover.Target>
        <Button
          variant="filled"
          size="md"
          radius="md"
          color="#323B49"
          onClick={() => setDatePickerOpen((o) => !o)}
          rightSection={<FaCalendarAlt />}
        >
          Pick Date
        </Button>
      </Popover.Target>
      <Popover.Dropdown>
        <div className="flex gap-2">
          <div className="flex flex-col gap-2">
            <Button variant="default" onClick={handleToday}>
              Today
            </Button>
            <Button variant="default" onClick={handleYesterday}>
              Yesterday
            </Button>
            <Button variant="default" onClick={handleThisWeek}>
              This Week
            </Button>
            <Button variant="default" onClick={handleLastWeek}>
              Last Week
            </Button>
            <Button variant="default" onClick={handleThisMonth}>
              This Month
            </Button>
            <Button variant="default" onClick={handleLastMonth}>
              Last Month
            </Button>
            <Button variant="default" onClick={handleThisYear}>
              This Year
            </Button>
            <Button variant="default" onClick={handleLastYear}>
              Last Year
            </Button>
          </div>
          <DatePicker
            type="range"
            // allowSingleDateInRange
            allowDeselect
            value={selectedDate}
            onChange={handleDateChange}
          />
        </div>
      </Popover.Dropdown>
    </Popover>
  );
};

export default CustomDatePicker;
