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
                title=self._convert_link(requirement["title"]),
                text=self._convert_link(requirement["text"]),
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

    def _convert_link(self, string: str) -> str:
        """Convert markdown type link to PlantUML type link.

        Args:
            string (str): String possibly include link.

        Returns:
            str: Converted string
        """
        for _ in range(100):
            matched = re.findall(r".*(\[.*\]\(.*\)).*", string)
            if matched:
                target = matched[0]
                target_matched = re.findall(r"\[(.*)\]\((.*)\)", target)
                string = string.replace(
                    target, f"[[{target_matched[0][1]} {target_matched[0][0]}]]"
                )
            else:
                break
        return string
