/**
 * @generated SignedSource<<32398b97889a570dc3a5fba1b9c74238>>
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
v1 = [
  {
    "alias": null,
    "args": [
      {
        "kind": "Variable",
        "name": "input",
        "variableName": "input"
      }
    ],
    "concreteType": "RespondToTaskLogMutation",
    "kind": "LinkedField",
    "name": "respondToTaskMsg",
    "plural": false,
    "selections": [
      {
        "alias": null,
        "args": null,
        "concreteType": "TaskLogMessageType",
        "kind": "LinkedField",
        "name": "taskLogMessage",
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
            "name": "role",
            "storageKey": null
          },
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "content",
            "storageKey": null
          }
        ],
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "errors",
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
    "name": "TaskResponseFormMutation",
    "selections": (v1/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "TaskResponseFormMutation",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "a67717131596acb10f6dba7129f172c2",
    "id": null,
    "metadata": {},
    "name": "TaskResponseFormMutation",
    "operationKind": "mutation",
    "text": "mutation TaskResponseFormMutation(\n  $input: TaskLogResponseInput!\n) {\n  respondToTaskMsg(input: $input) {\n    taskLogMessage {\n      id\n      role\n      content\n    }\n    errors\n  }\n}\n"
  }
};
})();

node.hash = "b80738f21a1b1a6b03f10099c26a1437";

module.exports = node;
