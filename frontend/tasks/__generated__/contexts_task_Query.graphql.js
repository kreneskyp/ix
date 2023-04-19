/**
 * @generated SignedSource<<528dcfff046c010459ef86dc720004ad>>
 * @lightSyntaxTransform
 * @nogrep
 */

/* eslint-disable */

'use strict';

var node = (function(){
var v0 = [
  {
    "defaultValue": null,
    "kind": "LocalArgument",
    "name": "id"
  }
],
v1 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "id",
  "storageKey": null
},
v2 = [
  {
    "alias": null,
    "args": [
      {
        "kind": "Variable",
        "name": "id",
        "variableName": "id"
      }
    ],
    "concreteType": "TaskType",
    "kind": "LinkedField",
    "name": "task",
    "plural": false,
    "selections": [
      (v1/*: any*/),
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "isComplete",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "completeAt",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "autonomous",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "concreteType": "GoalType",
        "kind": "LinkedField",
        "name": "goals",
        "plural": true,
        "selections": [
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "description",
            "storageKey": null
          },
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "complete",
            "storageKey": null
          }
        ],
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "concreteType": "AgentType",
        "kind": "LinkedField",
        "name": "agent",
        "plural": false,
        "selections": [
          (v1/*: any*/),
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "name",
            "storageKey": null
          },
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "model",
            "storageKey": null
          },
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "purpose",
            "storageKey": null
          }
        ],
        "storageKey": null
      }
    ],
    "storageKey": null
  }
];
return {
  "fragment": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Fragment",
    "metadata": null,
    "name": "contexts_task_Query",
    "selections": (v2/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "contexts_task_Query",
    "selections": (v2/*: any*/)
  },
  "params": {
    "cacheID": "b15a2ae29e7d0494182ae5683d85f2b7",
    "id": null,
    "metadata": {},
    "name": "contexts_task_Query",
    "operationKind": "query",
    "text": "query contexts_task_Query(\n  $id: UUID!\n) {\n  task(id: $id) {\n    id\n    isComplete\n    completeAt\n    autonomous\n    goals {\n      description\n      complete\n    }\n    agent {\n      id\n      name\n      model\n      purpose\n    }\n  }\n}\n"
  }
};
})();

node.hash = "feb02e8a80942a25e96acf73cf6ae17f";

module.exports = node;
