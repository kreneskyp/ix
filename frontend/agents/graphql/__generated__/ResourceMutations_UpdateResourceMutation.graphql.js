/**
 * @generated SignedSource<<9e7f6a1f700d62529e10cff42a3da6fe>>
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
    "concreteType": "UpdateResourceMutation",
    "kind": "LinkedField",
    "name": "updateResource",
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
    "name": "ResourceMutations_UpdateResourceMutation",
    "selections": (v2/*: any*/),
    "type": "Mutation",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "ResourceMutations_UpdateResourceMutation",
    "selections": (v2/*: any*/)
  },
  "params": {
    "cacheID": "197a01ea48636a6d4497bf0099df33fb",
    "id": null,
    "metadata": {},
    "name": "ResourceMutations_UpdateResourceMutation",
    "operationKind": "mutation",
    "text": "mutation ResourceMutations_UpdateResourceMutation(\n  $input: ResourceInput!\n) {\n  updateResource(input: $input) {\n    resource {\n      id\n      type\n      config\n      agent {\n        id\n      }\n    }\n  }\n}\n"
  }
};
})();

node.hash = "c0a6bcf32dcbd55f44c09ac8dbbe9ac6";

module.exports = node;
