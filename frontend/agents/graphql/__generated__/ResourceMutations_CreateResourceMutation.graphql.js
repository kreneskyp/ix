/**
 * @generated SignedSource<<8ad98d7e2747b8af1f1953eef8065541>>
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
v1 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "id",
  "storageKey": null
},
v2 = [
  {
    "alias": null,
    "args": [
      {
        "kind": "Variable",
        "name": "input",
        "variableName": "input"
      }
    ],
    "concreteType": "CreateResourceMutation",
    "kind": "LinkedField",
    "name": "createResource",
    "plural": false,
    "selections": [
      {
        "alias": null,
        "args": null,
        "concreteType": "ResourceType",
        "kind": "LinkedField",
        "name": "resource",
        "plural": false,
        "selections": [
          (v1/*: any*/),
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "type",
            "storageKey": null
          },
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "config",
            "storageKey": null
          },
          {
            "alias": null,
            "args": null,
            "concreteType": "AgentType",
            "kind": "LinkedField",
            "name": "agent",
            "plural": false,
            "selections": [
              (v1/*: any*/)
            ],
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
    "name": "ResourceMutations_CreateResourceMutation",
    "selections": (v2/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "ResourceMutations_CreateResourceMutation",
    "selections": (v2/*: any*/)
  },
  "params": {
    "cacheID": "57ac4bd486c6fc09ce325507f151cb47",
    "id": null,
    "metadata": {},
    "name": "ResourceMutations_CreateResourceMutation",
    "operationKind": "mutation",
    "text": "mutation ResourceMutations_CreateResourceMutation(\n  $input: ResourceInput!\n) {\n  createResource(input: $input) {\n    resource {\n      id\n      type\n      config\n      agent {\n        id\n      }\n    }\n  }\n}\n"
  }
};
})();

node.hash = "ac41cae34b72d2a90595704881e3e565";

module.exports = node;
