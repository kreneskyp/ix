import { useCallback, useMemo } from "react";
import useUpdateAPI from "utils/hooks/useUpdateAPI";
import { useAxiosDelete } from "utils/hooks/useAxiosDelete";
import { useAxios } from "utils/hooks/useAxios";

// utility for wrapping default onCompleted with onCompleted arg
const useNestedCallback = (func, callback) => {
  return (response, errors) => {
    func(response, errors);
    if (callback) {
      callback(response, errors);
    }
  };
};

export const useChainEditorAPI = ({
  onCompleted,
  onError,
  reactFlowInstance,
}) => {
  const { setNodes, setEdges } = reactFlowInstance || {};
  const onSuccess = onCompleted;

  const { call: createChain, isLoading: createChainLoading } = useUpdateAPI(
    `/api/chains/`,
    {
      onSuccess,
      onError,
      method: "post",
    }
  );

  const { call: axiosUpdateChain, isLoading: updateChainLoading } = useAxios(
    {
      onSuccess,
      onError,
      method: "put",
    },
    []
  );

  const updateChain = useCallback(
    (chainId, data) => {
      return axiosUpdateChain(`/api/chains/${chainId}`, { data });
    },
    [axiosUpdateNode]
  );

  const { call: axiosSetRoot, isLoading: setRootLoading } = useAxios(
    {
      onSuccess,
      onError,
      method: "post",
    },
    []
  );

  const setRoots = useCallback(
    (chainId, data) => {
      return axiosSetRoot(`/api/chains/${chainId}/set_root`, { data });
    },
    [axiosUpdateNode]
  );

  const { call: addNode, isLoading: addNodeLoading } = useUpdateAPI(
    `/api/chains/nodes`,
    {
      onSuccess,
      onError,
      method: "post",
    }
  );

  const { call: axiosUpdateNode, isLoading: updateNodeLoading } = useAxios(
    {
      onSuccess,
      onError,
      method: "put",
    },
    []
  );

  const updateNode = useCallback(
    (node_id, data) => {
      return axiosUpdateNode(`/api/chains/nodes/${node_id}`, { data });
    },
    [axiosUpdateNode]
  );

  const {
    call: axiosUpdateNodePosition,
    isLoading: updateNodePositionLoading,
  } = useAxios(
    {
      onSuccess,
      onError,
      method: "post",
    },
    []
  );

  const updateNodePosition = useCallback(
    (node_id, data) => {
      return axiosUpdateNodePosition(`/api/chains/nodes/${node_id}/position`, {
        data,
      });
    },
    [axiosUpdateNodePosition]
  );

  const onDeleteNode = useCallback(
    useNestedCallback((response) => {
      const { id: node_id } = response.data;
      setNodes((nodes) => nodes.filter((n) => n.id !== node_id));
      setEdges((edges) =>
        edges.filter(
          (edge) => edge.source !== node_id && edge.target !== node_id
        )
      );
    }, onCompleted),
    [reactFlowInstance]
  );

  const { call: axiosDeleteNode, isLoading: deleteNodeLoading } =
    useAxiosDelete(
      {
        onSuccess: onDeleteNode,
        onError,
      },
      [onDeleteNode]
    );

  const deleteNode = useCallback(
    (node_id) => {
      return axiosDeleteNode(`/api/chains/nodes/${node_id}`);
    },
    [axiosDeleteNode]
  );

  const { call: addEdge, isLoading: addEdgeLoading } = useUpdateAPI(
    `/api/chains/edges`,
    {
      onSuccess,
      onError,
      method: "post",
    }
  );

  const { call: axiosUpdateEdge, isLoading: updateEdgeLoading } = useAxios(
    {
      onSuccess,
      onError,
      method: "put",
    },
    []
  );

  const updateEdge = useCallback(
    (edge_id, data) => {
      return axiosUpdateEdge(`/api/chains/edges/${edge_id}`, { data });
    },
    [axiosUpdateEdge]
  );

  const { call: axiosDeleteEdge, isLoading: deleteEdgeLoading } =
    useAxiosDelete(
      {
        onSuccess,
        onError,
      },
      []
    );

  const deleteEdge = useCallback(
    (edge_id) => {
      return axiosDeleteEdge(`/api/chains/edges/${edge_id}`);
    },
    [axiosDeleteEdge]
  );

  return useMemo(() => {
    const isLoading =
      createChainLoading ||
      updateChainLoading ||
      setRootLoading ||
      addNodeLoading ||
      updateNodeLoading ||
      updateNodePositionLoading ||
      deleteNodeLoading ||
      addEdgeLoading ||
      updateEdgeLoading ||
      deleteEdgeLoading;

    return {
      isLoading,
      createChain,
      updateChain,
      setRoots,
      updateNode,
      updateNodePosition,
      addNode,
      deleteNode,
      addEdge,
      updateEdge,
      deleteEdge,
    };
  }, [onCompleted, onError, reactFlowInstance]);
};
