/**
 * @generated SignedSource<<402c7b326de9bf628797966a6f64e7e9>>
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
    "name": "input"
  }
],
v1 = [
  {
    "alias": null,
    "args": [
      {
        "kind": "Variable",
        "name": "input",
        "variableName": "input"
      }
    ],
    "concreteType": "CreateAgentMutation",
    "kind": "LinkedField",
    "name": "createAgent",
    "plural": false,
    "selections": [
      {
        "alias": null,
        "args": null,
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
    ],
    "storageKey": null
  }
];
return {
  "fragment": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Fragment",
    "metadata": null,
    "name": "AgentMutations_CreateAgentMutation",
    "selections": (v1/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "AgentMutations_CreateAgentMutation",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "67d84acfc0569e9931ac6ee4c27bb43b",
    "id": null,
    "metadata": {},
    "name": "AgentMutations_CreateAgentMutation",
    "operationKind": "mutation",
    "text": "mutation AgentMutations_CreateAgentMutation(\n  $input: AgentInput!\n) {\n  createAgent(input: $input) {\n    agent {\n      id\n      name\n      model\n      systemPrompt\n      commands\n      config\n    }\n  }\n}\n"
  }
};
})();

node.hash = "43fc56f8565b29f20bfd24c7e445bc0f";

module.exports = node;
