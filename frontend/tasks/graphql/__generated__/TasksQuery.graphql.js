/**
 * @generated SignedSource<<0f4d947bfbb7a71f85ca4dfbab6bb8f6>>
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
    "concreteType": "TaskType",
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
        "name": "name",
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
    "argumentDefinitions": [],
    "kind": "Fragment",
    "metadata": null,
    "name": "TasksQuery",
    "selections": (v0/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [],
    "kind": "Operation",
    "name": "TasksQuery",
    "selections": (v0/*: any*/)
  },
  "params": {
    "cacheID": "a7eafd9660eceec240aaa8b691051894",
    "id": null,
    "metadata": {},
    "name": "TasksQuery",
    "operationKind": "query",
    "text": "query TasksQuery {\n  tasks {\n    id\n    name\n    goals {\n      description\n      complete\n    }\n  }\n}\n"
  }
};
})();

node.hash = "ecf364cb35fe51a2f5dd0d4420455a6f";

module.exports = node;
