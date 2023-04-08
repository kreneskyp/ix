/**
 * @generated SignedSource<<9bb3103e83ef2490b6a5e6d0ce6cc8dd>>
 * @lightSyntaxTransform
 * @nogrep
 */

/* eslint-disable */

'use strict';

var node = {
  "argumentDefinitions": [
    {
      "defaultValue": null,
      "kind": "LocalArgument",
      "name": "agentId"
    }
  ],
  "kind": "Fragment",
  "metadata": null,
  "name": "contexts_agent",
  "selections": [
    {
      "alias": null,
      "args": [
        {
          "kind": "Variable",
          "name": "id",
          "variableName": "agentId"
        }
      ],
      "concreteType": "Agent",
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
  ],
  "type": "Query",
  "abstractKey": null
};

node.hash = "5085bb2d8986087fbf5614bf9bfa1c55";

module.exports = node;
