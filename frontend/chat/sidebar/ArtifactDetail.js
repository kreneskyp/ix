import React from "react";
import { Text, VStack, Grid, GridItem } from "@chakra-ui/react";

const ArtifactDetail = ({ artifact }) => {
  const { id, key, description, createdAt } = artifact;

  return (
    <VStack align="start" p={4} pt={0} w="100%" spacing={3}>
      <Text>{description}</Text>
      <Grid templateColumns="max-content 1fr" gap={2} alignItems="center">
        <GridItem>
          <Text fontSize="sm" color="gray.500">
            ID:
          </Text>
        </GridItem>
        <GridItem>{id}</GridItem>
        <GridItem>
          <Text fontSize="sm" color="gray.500">
            Key:
          </Text>
        </GridItem>
        <GridItem>{key}</GridItem>
        <GridItem>
          <Text fontSize="sm" color="gray.500">
            Storage Type:
          </Text>
        </GridItem>
        <GridItem>
          <Text fontSize="sm">{artifact.storage?.type}</Text>
        </GridItem>
        <GridItem>
          <Text fontSize="sm" color="gray.500">
            Storage ID:
          </Text>
        </GridItem>
        <GridItem>
          <Text fontSize="sm">{artifact.storage?.id}</Text>
        </GridItem>
        <GridItem>
          <Text fontSize="sm" color="gray.500">
            Created at:
          </Text>
        </GridItem>
        <GridItem>
          <Text fontSize="sm" color="gray.500">
            {new Date(createdAt).toLocaleString()}
          </Text>
        </GridItem>
      </Grid>
    </VStack>
  );
};

export default ArtifactDetail;
