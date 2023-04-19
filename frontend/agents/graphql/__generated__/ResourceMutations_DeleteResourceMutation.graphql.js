/**
 * @generated SignedSource<<40bb2121c6639e29464585fca1919f0e>>
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
    "concreteType": "DeleteResourceMutation",
    "kind": "LinkedField",
    "name": "deleteResource",
    "plural": false,
    "selections": [
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "success",
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
    "name": "ResourceMutations_DeleteResourceMutation",
    "selections": (v1/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "ResourceMutations_DeleteResourceMutation",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "9cdb733184ad9c1b74660350e3b2d027",
    "id": null,
    "metadata": {},
    "name": "ResourceMutations_DeleteResourceMutation",
    "operationKind": "mutation",
    "text": "mutation ResourceMutations_DeleteResourceMutation(\n  $id: UUID!\n) {\n  deleteResource(id: $id) {\n    success\n  }\n}\n"
  }
};
})();

node.hash = "5a50110f3a400a3a24ddc8f7a9deb4f0";

module.exports = node;
