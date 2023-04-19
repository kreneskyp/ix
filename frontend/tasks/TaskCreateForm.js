import React, { useState } from "react";
import { useMutation } from "react-relay";
import {
  Box,
  Button,
  Center,
  FormControl,
  FormLabel,
  HStack,
  Input,
  useToast,
  VStack,
} from "@chakra-ui/react";
import { AgentSelect } from "agents/AgentSelect";
import { CreateTaskMutation } from "tasks/graphql/CreateTaskMutation";
import { useNavigate } from "react-router-dom";

const DEFAULT_AGENT = "a6062f37-645e-46c4-9a9b-e77b15031566";

export const TaskCreateForm = ({ onMutationSuccess }) => {
  const [name, setName] = useState("");
  const [agentId, setAgentId] = useState(DEFAULT_AGENT);
  const [goals, setGoals] = useState(Array(5).fill(""));
  const [commit, isInFlight] = useMutation(CreateTaskMutation);
  let navigate = useNavigate();
  const toast = useToast();

  const handleGoalChange = (index, value) => {
    const newGoals = [...goals];
    newGoals[index] = value;
    setGoals(newGoals);
  };

  const handleAgentChange = (index, value) => {
    setAgentId(value);
  };

  const handleSubmit = () => {
    const input = {
      name,
      agentId: agentId,
      goals: goals.map((description) => ({ description })),
    };

    commit({
      variables: { input },
      onCompleted: (data) => {
        if (onMutationSuccess) {
          onMutationSuccess(data.createTask.task);
        }
        navigate(`/tasks/chat/${data.createTask.task.id}`);
      },
      onError: (error) => {
        toast({
          title: "Error",
          description: "Failed to save the task.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
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
      // agent selection
      <FormControl>
        <FormLabel>Agent</FormLabel>
        <AgentSelect value={agentId} onChange={handleAgentChange} />
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
