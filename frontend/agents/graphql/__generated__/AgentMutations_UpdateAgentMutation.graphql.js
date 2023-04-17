/**
 * @generated SignedSource<<59e95b0df6edfdd212ba1d5cce37995c>>
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
    "concreteType": "UpdateAgentMutation",
    "kind": "LinkedField",
    "name": "updateAgent",
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
    "name": "AgentMutations_UpdateAgentMutation",
    "selections": (v1/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "AgentMutations_UpdateAgentMutation",
    "selections": (v1/*: any*/)
  },
  "params": {
    "cacheID": "a0a067bd996466dd1fe3ba4c53c10bea",
    "id": null,
    "metadata": {},
    "name": "AgentMutations_UpdateAgentMutation",
    "operationKind": "mutation",
    "text": "mutation AgentMutations_UpdateAgentMutation(\n  $input: AgentInput!\n) {\n  updateAgent(input: $input) {\n    agent {\n      id\n      name\n      model\n      systemPrompt\n      commands\n      config\n    }\n  }\n}\n"
  }
};
})();

node.hash = "b2709c03868e6519b5160550b4e712b7";

module.exports = node;
