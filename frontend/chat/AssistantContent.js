import React from "react";
import MarkDown from "components/Markdown";

const AssistantContent = ({ message }) => {
  return <MarkDown content={message.content.text} />;
};

export default AssistantContent;
