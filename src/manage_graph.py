import networkx as nx
from typing import Dict, List, Any


class ManageGraph:
    def make_graph(self, requirements: List[Dict[str, Any]]) -> nx.DiGraph:
        """Make directional graph object from requirements.

        Args:
            requirements (List[Dict[str, Any]]): Requiremnts

        Returns:
            nx.DiGraph: Directional graph
        """
        graph = nx.DiGraph()

        for requirement in requirements:
            graph.add_node(
                requirement["unique_id"],
                type=requirement["type"],
                id=requirement["id"],
                title=requirement["title"],
            )

            for relation in requirement["relations"]:
                # TODO "to" as list
                graph.add_edge(
                    requirement["unique_id"], relation["to"], kind=relation["kind"]
                )

        return graph
