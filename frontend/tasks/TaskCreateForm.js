import React, { useState } from "react";
import { useMutation, graphql } from "react-relay";
import {
  Box,
  Button,
  Center,
  FormControl,
  FormLabel,
  HStack,
  Input,
  VStack,
} from "@chakra-ui/react";

const CreateTaskMutation = graphql`
  mutation TaskCreateFormMutation($input: CreateTaskInput!) {
    createTask(input: $input) {
      task {
        id
        name
        agent {
          id
          name
          purpose
        }
        goals {
          description
        }
      }
    }
  }
`;

export const TaskCreateForm = ({ onMutationSuccess }) => {
  const [name, setName] = useState("");
  const [goals, setGoals] = useState(Array(5).fill(""));
  const [commit, isInFlight] = useMutation(CreateTaskMutation);

  const handleGoalChange = (index, value) => {
    const newGoals = [...goals];
    newGoals[index] = value;
    setGoals(newGoals);
  };

  const handleSubmit = () => {
    const input = {
      name,
      goals: goals.map((description) => ({ description })),
    };

    commit({
      variables: { input },
      onCompleted: (data) => {
        if (onMutationSuccess) {
          onMutationSuccess(data.createTask.task);
        }
      },
      onError: (error) => {
        console.error("Error creating task:", error);
      },
    });
  };

  const loadExample = () => {
    // Customize this example data as needed
    const exampleData = {
      name: "Create a Django model for a car",
      goals: [
        { description: "Define a Car model" },
        { description: "Add fields for make, model, and year" },
        { description: "Create a migration file" },
        { description: "Apply the migration" },
        { description: "Write unit tests" },
      ],
    };

    setName(exampleData.name);
    setGoals(exampleData.goals.map(({ description }) => description));
  };

  return (
    <VStack mt={20} spacing={4} alignItems="flex-start">
      <FormControl>
        <FormLabel>Task Name</FormLabel>
        <Input
          type="text"
          placeholder="Task name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </FormControl>

      <FormControl>
        <FormLabel mt={2}>Goals</FormLabel>
        <VStack spacing={2} alignItems="flex-start">
          {goals.map((goal, index) => (
            <Box key={index}>
              <Input
                type="text"
                placeholder={`Goal ${index + 1}`}
                value={goal}
                onChange={(e) => handleGoalChange(index, e.target.value)}
                width={400}
              />
            </Box>
          ))}
        </VStack>
      </FormControl>
      <Center>
        <HStack mt={4} spacing={5}>
          <Button
            onClick={handleSubmit}
            isLoading={isInFlight}
            colorScheme="blue"
          >
            Create Task
          </Button>
          <Button onClick={loadExample} variant="outline">
            Load Example
          </Button>
        </HStack>
      </Center>
    </VStack>
  );
};

export default TaskCreateForm;
