import React from "react";

import {
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  useDisclosure,
} from "@chakra-ui/react";
import {
  faEllipsis,
  faExternalLinkAlt,
  faTrash,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { EditorViewState, NodeStateContext } from "chains/editor/contexts";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { Overlay } from "components/Overlay";
import { WithPortal } from "components/WithPortal";

const CHAIN_REFERENCE = "ix.runnable.flow.load_chain_id";

const DeleteItem = ({ node }) => {
  const api = React.useContext(ChainEditorAPIContext);
  const nodeState = React.useContext(NodeStateContext);
  const style = useEditorColorMode();

  const onClick = React.useCallback(
    (event) => {
      api.deleteNode(node.id);
      nodeState.deleteNode(node.id);
    },
    [node.id, api]
  );

  return (
    <MenuItem
      {...style.node_menu}
      onClick={onClick}
      display={"flex"}
      justifyContent={"space-between"}
    >
      Delete <FontAwesomeIcon icon={faTrash} style={{ marginLeft: "3px" }} />
    </MenuItem>
  );
};

export const NodeMenu = ({ node }) => {
  const editor = React.useContext(EditorViewState);
  const isReference = node.class_path === CHAIN_REFERENCE;
  const style = useEditorColorMode();
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <>
      {/* Hidden overlay for breakout to work with React Flow. */}
      {isOpen && <Overlay isOpen={isOpen} onClick={onClose} />}

      <Menu isOpen={isOpen} onClose={onClose} width={"100px"}>
        <MenuButton
          as={IconButton}
          icon={<FontAwesomeIcon icon={faEllipsis} />}
          variant="ghost"
          colorScheme="whiteAlpha"
          color="gray.300"
          p={0}
          m={0}
          size="xs"
          onClick={onOpen}
          _hover={{
            bg: "blackAlpha.500",
            color: "white",
            border: "none",
            p: 0,
            m: 0,
          }}
          _expanded={{
            bg: "blackAlpha.500",
            color: "white",
          }}
          _focus={{ boxShadow: "none" }}
        />
        {/* MenuList renders in portal to place it above the Overlay. */}
        <WithPortal>
          <MenuList zIndex={10000}>
            <DeleteItem node={node} />
            {isReference && (
              <MenuItem
                onClick={() => {
                  editor.selectOrOpenChain(node.config.chain_id);
                }}
                {...style.node_menu}
                display={"flex"}
                justifyContent={"space-between"}
                zIndex={20}
              >
                Open{" "}
                <FontAwesomeIcon
                  icon={faExternalLinkAlt}
                  style={{ marginLeft: "3px" }}
                />
              </MenuItem>
            )}
          </MenuList>
        </WithPortal>
      </Menu>
    </>
  );
};

export default NodeMenu;
