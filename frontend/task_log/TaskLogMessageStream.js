import React, { useState, useEffect } from "react";
import ChatMessage from "chat/ChatMessage";
import { fetchQuery, graphql } from "relay-runtime";
import { useTask } from "tasks/contexts";
import environment from "relay-environment";

const TaskLogMessageStream = () => {
  const [taskLogMessages, setMessages] = useState([]);
  const {task} = useTask();

  useEffect(() => {
    const fetchTaskLogMessages = async () => {
      const variables = {
        taskId: task.id,
      };
      const observable = fetchQuery(
        environment,
        graphql`
          query TaskLogMessageStreamQuery($taskId: ID!) {
            taskLogMessages(taskId: $taskId) {
              id
              role
              createdAt
              content {
                __typename
                ... on AssistantContentType {
                  type
                  thoughts {
                    text
                    reasoning
                    plan
                    criticism
                    speak
                  }
                  command {
                    name
                    args
                  }
                }
                ... on FeedbackRequestContentType {
                  type
                  message
                }
                ... on FeedbackContentType {
                  type
                  feedback
                }
                ... on SystemContentType {
                  type
                  message
                }
              }
              agent {
                id
                name
              }
            }
          }
        `,
        variables
      );

      const subscription = observable.subscribe({
        next: (response) => {
          if (response.taskLogMessages) {
            setMessages(response.taskLogMessages);
          }
        },
        error: (error) => console.error(error),
      });

      return () => subscription.unsubscribe();
    };

    const interval = setInterval(() => {
      fetchTaskLogMessages();
    }, 4000);
    return () => clearInterval(interval);
  }, [task]);

  return (
    <>
      {taskLogMessages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
    </>
  );
};

export default TaskLogMessageStream;
