/**
 * @generated SignedSource<<c767803b8cfc2a99c44ebacc92c1373e>>
 * @lightSyntaxTransform
 * @nogrep
 */

/* eslint-disable */

"use strict";

var node = (function () {
  var v0 = {
    alias: null,
    args: null,
    kind: "ScalarField",
    name: "id",
    storageKey: null,
  };
  return {
    argumentDefinitions: [
      {
        kind: "RootArgument",
        name: "taskId",
      },
    ],
    kind: "Fragment",
    metadata: null,
    name: "contexts_task_log",
    selections: [
      {
        alias: null,
        args: [
          {
            kind: "Variable",
            name: "taskId",
            variableName: "taskId",
          },
        ],
        concreteType: "TaskLog",
        kind: "LinkedField",
        name: "taskLogMessages",
        plural: true,
        selections: [
          (v0 /*: any*/),
          {
            alias: null,
            args: null,
            kind: "ScalarField",
            name: "assistant_timestamp",
            storageKey: null,
          },
          {
            alias: null,
            args: null,
            kind: "ScalarField",
            name: "user_timestamp",
            storageKey: null,
          },
          {
            alias: null,
            args: null,
            kind: "ScalarField",
            name: "command",
            storageKey: null,
          },
          {
            alias: null,
            args: null,
            concreteType: "Agent",
            kind: "LinkedField",
            name: "agent",
            plural: false,
            selections: [
              (v0 /*: any*/),
              {
                alias: null,
                args: null,
                kind: "ScalarField",
                name: "name",
                storageKey: null,
              },
            ],
            storageKey: null,
          },
        ],
        storageKey: null,
      },
    ],
    type: "Query",
    abstractKey: null,
  };
})();

node.hash = "0f093c5a786764b64b2c338b802bdfc5";

module.exports = node;
