import React, { useCallback, useRef, useEffect } from "react";
import { Transforms } from "slate";
import { Slate, Editable } from "slate-react";
import {
  Box,
  Popover,
  PopoverAnchor,
  PopoverBody,
  PopoverContent,
} from "@chakra-ui/react";
import { MentionSearchResults } from "chat/input/MentionSearchResults";
import { ArtifactSearchResults } from "chat/input/ArtifactSearchResults";
import { INITIAL_EDITOR_CONTENT } from "utils/slate";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useChatStyle } from "chat/ChatInterface";
import { FileDropZone } from "components/FileDropZone";
import { ChatInputContext } from "chat/input/ChatInputContext";
import { useSendInput } from "chat/input/useSendInput";

export const ChatInput = ({ chat }) => {
  const focusRef = useRef();
  const chatStyle = useChatStyle();
  const { editor, config, autoComplete, renderProps } =
    React.useContext(ChatInputContext);
  const { sendInput } = useSendInput(chat, editor, config.highlights);

  const { load: loadAgents, page: agentPage } = usePaginatedAPI(`/api/agents/`);
  const { load: loadArtifacts, page: artifactPage } =
    usePaginatedAPI(`/api/artifacts/`);
  const hasAgents =
    autoComplete.type === "mention" &&
    agentPage &&
    agentPage.objects.length > 0;
  const hasArtifacts =
    autoComplete.type === "artifact" &&
    artifactPage &&
    artifactPage.objects.length > 0;
  const results = hasAgents
    ? agentPage.objects
    : hasArtifacts
    ? artifactPage.objects
    : [];

  const searchAgents = useCallback((search) => {
    loadAgents({ search, chat_id: chat.id });
  }, []);

  const searchArtifacts = useCallback((search) => {
    loadArtifacts({ search, chat_id: chat.id });
  }, []);

  useEffect(() => {
    if (autoComplete.target) {
      if (autoComplete.type === "mention") {
        searchAgents(autoComplete.search);
      } else if (autoComplete.type === "artifact") {
        searchArtifacts(autoComplete.search);
      }
    }
  }, [autoComplete.search]);

  // key press handler attached to editor
  const onKeyDown = useCallback(
    (event) => {
      if (autoComplete.target && results.length > 0) {
        switch (event.key) {
          case "ArrowDown":
            event.preventDefault();
            const prevIndex =
              autoComplete.selected >= results.length - 1
                ? 0
                : autoComplete.selected + 1;
            autoComplete.setSelected(prevIndex);
            break;
          case "ArrowUp":
            event.preventDefault();
            const nextIndex =
              autoComplete.selected <= 0
                ? results.length - 1
                : autoComplete.selected - 1;
            autoComplete.setSelected(nextIndex);
            break;
          case "Tab":
          case "Enter":
            event.preventDefault();
            Transforms.select(editor, autoComplete.target);
            insertHighlight(
              autoComplete.type,
              editor,
              results[autoComplete.selected]
            );
            autoComplete.setTarget(null);
            break;
          case "Escape":
            event.preventDefault();
            autoComplete.setTarget(null);
            break;
        }
      } else if (!event.shiftKey) {
        // process enter key when shift is not pressed
        // and search popover is not open
        switch (event.key) {
          case "Enter":
            event.preventDefault();
            sendInput();
            break;
        }
      }
    },
    [results, editor, autoComplete.selected, autoComplete.target, chat.id]
  );

  // Search results popover content
  const isOpen = autoComplete.target && (hasAgents || hasArtifacts);
  let searchComponent = null;
  if (isOpen) {
    if (autoComplete.type === "mention") {
      searchComponent = (
        <MentionSearchResults
          search={autoComplete.search}
          results={results}
          selected={autoComplete.selected}
        />
      );
    } else if (autoComplete.type === "artifact") {
      searchComponent = (
        <ArtifactSearchResults
          search={autoComplete.search}
          results={results}
          selected={autoComplete.selected}
        />
      );
    }
  }

  return (
    <Box
      border="1px solid"
      borderRadius={5}
      maxH="400px"
      overflowY="auto"
      {...chatStyle.input}
    >
      <FileDropZone task_id={chat?.task_id}>
        <Box p={2}>
          <Popover
            isOpen={isOpen}
            placement="top-start"
            initialFocusRef={focusRef}
          >
            <PopoverAnchor>
              <Box ref={focusRef} width={1}></Box>
            </PopoverAnchor>
            <PopoverContent mb={2} boxShadow="xl">
              <PopoverBody border="1px solid" {...chatStyle.autocomplete}>
                {searchComponent}
              </PopoverBody>
            </PopoverContent>
          </Popover>

          <Slate
            editor={editor}
            value={INITIAL_EDITOR_CONTENT}
            onChange={autoComplete.handleChange}
            width={chatStyle.input.width}
          >
            <Editable
              {...renderProps}
              onKeyDown={onKeyDown}
              placeholder="Enter text or drop a file..."
              width={chatStyle.input.width}
            />
          </Slate>
        </Box>
      </FileDropZone>
    </Box>
  );
};

ChatInput.defaultProps = {
  width: 800,
};

const insertHighlight = (type, editor, object) => {
  // generate a highlight node and insert it into the editor
  const highlight = {
    type,
    display: type === "mention" ? object.alias : object.key,
    children: [{ text: "" }],
    object
  };
  Transforms.insertNodes(editor, highlight);
  Transforms.move(editor);
};

export default ChatInput;
