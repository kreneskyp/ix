/**
 * @generated SignedSource<<e101b993be682c5cc0b0caec1a55ea2d>>
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
    "concreteType": "AgentType",
    "kind": "LinkedField",
    "name": "agent",
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
        "name": "name",
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
    "name": "contexts_agent_Query",
    "selections": (v1/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "contexts_agent_Query",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "3b98d01c6c61d8020522650b5df3216c",
    "id": null,
    "metadata": {},
    "name": "contexts_agent_Query",
    "operationKind": "query",
    "text": "query contexts_agent_Query(\n  $id: ID!\n) {\n  agent(id: $id) {\n    id\n    name\n  }\n}\n"
  }
};
})();

node.hash = "8d8522d61a07cd50d987344a6c66aa5e";

module.exports = node;
