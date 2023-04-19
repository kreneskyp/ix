import React, { useEffect } from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { TasksTable } from "tasks/TasksTable";
import { TasksQuery } from "tasks/graphql/TasksQuery";
import { useQueryLoader } from "react-relay";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { ScrollableBox } from "site/ScrollableBox";

export const TasksListView = () => {
  const [queryRef, loadQuery] = useQueryLoader(TasksQuery);

  useEffect(() => {
    loadQuery({}, { fetchPolicy: "network-only" });
  }, []);

  let content;
  if (!queryRef) {
    return <Spinner />;
  } else {
    content = <TasksTable queryRef={queryRef} />;
  }

  return (
    <Layout>
      <LayoutLeftPane></LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Tasks</Heading>
          <ScrollableBox>{content}</ScrollableBox>
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
