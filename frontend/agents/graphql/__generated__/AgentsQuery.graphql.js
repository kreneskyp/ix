/**
 * @generated SignedSource<<4fadf44b57171a8fccfc1548e5dd765a>>
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
    "concreteType": "AgentType",
    "kind": "LinkedField",
    "name": "agents",
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
        "kind": "ScalarField",
        "name": "model",
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
    "argumentDefinitions": [],
    "kind": "Fragment",
    "metadata": null,
    "name": "AgentsQuery",
    "selections": (v0/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [],
    "kind": "Operation",
    "name": "AgentsQuery",
    "selections": (v0/*: any*/)
  },
  "params": {
    "cacheID": "8966f49c7125e0d00edbe8e47f9e24cd",
    "id": null,
    "metadata": {},
    "name": "AgentsQuery",
    "operationKind": "query",
    "text": "query AgentsQuery {\n  agents {\n    id\n    name\n    model\n    systemPrompt\n    commands\n    config\n  }\n}\n"
  }
};
})();

node.hash = "ec1c7312220fac83126ad28fce92c041";

module.exports = node;
