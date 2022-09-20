import networkx as nx
import re
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

    def get_target_connected_nodes(
        self, graph: nx.DiGraph, target_id: str, up_level: int, down_level
    ) -> List[str]:
        # Get upper nodes
        upper_nodes = self._get_upper_nodes(graph, target_id, up_level)

        # Get lower nodes
        lower_nodes = self._get_lower_nodes(graph, target_id, down_level)

        return list(set(upper_nodes + lower_nodes))

    def _get_upper_nodes(
        self, graph: nx.DiGraph, target_id: str, up_level: int
    ) -> List[str]:
        upper_nodes = [target_id]
        for _ in range(up_level):
            temp_upper_nodes = []
            for upper_node in upper_nodes:
                for node in graph.successors(upper_node):
                    temp_upper_nodes.append(node)
            upper_nodes = list(set(upper_nodes + temp_upper_nodes))

        return upper_nodes

    def _get_lower_nodes(
        self, graph: nx.DiGraph, target_id: str, down_level: int
    ) -> List[str]:
        lower_nodes = [target_id]
        for _ in range(down_level):
            temp_lower_nodes = []
            for upper_node in lower_nodes:
                for node in graph.predecessors(upper_node):
                    temp_lower_nodes.append(node)
            lower_nodes = list(set(lower_nodes + temp_lower_nodes))

        return lower_nodes

    def shrink_graph(self, graph: nx.DiGraph, related_nodes: List[str]) -> nx.DiGraph:
        # Remove non-related nodes
        all_nodes = list(graph.nodes())
        remove_nodes = list(set(all_nodes) - set(related_nodes))
        for remove_node in remove_nodes:
            graph.remove_node(remove_node)

        return graph

    def get_unique_id_from_title(self, graph: nx.DiGraph, title: str) -> str:
        """Get unique_id from title or id string

        Note:
            This method judges with title > id priority and return first detected.

        Args:
            graph (nx.DiGraph): Graph
            title (str): Title string

        Returns:
            str: unique_id of title entity
        """
        title = title.strip()
        unique_id = ""
        for node in graph.nodes(data=True):
            node_title = node[1]["title"]
            node_id = node[1]["id"]
            if node_title == title or node_id == title:
                unique_id = node[1]["unique_id"]
                break

        return unique_id
