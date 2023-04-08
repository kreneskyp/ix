/**
 * @generated SignedSource<<c57edd4a53710003b57506d9570b7897>>
 * @lightSyntaxTransform
 * @nogrep
 */

/* eslint-disable */

'use strict';

var node = (function(){
var v0 = [
  {
    "alias": null,
    "args": null,
    "concreteType": "Task",
    "kind": "LinkedField",
    "name": "tasks",
    "plural": true,
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
        "name": "createdAt",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "completeAt",
        "storageKey": null
      }
    ],
    "storageKey": null
  }
];
return {
  "fragment": {
    "argumentDefinitions": [],
    "kind": "Fragment",
    "metadata": null,
    "name": "contexts_tasks_Query",
    "selections": (v0/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [],
    "kind": "Operation",
    "name": "contexts_tasks_Query",
    "selections": (v0/*: any*/)
  },
  "params": {
    "cacheID": "426db914a7d56b540cf6337ff9b2922d",
    "id": null,
    "metadata": {},
    "name": "contexts_tasks_Query",
    "operationKind": "query",
    "text": "query contexts_tasks_Query {\n  tasks {\n    id\n    isComplete\n    createdAt\n    completeAt\n  }\n}\n"
  }
};
})();

node.hash = "809fd82770b058b6c0fe1b0634356ea9";

module.exports = node;
