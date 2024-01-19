import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFile, faGear } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";
import { Box } from "@chakra-ui/layout";
import { StackableIcon } from "icons/StackableIcon";
import { IndicatorIcon } from "icons/IndicatorIcon";

export const SchemaIcon = () => {
  const { colorMode } = useColorMode();
  const iconColor = colorMode === "light" ? "gray.200" : "black";

  return (
    <StackableIcon>
      <FontAwesomeIcon icon={faFile} />
      <IndicatorIcon indicatorSize={11}>
        <FontAwesomeIcon icon={faGear} />
      </IndicatorIcon>
    </StackableIcon>
  );
};

export default SchemaIcon;
