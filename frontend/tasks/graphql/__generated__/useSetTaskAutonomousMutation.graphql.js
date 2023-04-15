/**
 * @generated SignedSource<<27ad7c29eb5956acbeb89d3ffe9d9bd6>>
 * @lightSyntaxTransform
 * @nogrep
 */

/* eslint-disable */

'use strict';

var node = (function(){
var v0 = {
  "defaultValue": null,
  "kind": "LocalArgument",
  "name": "autonomous"
},
v1 = {
  "defaultValue": null,
  "kind": "LocalArgument",
  "name": "taskId"
},
v2 = [
  {
    "alias": null,
    "args": [
      {
        "kind": "Variable",
        "name": "autonomous",
        "variableName": "autonomous"
      },
      {
        "kind": "Variable",
        "name": "taskId",
        "variableName": "taskId"
      }
    ],
    "concreteType": "SetTaskAutonomousMutation",
    "kind": "LinkedField",
    "name": "setTaskAutonomous",
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
            "name": "autonomous",
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
    "argumentDefinitions": [
      (v0/*: any*/),
      (v1/*: any*/)
    ],
    "kind": "Fragment",
    "metadata": null,
    "name": "useSetTaskAutonomousMutation",
    "selections": (v2/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [
      (v1/*: any*/),
      (v0/*: any*/)
    ],
    "kind": "Operation",
    "name": "useSetTaskAutonomousMutation",
    "selections": (v2/*: any*/)
  },
  "params": {
    "cacheID": "ba6e2ad920f1128a9a1f4ba76925a524",
    "id": null,
    "metadata": {},
    "name": "useSetTaskAutonomousMutation",
    "operationKind": "mutation",
    "text": "mutation useSetTaskAutonomousMutation(\n  $taskId: ID!\n  $autonomous: Boolean!\n) {\n  setTaskAutonomous(taskId: $taskId, autonomous: $autonomous) {\n    task {\n      id\n      autonomous\n    }\n  }\n}\n"
  }
};
})();

node.hash = "7b443399475ccea6331a06032fd6f331";

module.exports = node;
