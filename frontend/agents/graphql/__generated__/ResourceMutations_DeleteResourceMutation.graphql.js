/**
 * @generated SignedSource<<8b242b94d6c03eb8427a2d7184656da9>>
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
    "cacheID": "ca52a0a1b30e3cfc2c80bd14d9103fe2",
    "id": null,
    "metadata": {},
    "name": "ResourceMutations_DeleteResourceMutation",
    "operationKind": "mutation",
    "text": "mutation ResourceMutations_DeleteResourceMutation(\n  $id: ID!\n) {\n  deleteResource(id: $id) {\n    success\n  }\n}\n"
  }
};
})();

node.hash = "2b469767a177af44e4e522024553c3a1";

module.exports = node;
