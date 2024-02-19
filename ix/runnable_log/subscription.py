import logging
from uuid import UUID

import graphene
from channels_graphql_ws import Subscription
from graphene.types.generic import GenericScalar

logger = logging.getLogger(__name__)


class RunStartType(graphene.ObjectType):
    """A run starting"""

    task_id = graphene.UUID()


class ExecutionType(graphene.ObjectType):
    """A node executing within a run. Sent when a node starts and finishes executing."""

    id = graphene.UUID()
    parent_id = graphene.UUID(required=False)
    user_id = graphene.UUID()
    task_id = graphene.UUID()
    node_id = graphene.UUID()
    started_at = graphene.DateTime()
    finished_at = graphene.DateTime()
    completed = graphene.Boolean()
    inputs = GenericScalar(required=False)
    outputs = GenericScalar(required=False)
    message = graphene.String(required=False)


class RunEvent(graphene.Union):
    """Any event during a run from start to finish."""

    class Meta:
        types = (ExecutionType, RunStartType)


class RunEventSubscription(Subscription):
    """GraphQL subscription to progress events for a chain run."""

    event = graphene.Field(RunEvent)

    class Arguments:
        chainId = graphene.String()

    @staticmethod
    async def subscribe(root, info, chainId):
        """Called when a client subscribes."""
        logger.error(f"Client subscribing for run events for chain_id={chainId}")
        # Subscribe to a specific event type (e.g., "GROUP" or "EXECUTION")
        return [f"run_event_{chainId}"]

    @staticmethod
    async def publish(payload, info, chainId):
        """Called to notify subscribed clients."""
        datum = payload.get("event")
        event_type = payload.get("event_type")
        if event_type == "run":
            event = RunStartType(**datum)
        elif event_type == "execution":
            event = ExecutionType(
                id=datum.get("id"),
                parent_id=datum.get("parent_id"),
                user_id=datum.get("user_id"),
                task_id=datum.get("task_id"),
                node_id=datum.get("node_id"),
                started_at=datum.get("started_at"),
                finished_at=datum.get("finished_at", None),
                completed=datum.get("completed"),
                inputs=datum.get("inputs", None),
                outputs=datum.get("outputs", None),
                message=datum.get("message", None),
            )
        else:
            raise ValueError(f"Unknown event type: {event_type}")
        return RunEventSubscription(event=event)

    @classmethod
    def on_run(cls, chain_id: str | UUID, task_id: UUID):
        """Called when a new run is created."""
        cls.broadcast(
            group=f"run_event_{chain_id}",
            payload={"event_type": "run", "event": dict(task_id=str(task_id))},
        )

    @classmethod
    def on_execution(cls, chain_id: str | UUID, event: dict):
        """Called to send an execution event."""
        cls.broadcast(
            group=f"run_event_{chain_id}",
            payload={
                "event_type": "execution",
                "event": event,
            },
        )

    @classmethod
    async def aon_execution(cls, chain_id: str | UUID, event: dict):
        """Called to send an execution event."""
        await cls.broadcast_async(
            group=f"run_event_{chain_id}",
            payload={"event_type": "execution", "event": event},
        )
