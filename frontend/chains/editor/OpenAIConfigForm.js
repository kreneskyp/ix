import React from "react";
import {
  Flex,
  FormLabel,
  HStack,
  Select,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Text,
  VStack,
} from "@chakra-ui/react";

export const SliderInput = ({
  field,
  label,
  value,
  onChange,
  min = 0,
  max = 1,
  step = 0.5,
}) => (
  <VStack spacing={0} width="100%">
    <Flex
      alignItems="center"
      justifyContent="space-between"
      width="100%"
      height="100%"
    >
      <FormLabel>{label}</FormLabel>
      <Text>{value}</Text>
    </Flex>
    <Slider
      aria-label="slider"
      min={0}
      max={1}
      step={0.05}
      value={value || 0}
      onChange={(value) => onChange(field, value)}
    >
      <SliderTrack>
        <SliderFilledTrack />
      </SliderTrack>
      <SliderThumb />
    </Slider>
  </VStack>
);

export const OpenAIConfigForm = ({ options, config, setData }) => {
  const handleChange = (key, value) => {
    setData({
      ...config,
      [key]: parseFloat(value),
    });
  };

  return (
    <VStack spacing={2} width="100%">
      <HStack>
        <FormLabel>Model</FormLabel>
        <Select size="sm">
          {options.models.map((modelOptions) => (
            <option key={modelOptions.value} value={modelOptions.value}>
              {modelOptions.label}
            </option>
          ))}
        </Select>
      </HStack>
      <SliderInput
        label="Temperature"
        field="temperature"
        value={config?.temperature}
        onChange={handleChange}
      />
      <SliderInput
        label="Top P"
        field="top_p"
        value={config?.top_p}
        onChange={handleChange}
      />
      <SliderInput
        label="Frequency Penalty"
        field="frequency_penalty"
        value={config?.frequency_penalty}
        max={2}
        onChange={handleChange}
      />
      <SliderInput
        label="Presence Penalty"
        field="presence_penalty"
        value={config?.presence_penalty}
        max={2}
        onChange={handleChange}
      />
    </VStack>
  );
};
