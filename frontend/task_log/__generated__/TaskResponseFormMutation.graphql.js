/**
 * @generated SignedSource<<84497838de69306e1becace1525ca706>>
 * @lightSyntaxTransform
 * @nogrep
 */

/* eslint-disable */

"use strict";

var node = (function () {
  var v0 = [
      {
        defaultValue: null,
        kind: "LocalArgument",
        name: "input",
      },
    ],
    v1 = [
      {
        kind: "Variable",
        name: "input",
        variableName: "input",
      },
    ],
    v2 = {
      alias: null,
      args: null,
      kind: "ScalarField",
      name: "userResponse",
      storageKey: null,
    },
    v3 = {
      alias: null,
      args: null,
      kind: "ScalarField",
      name: "authorized",
      storageKey: null,
    };
  return {
    fragment: {
      argumentDefinitions: (v0 /*: any*/),
      kind: "Fragment",
      metadata: null,
      name: "TaskResponseFormMutation",
      selections: [
        {
          alias: null,
          args: (v1 /*: any*/),
          concreteType: "TaskLogResponse",
          kind: "LinkedField",
          name: "respondToTaskLogMessage",
          plural: false,
          selections: [
            {
              alias: null,
              args: null,
              concreteType: "TaskLog",
              kind: "LinkedField",
              name: "taskLog",
              plural: false,
              selections: [(v2 /*: any*/), (v3 /*: any*/)],
              storageKey: null,
            },
          ],
          storageKey: null,
        },
      ],
      type: "Mutation",
      abstractKey: null,
    },
    kind: "Request",
    operation: {
      argumentDefinitions: (v0 /*: any*/),
      kind: "Operation",
      name: "TaskResponseFormMutation",
      selections: [
        {
          alias: null,
          args: (v1 /*: any*/),
          concreteType: "TaskLogResponse",
          kind: "LinkedField",
          name: "respondToTaskLogMessage",
          plural: false,
          selections: [
            {
              alias: null,
              args: null,
              concreteType: "TaskLog",
              kind: "LinkedField",
              name: "taskLog",
              plural: false,
              selections: [
                (v2 /*: any*/),
                (v3 /*: any*/),
                {
                  alias: null,
                  args: null,
                  kind: "ScalarField",
                  name: "id",
                  storageKey: null,
                },
              ],
              storageKey: null,
            },
          ],
          storageKey: null,
        },
      ],
    },
    params: {
      cacheID: "96bd6b04970729859856125863841843",
      id: null,
      metadata: {},
      name: "TaskResponseFormMutation",
      operationKind: "mutation",
      text: "mutation TaskResponseFormMutation(\n  $input: TaskLogMessageResponseInput!\n) {\n  respondToTaskLogMessage(input: $input) {\n    taskLog {\n      userResponse\n      authorized\n      id\n    }\n  }\n}\n",
    },
  };
})();

node.hash = "91bb1fb3ecadc8d40ccb6709929ac949";

module.exports = node;
