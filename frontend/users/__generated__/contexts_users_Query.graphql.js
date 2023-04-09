/**
 * @generated SignedSource<<375a053825c4ba7dc753c6a60b4002bf>>
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
    "concreteType": "UserType",
    "kind": "LinkedField",
    "name": "users",
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
        "name": "username",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "email",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "firstName",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "lastName",
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
    "name": "contexts_users_Query",
    "selections": (v0/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [],
    "kind": "Operation",
    "name": "contexts_users_Query",
    "selections": (v0/*: any*/)
  },
  "params": {
    "cacheID": "22b3f0c39872c7f742497f50329e6283",
    "id": null,
    "metadata": {},
    "name": "contexts_users_Query",
    "operationKind": "query",
    "text": "query contexts_users_Query {\n  users {\n    id\n    username\n    email\n    firstName\n    lastName\n  }\n}\n"
  }
};
})();

node.hash = "6956e50c42719533d00fe8c6d4be6027";

module.exports = node;
