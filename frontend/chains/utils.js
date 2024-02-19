export const addType = (type, setTypes) => {
  setTypes((prev) => {
    if (!prev.some((t) => t.id === type.id)) {
      return [...prev, type];
    }
    return prev;
  });
};

export const addTypes = (types, setTypes) => {
  setTypes((prev) => {
    const new_types = types.filter(
      (type) => !prev.some((t) => t.id === type.id)
    );
    return [...prev, ...new_types];
  });
};

export const addNode = (node, setNodes) => {
  setNodes((prevNodes) => {
    return { ...prevNodes, [node.id]: node };
  });
};

export const addNodes = (newNodes, setNodes) => {
  setNodes((prevNodes) => {
    const updatedNodes = { ...prevNodes };
    newNodes.forEach((node) => {
      if (!prevNodes[node.id]) {
        updatedNodes[node.id] = node;
      }
    });
    return updatedNodes;
  });
};
