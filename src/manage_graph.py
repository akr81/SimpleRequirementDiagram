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

        # First loop: Add all requirements
        for requirement in requirements:
            graph.add_node(
                requirement["unique_id"],
                type=requirement["type"],
                id=requirement["id"],
                title=requirement["title"],
                text=requirement["text"],
                unique_id=requirement["unique_id"],
            )

        # Second loop: Add relations with node check
        for requirement in requirements:
            for relation in requirement["relations"]:
                if relation["to"] not in graph.nodes:
                    raise ValueError(
                        f"Unknown node {relation['to']} specified as relation in {requirement}"
                    )
                if "note" not in relation:
                    graph.add_edge(
                        requirement["unique_id"], relation["to"], kind=relation["kind"]
                    )
                else:
                    graph.add_edge(
                        requirement["unique_id"],
                        relation["to"],
                        kind=relation["kind"],
                        note=relation["note"],
                    )

        return graph
