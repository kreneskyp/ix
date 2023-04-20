import { useQueryLoader } from "react-relay";
import { AgentsQuery } from "agents/graphql/AgentsQuery";
import React, { useEffect } from "react";
import { Select, Spinner } from "@chakra-ui/react";
import { AgentCardList } from "agents/AgentCardList";
import { usePreloadedQuery } from "react-relay/hooks";

/**
 * Separate options rendering because it's difficult to handle useQueryLoader
 * and usePreloadedQuery in the same component. useQueryLoader should probably
 * move higher up in the app component tree so that it can be triggered on
 * navigation links
 *
 * @param queryRef
 * @returns {JSX.Element}
 * @constructor
 */
export const AgentSelectOptions = ({ queryRef }) => {
  const { agents } = usePreloadedQuery(AgentsQuery, queryRef);

  return (
    <>
      {agents.map((agent) => (
        <option key={agent.id} value={agent.id}>
          {agent.name} - {agent.model}
        </option>
      ))}
    </>
  );
};

export const AgentSelect = (props) => {
  const [queryRef, loadQuery] = useQueryLoader(AgentsQuery);
  useEffect(() => {
    loadQuery({}, { fetchPolicy: "network-only" });
  }, []);

  let options;
  if (queryRef) {
    options = <AgentSelectOptions queryRef={queryRef} />;
  }

  return (
    <Select placeholder="Select agent" {...props}>
      {options}
    </Select>
  );
};
