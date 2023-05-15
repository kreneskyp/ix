import {
  Environment,
  Network,
  Observable,
  RecordSource,
  Store,
} from "relay-runtime";
// import { createClient } from 'graphql-ws';

import { SubscriptionClient } from "subscriptions-transport-ws";

// Create WebSocket client
const wsClient = new SubscriptionClient("ws://localhost:8000/graphql-ws/", {
  reconnect: true,
  connectionParams: {
    "Sec-WebSocket-Protocol": "graphql-ws",
  },
});

const subscribe = (operation, variables) => {
  return Observable.create((sink) => {
    const request = {
      query: operation.text,
      operationName: operation.name,
      variables,
    };

    // This will return a disposable subscription
    const disposable = wsClient.request(request).subscribe({
      next: (result) => {
        if (result.errors) {
          sink.error(result.errors);
        } else {
          sink.next(result);
        }
      },
      error: (error) => {
        sink.error(error);
      },
      complete: () => {
        sink.complete();
      },
    });

    return () => {
      disposable.unsubscribe();
    };
  });
};

const fetchQuery = async (operation, variables) => {
  const response = await fetch("/graphql/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: operation.text,
      variables,
    }),
  });
  return await response.json();
};

const network = Network.create(fetchQuery, subscribe);
const store = new Store(new RecordSource());

const environment = new Environment({
  network,
  store,
});

export default environment;
