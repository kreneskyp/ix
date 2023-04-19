/**
 * @generated SignedSource<<7ccf4f2e5fe697a136969eedf7b5a53c>>
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
    "cacheID": "e1ec673f443f3f4380b449e536a705a6",
    "id": null,
    "metadata": {},
    "name": "useSetTaskAutonomousMutation",
    "operationKind": "mutation",
    "text": "mutation useSetTaskAutonomousMutation(\n  $taskId: UUID!\n  $autonomous: Boolean!\n) {\n  setTaskAutonomous(taskId: $taskId, autonomous: $autonomous) {\n    task {\n      id\n      autonomous\n    }\n  }\n}\n"
  }
};
})();

node.hash = "1ac941d39ed5626d962ab3a75884a0fb";

module.exports = node;
