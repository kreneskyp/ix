import React from "react";
import { components } from "react-select";
import { FormHelperText, Text, VStack } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getOptionStyle } from "chains/editor/NodeSelector";

const getStyle = (style, isDisabled, isFocused, isSelected) => {
  if (isDisabled) {
    return style.disabled;
  }
  if (isFocused) {
    return style.hover;
  }
  if (isSelected) {
    return style.selected;
  }
  return style.default;
};

export const OptionHelp = ({ data }) => {
  return (
    <FormHelperText
      fontSize={"xs"}
      m={0}
      minHeight={"100%"}
      maxHeight={75}
      overflow="hidden"
      textOverflow="ellipsis"
      css={{
        display: "-webkit-box",
        WebkitBoxOrient: "vertical",
        WebkitLineClamp: 3,
      }}
    >
      {data.help}
    </FormHelperText>
  );
};

export const OptionContent = ({ data, isDisabled, isFocused, isSelected }) => {
  const { isLight } = useEditorColorMode();
  const baseStyle = getOptionStyle(isLight);
  const style = getStyle(baseStyle, isDisabled, isFocused, isSelected);

  return (
    <VStack
      spacing={0}
      p={2}
      alignItems={"start"}
      width={"100%"}
      height={"100%"}
      borderRadius={5}
      transition={"bg 0.5s ease-in"}
      {...style}
    >
      <Text fontSize={"sm"} fontWeight={"bold"} m={0}>
        {data.label}
      </Text>
      <OptionHelp data={data} {...style.help} />
    </VStack>
  );
};

export const Option = ({
  data,
  isDisabled,
  isFocused,
  isSelected,
  ...props
}) => {
  return (
    <components.Option {...props}>
      <OptionContent
        data={data}
        isFocused={isFocused}
        isDisabled={isDisabled}
        isSelected={isSelected}
      />
    </components.Option>
  );
};
