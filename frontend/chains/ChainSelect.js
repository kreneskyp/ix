import React from "react";
import axios from "axios";
import { AsyncAPIObjectSelect } from "components/AsyncAPIObjectSelect";

const getOptions = async (inputValue) => {
  const response = await axios.get(
    `/api/chains/?is_agent=false&limit=20&search=${inputValue}`
  );
  const data = response.data;
  const options = data?.objects.map((item) => ({
    label: item.name,
    value: item.id,
  }));
  return options;
};

const getDefaultOptions = async () => {
  try {
    const response = await axios.get(`/api/chains/?is_agent=false&limit=10`);
    const options = response.data.objects.map((item) => ({
      label: item.name,
      value: item.id,
    }));
    return options;
  } catch (error) {
    // Handle error here
    console.error("Error fetching default options:", error);
    return [];
  }
};

const getDetail = async (id) => {
  const response = await axios.get(`/api/chains/${id}`);
  return { label: response.data.name, value: response.data.id };
};

export const ChainSelect = ({ onChange, value, ...props }) => {
  return (
    <AsyncAPIObjectSelect
      getOptions={getOptions}
      getDefaultOptions={getDefaultOptions}
      getDetail={getDetail}
      onChange={onChange}
      value={value}
      {...props}
    />
  );
};
