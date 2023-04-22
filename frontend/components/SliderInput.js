import React, { useState } from "react";
import {
  Box,
  Flex,
  Input,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
} from "@chakra-ui/react";

const SliderInput = ({ min, max, defaultValue, onChange }) => {
  const [value, setValue] = useState(defaultValue);

  const handleChange = (newValue) => {
    setValue(newValue);
    onChange(newValue);
  };

  return (
    <Flex alignItems="center" justifyContent="space-between">
      <Slider
        aria-label="slider"
        min={min}
        max={max}
        value={value}
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
          value={value}
          min={min}
          max={max}
          onChange={(e) => handleChange(e.target.value)}
        />
      </Box>
    </Flex>
  );
};

export default SliderInput;
