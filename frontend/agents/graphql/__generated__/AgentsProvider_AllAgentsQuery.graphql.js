/**
 * @generated SignedSource<<d6217930779708b9b7c473ebad9bb999>>
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
    "name": "AgentsProvider_AllAgentsQuery",
    "selections": (v0/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [],
    "kind": "Operation",
    "name": "AgentsProvider_AllAgentsQuery",
    "selections": (v0/*: any*/)
  },
  "params": {
    "cacheID": "3839ac1dbbb4551ec29b1418692b6703",
    "id": null,
    "metadata": {},
    "name": "AgentsProvider_AllAgentsQuery",
    "operationKind": "query",
    "text": "query AgentsProvider_AllAgentsQuery {\n  agents {\n    id\n    name\n    model\n    systemPrompt\n    commands\n    config\n  }\n}\n"
  }
};
})();

node.hash = "77cab925c1ba2be855eb7c7c1fb0043f";

module.exports = node;
