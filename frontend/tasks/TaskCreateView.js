import React from 'react';
import { Box, Center, Heading, VStack, Button } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import TaskCreateForm from 'tasks/TaskCreateForm';

export const TaskCreateView = () => {
  const navigate = useNavigate();

  const handleMutationSuccess = (task) => {
    navigate(`/tasks/chat/${task.id}`);
  };



  return (
    <Center minHeight="100vh" minWidth="100vw">
      <Box
        p={8}
        borderWidth={1}
        borderRadius="lg"
        boxShadow="2xl"
        backgroundColor="white"
      >
        <VStack spacing={6} alignItems="center">
          <Heading as="h2" size="md" mb={4}>
            Define the task you would like me to accomplish.
          </Heading>
          <TaskCreateForm onMutationSuccess={handleMutationSuccess} />

        </VStack>
      </Box>
    </Center>
  );
};

export default TaskCreateView;
