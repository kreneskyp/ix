import React, from "react";
import {
  Flex,
  FormLabel,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Text,
  VStack,
} from "@chakra-ui/react";

export const SliderInput = ({
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
      min={min}
      max={max}
      step={step}
      value={value || 0}
      onChange={onChange}
    >
      <SliderTrack>
        <SliderFilledTrack />
      </SliderTrack>
      <SliderThumb />
    </Slider>
  </VStack>
);

export default SliderInput;
