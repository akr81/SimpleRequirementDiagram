from typing import Dict, List, Tuple, Any
import networkx as nx
import re
import unicodedata


class ConvertPumlCode:
    def __init__(self, config: Dict[str, Any]):
        self.detail = config["detail"]
        self.width = config["width"]
        self.left_to_right = config["left_to_right"]

    def convert_to_puml(self, graph: nx.DiGraph, title: str) -> str:
        ret = """
@startuml
"""
        if self.left_to_right:
            ret += "left to right direction\n"

        ret += """
hide circle
hide empty members
hide method
skinparam linetype polyline
skinparam linetype ortho
skinparam class {
BackgroundColor White
ArrowColor Black
BorderColor Black
}
skinparam note {
BackgroundColor White
ArrowColor Black
BorderColor Black
}

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
        title = self._insert_newline(data["title"])
        ret = f"class \"{self._get_title_string(data['id'], title)}\" as {data['unique_id']} <<usecase>>"
        return ret

    def _convert_requirement(self, data: Dict[str, Any]) -> str:
        title = self._insert_newline(data["title"])
        text = self._insert_newline(data["text"])

        if self.detail:
            ret = f"class \"{title}\" as {data['unique_id']} <<requirement>> " + "{\n"
            ret += f"id=\"{data['id']}\"\n"
            ret += f'text="{text}"\n'
            ret += "}\n"
        else:
            ret = f"class \"{self._get_title_string(data['id'], title)}\" as {data['unique_id']} <<requirement>>"
        return ret

    def _convert_block(self, data: Dict[str, Any]) -> str:
        title = self._insert_newline(data["title"])
        ret = f"class \"{self._get_title_string(data['id'], title)}\" as {data['unique_id']} <<block>>"
        return ret

    def _convert_note_entity(self, data: Dict[str, Any]) -> str:
        """Return note type entity string
        This method is for rationale, problem entity.

        Args:
            data (Dict[str, Any]): Entity (node)

        Returns:
            str: PlantUML string for note
        """
        # Display longer string from title and text
        if len(data["title"]) >= len(data["text"]):
            string = data["title"]
        else:
            string = data["text"]

        string = self._insert_newline(string)
        string = string.replace("\\n", "\n")
        ret = f"""note as {data['unique_id']}
<<{data['type']}>>
{string}
end note
"""
        return ret

    def _get_title_string(self, id: str, title: str) -> str:
        """Return title string (ID + title)

        Args:
            id (str): ID of requirement
            title (str): Title of requirement

        Returns:
            str: Title string
        """
        if id != "":
            return f"{id}\\n{title}"
        else:
            return f"{title}"

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
                # Display longer string from title and text
                if len(node[1]["title"]) >= len(node[1]["text"]):
                    string = node[1]["title"]
                else:
                    string = node[1]["text"]

                string = self._insert_newline(string)
                string = string.replace("\\n", "\n")

                ret += f"""
note on link
<<{node[1]["type"]}>>
{string}
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
        char_list = list(string)
        english_flag = True
        for char in char_list:
            if unicodedata.east_asian_width(char) == "W":
                # Japanese char exist
                english_flag = False
                break

        # Convert link to plantuml
        string = self._convert_link(string)
        string, stored = self._replace_link(string, "$")

        if english_flag:
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

        # Return unique char to link
        for link in stored:
            string = string.replace("$", link, 1)

        return string

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

    def _replace_link(self, string: str, unique: str = "$") -> Tuple[str, List[str]]:
        """Replace PlantUML type link to unique char.

        Args:
            string (str): String possibly include link.

        Returns:
            str: Converted string
        """
        stored = []
        for _ in range(100):
            matched = re.findall(r".*(\[\[.*\]\]).*", string)
            if matched:
                target = matched[0]
                stored.append(target)
                string = string.replace(target, unique)
            else:
                break
        return string, stored
