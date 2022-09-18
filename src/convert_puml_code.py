from typing import Dict, List, Any
import networkx as nx


class ConvertPumlCode:
    def __init__(self, config: Dict[str, Any]):
        self.detail = config["detail"]
        self.width = config["width"]

    def convert_to_puml(self, graph: nx.DiGraph, title: str) -> str:
        ret = """
@startuml

scale 2.0
hide circle
hide empty members
hide method
skinparam linetype polyline
skinparam linetype ortho

"""
        # Add title as package
        # req Title [setting]
        ret += f"package {title} <<Frame>> " + "{\n"

        # Convert nodes
        for node in graph.nodes(data=True):
            ret += self._convert_node(node) + "\n"

        # Convert edges
        for edge in graph.edges(data=True):
            ret += self._convert_edge(edge) + "\n"
            if "note" in edge[2] and edge[2]["note"] != "":
                ret += self._convert_note_edge(edge[2]["note"], graph.nodes(data=True))

        ret += "\n}\n@enduml\n"
        return ret

    def _convert_node(self, node):
        attr = node[1]
        type = attr["type"]
        ret = ""
        if type == "usecase":
            ret = self._convert_usecase(attr)
        elif type == "requirement":
            ret = self._convert_requirement(attr)
        elif type == "block":
            ret = self._convert_block(attr)
        elif type == "rationale" or type == "problem":
            ret = self._convert_note_entity(attr)
        else:
            raise ValueError(f"No implement error: Unknown type specified: {type}")

        return ret

    def _convert_usecase(self, data: Dict[str, Any]) -> str:
        # For PlantUML, the "usecase" entity cannot used on class diagram
        ret = f"class \"{self._get_title_string(data)}\" as {data['unique_id']} <<usecase>>"
        return ret

    def _convert_requirement(self, data: Dict[str, Any]) -> str:
        if self.detail:
            text = self._insert_newline(data["text"])
            ret = (
                f"class \"{data['title']}\" as {data['unique_id']} <<requirement>> "
                + "{\n"
            )
            ret += f"id=\"{data['id']}\"\n"
            ret += f'text="{text}"\n'
            ret += "}\n"
        else:
            ret = f"class \"{self._get_title_string(data)}\" as {data['unique_id']} <<requirement>>"
        return ret

    def _convert_block(self, data: Dict[str, Any]) -> str:
        ret = (
            f"class \"{self._get_title_string(data)}\" as {data['unique_id']} <<block>>"
        )
        return ret

    def _convert_note_entity(self, data: Dict[str, Any]) -> str:
        ret = f"""note as {data['unique_id']}
<<{data['type']}>>
{data['title']}
end note"""
        return ret

    def _get_title_string(self, data: Dict[str, Any]) -> str:
        """Return title string (ID + title)

        Args:
            data (Dict[str, Any]): Node attribute information

        Returns:
            str: Title string
        """
        if data["id"] != "":
            return f"{data['id']}\\n{data['title']}"
        else:
            return f"{data['title']}"

    def _convert_edge(self, data: Dict[str, Any]):
        src = data[0]
        dst = data[1]
        kind = data[2]["kind"]
        ret = ""
        if kind == "contains":
            ret = f"{dst} +-- {src}"
        elif kind == "refine":
            ret = f"{src} ..> {dst}: <<refine>>"
        elif kind == "deriveReqt":
            ret = f"{dst} <.. {src}: <<deriveReqt>>"
        elif kind == "satisfy":
            ret = f"{dst} <.. {src}: <<satisfy>>"
        elif kind == "None":
            # For rationale and problem (entiry) only
            ret = f"{dst} <.. {src}"
        else:
            raise ValueError(f"No implement exist for relation kind: {kind}")

        return ret

    def _convert_note_edge(self, note_id: str, nodes: List[Dict[str, Any]]) -> str:
        ret = ""
        for node in nodes:
            if node[1]["unique_id"] == note_id:
                ret += f"""
note on link
<<{node[1]["type"]}>>
{node[1]["title"]}
end note
"""
        return ret

    def _insert_newline(self, string: str) -> str:
        """Insert newline to long string to save width

        Args:
            string (str): long string

        Returns:
            str: inserted string
        """
        print(len(string), string)
        if " " in string:
            print("English")
            # For English text
            words = string.split(" ")
            string = ""
            temp_string = ""
            for _ in range(len(words)):
                word = words.pop(0)
                temp_string += word + " "
                if len(temp_string) > self.width:
                    string += temp_string.strip() + "\\n"
                    temp_string = ""
            string += temp_string.strip()
        else:
            # For Japanese text
            index_list = sorted(
                list(range(0, len(string), int(self.width * 0.66))), reverse=True
            )
            string_as_list = list(string)
            for index in index_list:
                if index == 0:
                    break
                else:
                    string_as_list.insert(index, "\\n")
            string = "".join(string_as_list)
        return string
