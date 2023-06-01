import React, {
  useMemo,
  useCallback,
  useRef,
  useEffect,
  useState,
} from "react";
import { Editor, Transforms, Range, createEditor } from "slate";
import { withHistory } from "slate-history";
import {
  Slate,
  Editable,
  withReact,
  useSelected,
  useFocused,
} from "slate-react";
import {
  Box,
  Popover,
  PopoverAnchor,
  PopoverBody,
  PopoverContent,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { MentionSearchResults } from "chat/input/MentionSearchResults";
import { ArtifactSearchResults } from "chat/input/ArtifactSearchResults";
import { usePreloadedQuery, useQueryLoader } from "react-relay/hooks";
import { SearchAgentsQuery } from "chat/graphql/SearchAgentsQuery";
import { SearchArtifactsQuery } from "chat/graphql/SearchArtifactsQuery";
import { useSendInput } from "chat/graphql/useSendInput";
import { clear_editor, INITIAL_EDITOR_CONTENT } from "utils/slate";
import { useChatColorMode } from "chains/editor/useColorMode";

const SearchAgentsQueryRunner = ({ queryRef, setResults }) => {
  // load query and then update state
  const data = usePreloadedQuery(SearchAgentsQuery, queryRef);
  const agents = data?.searchAgents;
  useEffect(() => {
    setResults(agents);
  }, [queryRef, agents]);
};

const SearchArtifactsQueryRunner = ({ queryRef, setResults }) => {
  // load query and then update state
  const data = usePreloadedQuery(SearchArtifactsQuery, queryRef);
  const artifacts = data?.searchArtifacts;
  useEffect(() => {
    setResults(artifacts);
  }, [queryRef, artifacts]);
};

export const ChatInput = ({ chat }) => {
  const focusRef = useRef();
  const [target, setTarget] = useState(null);
  const [targetType, setTargetType] = useState();
  const [index, setIndex] = useState(0);
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const renderElement = useCallback((props) => <Element {...props} />, []);
  const renderLeaf = useCallback((props) => <Leaf {...props} />, []);
  const editor = useMemo(
    () => withHighlights(withReact(withHistory(createEditor()))),
    []
  );

  // queries
  const [agentsQueryRef, loadAgentsQuery, disposeAgentsQuery] =
    useQueryLoader(SearchAgentsQuery);
  const searchAgents = useCallback((search) => {
    loadAgentsQuery({ search, chatId: chat.id }, { fetchPolicy: "store-and-network" });
  }, []);

  const [artifactQueryRef, loadArtifactQuery, disposeArtifactQuery] =
    useQueryLoader(SearchArtifactsQuery);
  const searchArtifacts = useCallback((search) => {
    loadArtifactQuery({ search, chatId: chat.id }, { fetchPolicy: "store-and-network" });
  }, []);

  useEffect(() => {
    if (target) {
      if (targetType === "mention") {
        searchAgents(search);
      } else if (targetType === "artifact") {
        searchArtifacts(search);
      }
    }
  }, [search]);

  const { sendInput, error, loading } = useSendInput(chat.id);

  const handleSendInput = async () => {
    // don't send empty input
    const input = serialize(editor.children);
    if (input === "") {
      return;
    }

    // send input and then clear the input
    await sendInput(input);
    clear_editor(editor);
  };

  // key press handler attached to editor
  const onKeyDown = useCallback(
    (event) => {
      if (target && results.length > 0) {
        switch (event.key) {
          case "ArrowDown":
            event.preventDefault();
            const prevIndex = index >= results.length - 1 ? 0 : index + 1;
            setIndex(prevIndex);
            break;
          case "ArrowUp":
            event.preventDefault();
            const nextIndex = index <= 0 ? results.length - 1 : index - 1;
            setIndex(nextIndex);
            break;
          case "Tab":
          case "Enter":
            event.preventDefault();
            Transforms.select(editor, target);
            insertHighlight(targetType, editor, results[index]);
            setTarget(null);
            break;
          case "Escape":
            event.preventDefault();
            setTarget(null);
            break;
        }
      } else if (!event.shiftKey) {
        // process enter key when shift is not pressed
        // and search popover is not open
        switch (event.key) {
          case "Enter":
            event.preventDefault();
            handleSendInput();
            break;
        }
      }
    },
    [results, editor, index, target]
  );

  // handler for editor changes
  const onChange = useCallback((newValue) => {
    const searchForHighlight = (editor, type, pattern) => {
      const { selection } = editor;

      if (selection && Range.isCollapsed(selection)) {
        // before
        const [start] = Range.edges(selection);
        const wordBefore = Editor.before(editor, start, { unit: "word" });
        const before = wordBefore && Editor.before(editor, wordBefore);
        const beforeRange = before && Editor.range(editor, before, start);
        const beforeText = beforeRange && Editor.string(editor, beforeRange);

        // match
        const beforeMatch = beforeText && beforeText.match(pattern);

        // after
        const after = Editor.after(editor, start);
        const afterRange = Editor.range(editor, start, after);
        const afterText = Editor.string(editor, afterRange);
        const afterMatch = afterText.match(/^(\s|$)/);

        if (beforeMatch && afterMatch) {
          setTarget(beforeRange);
          setTargetType(type);
          setSearch(beforeMatch[1]);
          setIndex(0);
          return true;
        }
      }
      return false;
    };

    // search text for agent mentions
    if (searchForHighlight(editor, "mention", /^@(\w+)$/)) {
      return;
    }

    // search text for artifact mentions
    if (searchForHighlight(editor, "artifact", /^{(\w+)$/)) {
      return;
    }

    // no target was found after update, clear target.
    if (target !== null) {
      setTarget(null);
    }
  });

  const onClose = useCallback(() => {
    // clear query refs
    if (agentsQueryRef !== null) {
      disposeAgentsQuery();
    }
    if (artifactQueryRef !== null) {
      disposeArtifactQuery();
    }
  });

  // Search results popover content
  const isOpen = target && results.length > 0;
  let searchComponent = null;
  if (isOpen) {
    if (targetType === "mention") {
      searchComponent = (
        <MentionSearchResults
          search={search}
          results={results}
          selected={index}
        />
      );
    } else if (targetType === "artifact") {
      searchComponent = (
        <ArtifactSearchResults
          search={search}
          results={results}
          selected={index}
        />
      );
    }
  }

  // Couldn't determine a good pattern for using relay to fetch
  // search updates for the autocomplete. The results are needed
  // here to decide whether to render the popover or not.
  //
  // QueryRunner components render empty but will fetch the query
  // data then update the results state. This is a huge hack but
  // it works for now.
  const agentSearchRunner = agentsQueryRef !== null && (
    <SearchAgentsQueryRunner
      queryRef={agentsQueryRef}
      setResults={setResults}
    />
  );

  const artifactSearchRunner = artifactQueryRef !== null && (
    <SearchArtifactsQueryRunner
      queryRef={artifactQueryRef}
      setResults={setResults}
    />
  );

  const sx = useColorModeValue(
    { bg: "gray.100", color: "gray.900", borderColor: "gray.300" },
    { bg: "gray.900", color: "gray.100", borderColor: "gray.700" }
  );

  const popoverSx = useColorModeValue(
    { bg: "gray.100", color: "gray.900", borderColor: "gray.300" },
    { bg: "gray.800", color: "gray.100", borderColor: "gray.700" }
  );

  return (
    <Box width={800} sx={sx} p={2} border="1px solid" borderRadius={5} maxH="400px"  overflowY="auto">
      {agentSearchRunner}
      {artifactSearchRunner}
      <Popover
        isOpen={isOpen}
        onClose={onClose}
        placement="top-start"
        initialFocusRef={focusRef}
      >
        <PopoverAnchor>
          <Box ref={focusRef} width={1}></Box>
        </PopoverAnchor>
        <PopoverContent mb={2} boxShadow="xl">
          <PopoverBody border="1px solid" sx={popoverSx}>
            {searchComponent}
          </PopoverBody>
        </PopoverContent>
      </Popover>

      <Slate
        editor={editor}
        value={INITIAL_EDITOR_CONTENT}
        onChange={onChange}
        width={800}
      >
        <Editable
          renderElement={renderElement}
          renderLeaf={renderLeaf}
          onKeyDown={onKeyDown}
          placeholder="Enter some text..."
          width={800}
        />
      </Slate>
    </Box>
  );
};

const serialize = (paragraphs) => {
  // serialize editor content to string.
  const serialized = paragraphs
    // Return the string content of each paragraph in the value's children.
    .map((paragraph) =>
      paragraph.children
        .map((child) => {
          // format nodes based on type
          if (child.type === "mention") {
            return `@${child.display}`;
          } else if (child.type === "artifact") {
            return `{${child.display}}`;
          } else {
            return child.text;
          }
        })
        .join("")
    )
    // Join them all with line breaks denoting paragraphs.
    .join("\n");
  return serialized;
};

const withHighlights = (editor) => {
  const { isInline, isVoid, markableVoid } = editor;

  const isHighlight = (element) =>
    element.type === "mention" || element.type === "artifact";

  editor.isInline = (element) => {
    return isHighlight(element) ? true : isInline(element);
  };

  editor.isVoid = (element) => {
    return isHighlight(element) ? true : isVoid(element);
  };

  editor.markableVoid = (element) => {
    return isHighlight(element) || markableVoid(element);
  };

  return editor;
};

const insertHighlight = (type, editor, object) => {
  // generate a highlight node and insert it into the editor
  const highlight = {
    type,
    display: type === "mention" ? object.alias : object.key,
    children: [{ text: "" }],
  };
  Transforms.insertNodes(editor, highlight);
  Transforms.move(editor);
};

const Leaf = ({ attributes, children, leaf }) => {
  if (leaf.bold) {
    children = <strong>{children}</strong>;
  }

  if (leaf.code) {
    children = <code>{children}</code>;
  }

  if (leaf.italic) {
    children = <em>{children}</em>;
  }

  if (leaf.underline) {
    children = <u>{children}</u>;
  }

  return <span {...attributes}>{children}</span>;
};

const Element = (props) => {
  const { attributes, children, element } = props;
  switch (element.type) {
    case "mention":
      return <Mention {...props} />;
    case "artifact":
      return <Artifact {...props} />;
    default:
      return <p {...attributes}>{children}</p>;
  }
};

const Mention = ({ attributes, children, element }) => {
  const selected = useSelected();
  const focused = useFocused();

  const { mention } = useChatColorMode();
  const bg =
    selected && focused
      ? useColorModeValue("gray.200", "gray.700")
      : "transparent";

  return (
    <Text
      as="span"
      {...attributes}
      borderRadius={3}
      contentEditable={false}
      bg={bg}
      sx={mention}
    >
      @{element.display}
      {children}
    </Text>
  );
};

const Artifact = ({ attributes, children, element }) => {
  const selected = useSelected();
  const focused = useFocused();
  const { artifact, editorHighlight } = useChatColorMode();
  const bg = selected && focused ? editorHighlight : "transparent";

  return (
    <Text
      as="span"
      {...attributes}
      borderRadius={3}
      contentEditable={false}
      bg={bg}
      sx={artifact}
    >
      &#123; {element.display} &#125;
      {children}
    </Text>
  );
};

export default ChatInput;
