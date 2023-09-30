import React from "react";
import { Text } from "@chakra-ui/react";
import { PlanContent } from "planner/PlanContent";
import { ArtifactListContent } from "chat/messages/ArtifactListContent";
import { ArtifactFileContent } from "chat/messages/ArtifactFileContent";

export const ArtifactContent = ({ message }) => {
  let contentComponent;
  const content = message.content;
  switch (content.artifact_type) {
    case "PLAN":
      contentComponent = <PlanContent message={message} />;
      break;
    case "artifact_list":
    case "file_list":
      contentComponent = <ArtifactListContent message={message} />;
      break;
    case "file":
      contentComponent = <ArtifactFileContent message={message} />;
      break;
    default:
      contentComponent = <Text>{message.content.artifact_type}</Text>;
      break;
  }
  return contentComponent;
};
