from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management import call_command
from io import StringIO
import json

from ix import chains
from ix.agents.models import Agent


class Command(BaseCommand):
    help = "Export Agent and related objects to a fixture using django dumpdata command"

    def add_arguments(self, parser):
        parser.add_argument("-a", "--alias", type=str, help="Alias of the Agent")
        parser.add_argument("-i", "--id", type=str, help="ID of the Agent")

    def handle(self, *args, **kwargs):
        agent_alias = kwargs["alias"]
        agent_id = kwargs["id"]
        agent = None

        if agent_alias:
            agent = Agent.objects.get(alias=agent_alias)
        elif agent_id:
            try:
                agent = Agent.objects.get(id=agent_id)
            except Agent.DoesNotExist:
                chain = Chain.objects.get(id=agent_id)
        else:
            self.stdout.write(
                self.style.ERROR("You must provide either an alias or an ID")
            )
            return

        if agent is not None:
            chain = agent.chain

        edge_ids = list(chain.edges.values_list("id", flat=True))
        node_ids = list(chain.nodes.values_list("id", flat=True))

        # Collect the serialized data
        collected_data = []

        to_dump = []
        if agent is not None:
            to_dump.append(agent)
        to_dump.extend(
            [
                ("chains.Chain", chain.id),
                ("chains.ChainNode", ",".join(map(str, node_ids))),
                ("chains.ChainEdge", ",".join(map(str, edge_ids))),
            ]
        )

        for model, pks in to_dump:
            output = StringIO()
            call_command(
                "dumpdata",
                model,
                "--indent=2",
                "--pks={}".format(pks),
                "--natural-foreign",
                stdout=output,
            )
            output.seek(0)
            data = json.loads(output.read())

            # Sort data by keys for this model type
            sorted_data = sorted(data, key=lambda x: x["pk"])
            collected_data.extend(sorted_data)

        # Write to file
        file_id = f"{agent.alias}" if agent is not None else f"{chain.id}"
        chain_fixtures_dir = Path(chains.__file__).parent / "fixtures/agent"
        filename = f"{chain_fixtures_dir}/{file_id}.json"
        with open(filename, "w") as f:
            json.dump(collected_data, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"Exported Agent @{file_id} to {filename}")
        )
