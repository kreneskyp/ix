/**
 * @generated SignedSource<<03714335cbff7344062082b700cfe062>>
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
v1 = [
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
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "id",
        "storageKey": null
      },
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
    "selections": (v1/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "contexts_task_Query",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "2a39acef6e49aa7c676cd5a6aba74fe7",
    "id": null,
    "metadata": {},
    "name": "contexts_task_Query",
    "operationKind": "query",
    "text": "query contexts_task_Query(\n  $id: ID!\n) {\n  task(id: $id) {\n    id\n    isComplete\n    completeAt\n    autonomous\n    goals {\n      description\n      complete\n    }\n  }\n}\n"
  }
};
})();

node.hash = "49ea9f7bd475f3345266ed0abadaf262";

module.exports = node;
