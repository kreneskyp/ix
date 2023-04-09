/**
 * @generated SignedSource<<89c40cd9f6cd1a81c432afe97e768ba9>>
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
    "name": "input"
  }
],
v1 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "id",
  "storageKey": null
},
v2 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "name",
  "storageKey": null
},
v3 = [
  {
    "alias": null,
    "args": [
      {
        "kind": "Variable",
        "name": "input",
        "variableName": "input"
      }
    ],
    "concreteType": "CreateTaskResponse",
    "kind": "LinkedField",
    "name": "createTask",
    "plural": false,
    "selections": [
      {
        "alias": null,
        "args": null,
        "concreteType": "TaskType",
        "kind": "LinkedField",
        "name": "task",
        "plural": false,
        "selections": [
          (v1/*: any*/),
          (v2/*: any*/),
          {
            "alias": null,
            "args": null,
            "concreteType": "AgentType",
            "kind": "LinkedField",
            "name": "agent",
            "plural": false,
            "selections": [
              (v1/*: any*/),
              (v2/*: any*/),
              {
                "alias": null,
                "args": null,
                "kind": "ScalarField",
                "name": "purpose",
                "storageKey": null
              }
            ],
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
              }
            ],
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
    "name": "TaskCreateFormMutation",
    "selections": (v3/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "TaskCreateFormMutation",
    "selections": (v3/*: any*/)
  },
  "params": {
    "cacheID": "92d59853210d6ae624bfc1abc730fa15",
    "id": null,
    "metadata": {},
    "name": "TaskCreateFormMutation",
    "operationKind": "mutation",
    "text": "mutation TaskCreateFormMutation(\n  $input: CreateTaskInput!\n) {\n  createTask(input: $input) {\n    task {\n      id\n      name\n      agent {\n        id\n        name\n        purpose\n      }\n      goals {\n        description\n      }\n    }\n  }\n}\n"
  }
};
})();

node.hash = "6b35056077bc83b7601c52774a464cec";

module.exports = node;
