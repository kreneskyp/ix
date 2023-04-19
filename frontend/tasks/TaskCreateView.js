import React from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { Heading, VStack } from "@chakra-ui/react";
import TaskCreateForm from "tasks/TaskCreateForm";

export const TaskCreateView = () => {
  return (
    <Layout>
      <LayoutLeftPane></LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Create Task</Heading>
          <TaskCreateForm />
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
