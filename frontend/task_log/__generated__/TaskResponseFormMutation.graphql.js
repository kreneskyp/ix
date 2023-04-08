/**
 * @generated SignedSource<<1cce59712b47f323309152c53412110d>>
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
    "concreteType": "TaskLogResponse",
    "kind": "LinkedField",
    "name": "respondToTaskMsg",
    "plural": false,
    "selections": [
      {
        "alias": null,
        "args": null,
        "concreteType": "TaskLog",
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
            "name": "userResponse",
            "storageKey": null
          },
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "authorized",
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
    "cacheID": "fbdb45e29d56337d85fdd17fb7974ef0",
    "id": null,
    "metadata": {},
    "name": "TaskResponseFormMutation",
    "operationKind": "mutation",
    "text": "mutation TaskResponseFormMutation(\n  $input: TaskLogResponseInput!\n) {\n  respondToTaskMsg(input: $input) {\n    taskLogMessage {\n      id\n      userResponse\n      authorized\n    }\n    errors\n  }\n}\n"
  }
};
})();

node.hash = "63b9285df89c9ba19199dc9d60149611";

module.exports = node;
