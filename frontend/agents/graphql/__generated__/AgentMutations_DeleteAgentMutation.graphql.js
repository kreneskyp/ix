/**
 * @generated SignedSource<<b833171e909a5e16fcea98f386f476a8>>
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
    "cacheID": "1b9c5c1ef2a233e64a567f1cfe670b2b",
    "id": null,
    "metadata": {},
    "name": "AgentMutations_DeleteAgentMutation",
    "operationKind": "mutation",
    "text": "mutation AgentMutations_DeleteAgentMutation(\n  $id: ID!\n) {\n  deleteAgent(id: $id) {\n    success\n  }\n}\n"
  }
};
})();

node.hash = "39785d98d0e9882e534b06f83db3d451";

module.exports = node;
