/**
 * @generated SignedSource<<f0a0ddee86e78a73105464f5b542fa70>>
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
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "model",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "purpose",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "systemPrompt",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "commands",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "config",
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
    "name": "AgentProvider_AgentByIdQuery",
    "selections": (v1/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "AgentProvider_AgentByIdQuery",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "9a20aef007dd169371a53a549e58c518",
    "id": null,
    "metadata": {},
    "name": "AgentProvider_AgentByIdQuery",
    "operationKind": "query",
    "text": "query AgentProvider_AgentByIdQuery(\n  $id: ID!\n) {\n  agent(id: $id) {\n    id\n    name\n    model\n    purpose\n    systemPrompt\n    commands\n    config\n  }\n}\n"
  }
};
})();

node.hash = "d990d4afe50f97ee18749b8502302544";

module.exports = node;
