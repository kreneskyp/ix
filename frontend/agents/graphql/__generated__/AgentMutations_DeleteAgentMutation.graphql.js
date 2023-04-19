/**
 * @generated SignedSource<<bd2707e21bb6e7fab4ecd3f90cf54e2e>>
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
    "concreteType": "DeleteAgentMutation",
    "kind": "LinkedField",
    "name": "deleteAgent",
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
    "name": "AgentMutations_DeleteAgentMutation",
    "selections": (v1/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "AgentMutations_DeleteAgentMutation",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "106d80b073ef9b2bc616c7461dde4c01",
    "id": null,
    "metadata": {},
    "name": "AgentMutations_DeleteAgentMutation",
    "operationKind": "mutation",
    "text": "mutation AgentMutations_DeleteAgentMutation(\n  $id: UUID!\n) {\n  deleteAgent(id: $id) {\n    success\n  }\n}\n"
  }
};
})();

node.hash = "bcda4055cd109d51ccd9f74a1855bbc7";

module.exports = node;
