import React from 'react';
import { usePreloadedQuery } from 'react-relay/hooks';
import graphql from 'react-relay';
import { ReactFlowProvider, Controls, ReactFlow } from 'react-flow-renderer';

# const getClassWithMethodsQuery = graphql`
#     query ClassDiagramQuery($classPath: String!) {
#         getClassWithMethods(classPath: $classPath) {
#             name
#             type
#             superclass {
#                 name
#             }
#             childClasses {
#                 name
#             }
#             children {
#                 edges {
#                     node {
#                         name
#                         type
#                     }
#                 }
#             }
#         }
#     }
# `;

const ClassNode = ({ data }) => {
  return (
    <div style={{ background: 'lightblue', padding: '10px', borderRadius: '5px' }}>
      <strong>{data.label}</strong>
    </div>
  );
};

const onLoad = (reactFlowInstance) => {
  reactFlowInstance.fitView();
};

function ClassDiagram({ classPath, queryRef }) {
  const data = usePreloadedQuery(getClassWithMethodsQuery, queryRef);
  const elements = React.useMemo(() => {
    const nodes = [
      { id: data.getClassWithMethods.name, type: 'class', data: { label: data.getClassWithMethods.name }, position: { x: 250, y: 25 } },
      ...data.getClassWithMethods.childClasses.map((childClass, i) => (
        { id: childClass.name, data: { label: childClass.name }, position: { x: 100 + i * 100, y: 250 } }
      )),
      ...data.getClassWithMethods.children.edges.map((method, i) => (
        { id: method.node.name, data: { label: method.node.name }, position: { x: 100 + i * 100, y: 500 } }
      )),
    ];

    const edges = [
      ...data.getClassWithMethods.childClasses.map(childClass => ({ id: 'e' + data.getClassWithMethods.name + '-' + childClass.name, source: data.getClassWithMethods.name, target: childClass.name, animated: true })),
      ...data.getClassWithMethods.children.edges.map(method => ({ id: 'e' + data.getClassWithMethods.name + '-' + method.node.name, source: data.getClassWithMethods.name, target: method.node.name, animated: true })),
    ];

    return [...nodes, ...edges];
  }, [data]);

  return (
    <ReactFlowProvider>
      <ReactFlow elements={elements} nodeTypes={{ class: ClassNode }} onLoad={onLoad}>
        <Controls />
      </ReactFlow>
    </ReactFlowProvider>
  );
}

export default ClassDiagram;
