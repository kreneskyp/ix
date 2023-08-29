import axios from "axios";
import React, { useState } from "react";
import {
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  AlertDialog,
  AlertDialogOverlay,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogBody,
  AlertDialogFooter,
  Button,
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { Pagination } from "components/Pagination";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash } from "@fortawesome/free-solid-svg-icons";

export const ChatTable = ({ page, load }) => {
  const { count, has_next, has_previous, objects, pages, page_number } = page;
  const chats = objects;

  const [isOpen, setIsOpen] = useState(false);
  const [selectedChat, setSelectedChat] = useState(null);

  const onClose = () => setIsOpen(false);
  const onDelete = async () => {
    try {
      await axios.delete(`/api/chats/${selectedChat.id}`);
      load(page_number - 1); // Refresh the chat list after delete
      setIsOpen(false); // Close the dialog
    } catch (error) {
      console.error("Failed to delete chat:", error);
      setIsOpen(false); // Close the dialog
    }
  };

  return (
    <div>
      <Table colorScheme="gray" mb={10}>
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Created At</Th>
            <Th>Agents</Th>
          </Tr>
        </Thead>
        <Tbody>
          {chats?.map((chat) => {
            const { id, name } = chat;
            const chatLink = `/chat/${id}`;
            const createdAt = new Date(chat.created_at).toLocaleString();
            return (
              <Tr key={id}>
                <Td>
                  <Link to={chatLink}>
                    {name || createdAt} ({id})
                  </Link>
                </Td>
                <Td>{createdAt}</Td>
                <Td>
                  {chat.agents?.map((agent) => (
                    <span key={agent.alias}>{agent.alias} </span>
                  ))}
                </Td>
                <Td>
                  <Button
                    onClick={() => {
                      setSelectedChat(chat);
                      setIsOpen(true);
                    }}
                  >
                    <FontAwesomeIcon icon={faTrash} />
                  </Button>
                </Td>
              </Tr>
            );
          })}
        </Tbody>
      </Table>
      <Pagination
        hasNext={has_next}
        hasPrevious={has_previous}
        load={load}
        pages={pages}
        pageNumber={page_number}
      />

      <AlertDialog isOpen={isOpen} onClose={onClose}>
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Chat
            </AlertDialogHeader>

            <AlertDialogBody>
              <Text>{selectedChat?.name || selectedChat?.id}</Text>
              <Text mt={10}>
                Are you sure you want to delete this chat? This action cannot be
                undone.
              </Text>
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button onClick={onClose}>Cancel</Button>
              <Button colorScheme="red" onClick={onDelete} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </div>
  );
};
