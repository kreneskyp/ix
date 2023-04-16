import React from "react";
import SliderInput from "components/SliderInput";
import {
  Box,
  Flex,
  FormLabel,
  Input,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
} from "@chakra-ui/react";

export const OpenAIAgentConfigForm = ({ agent, setAgentData }) => {
  const config = agent.config;
  const handleChange = (value) => {
    setAgentData({
      ...agent,
      config: { ...config, temperature: parseFloat(value) },
    });
  };

  return (
    <>
      <FormLabel>Temperature</FormLabel>
      <Flex alignItems="center" justifyContent="space-between">
        <Slider
          aria-label="slider"
          min={0}
          max={1}
          step={0.05}
          value={config?.temperature || 0}
          onChange={handleChange}
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb />
        </Slider>
        <Box width="100px" marginLeft="1rem">
          <Input
            type="number"
            value={config?.temperature || 0}
            onChange={handleChange}
          />
        </Box>
      </Flex>
    </>
  );
};
