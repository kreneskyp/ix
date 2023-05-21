import React from "react";
import HighlightText from "components/HighlightText";

const AssistantContent = ({ message }) => {
  return <HighlightText content={message.content.text} />;
};

export default AssistantContent;
