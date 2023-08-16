import { Box, List, ListItem, Text } from "@chakra-ui/react";
import React from "react";

export const APIErrorList = ({ error }) => {
  const extractErrors = (axiosError) => {
    return axiosError.response.data.detail
      .map((error) => {
        if (error.loc && error.msg) {
          let field = error.loc[1];
          return `'${field}' field is ${error.msg}.`;
        }
        return null;
      })
      .filter((message) => message); // Filter out any null values
  };

  const errorMessages = extractErrors(error);

  return (
    <Box>
      <Text mb={2}>Failed to save the agent due to the following errors:</Text>
      <List spacing={1}>
        {errorMessages.map((msg, index) => (
          <ListItem key={index}>- {msg}</ListItem>
        ))}
      </List>
    </Box>
  );
};
