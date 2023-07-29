import React from "react";
import HighlightText from "components/HighlightText";
import { useStreamContent } from "chat/graphql/useChatMessageTokenSubscription";

const AssistantContent = ({ message }) => {
  // Use stream content when in streaming mode
  // otherwise use the text content.
  //
  // Render empty string when stream content is unavailable. Stream content may
  // not have been received yet or may have been lost to a refresh.
  // the complete message will be received when the message is complete.
  const isStream = message.content.stream || false;
  const stream = useStreamContent(message.id);
  const content = isStream ? stream || "" : message.content.text;
  return <HighlightText content={content} />;
};

export default AssistantContent;
