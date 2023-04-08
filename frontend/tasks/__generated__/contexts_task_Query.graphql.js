/**
 * @generated SignedSource<<193971138314eea87489007ec3409ca4>>
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
    "concreteType": "Task",
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
        "concreteType": "Goal",
        "kind": "LinkedField",
        "name": "goals",
        "plural": true,
        "selections": [
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
    "cacheID": "a8d8544e00c3bfe073d526ddc3a9ae53",
    "id": null,
    "metadata": {},
    "name": "contexts_task_Query",
    "operationKind": "query",
    "text": "query contexts_task_Query(\n  $id: ID!\n) {\n  task(id: $id) {\n    id\n    isComplete\n    completeAt\n    goals {\n      name\n      description\n      complete\n    }\n  }\n}\n"
  }
};
})();

node.hash = "1a150ee33c5c0c9248a0c423fe9cf1d5";

module.exports = node;
