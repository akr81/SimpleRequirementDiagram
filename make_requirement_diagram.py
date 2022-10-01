import json
import networkx as nx
import re
import typer
from typing import Union

from src.manage_graph import ManageGraph
from src.convert_puml_code import ConvertPumlCode

app = typer.Typer(add_completion=False)


class MakeRequirementDiagram:
    def make_requirement_diagram(
        self,
        requirement: Union[str, nx.DiGraph],
        target: str = None,
        title: str = None,
        detail: bool = False,
        debug: bool = False,
        upper: int = 100,
        lower: int = 100,
        left_to_right: bool = False,
        width: int = 24,
        output: str = "./sample.puml",
    ):
        manager = ManageGraph()
        if isinstance(requirement, str):
            with open(requirement, "r", encoding="UTF-8") as f:
                requirements = json.load(f)
            graph = manager.make_graph(requirements)
        elif isinstance(requirement, nx.DiGraph):
            graph = requirement
        else:
            raise ValueError(f"Unexpected requirement specified: {type(requirement)}")

        if debug:
            detail = True

        if target:
            # Target specified as title -> get unique_id
            if not re.match("[0-9]{8}_[0-9]{6}", target):
                target = manager.get_unique_id_from_title(graph, target)

            related_nodes = manager.get_target_connected_nodes(
                graph, target, upper, lower
            )
            graph = manager.shrink_graph(graph, related_nodes)

        converter = ConvertPumlCode(
            {
                "detail": detail,
                "width": width,
                "left_to_right": left_to_right,
                "debug": debug,
            }
        )

        puml = converter.convert_to_puml(graph, title, target)

        with open(output, "w", encoding="UTF-8") as f:
            f.writelines(puml)


@app.command()
def main(
    req: str = typer.Option(
        ..., "-r", "--req", help="path to the requirements json file"
    ),
    target: str = typer.Option(
        None, "-t", "--target", help="target node as unique_id or title"
    ),
    upper: int = typer.Option(100, "-u", "--upper", help="upper level from target"),
    lower: int = typer.Option(100, "-l", "--lower", help="lower level from target"),
    title: str = typer.Option("", "-ti", "--title", help="title of diagram"),
    left_to_right: bool = typer.Option(
        False, "-lr", "--left_to_right", help="change plot direction left to right"
    ),
    detail: bool = typer.Option(
        False, "-d", "--detail", help="display text information"
    ),
    debug: bool = typer.Option(
        False, "-D", "--debug", help="display text and unique_id information"
    ),
    width: int = typer.Option(24, "-w", "--width", help="entity char width"),
    output: str = typer.Option(
        "./sample.puml", "-o", "--output", help="path to output puml file"
    ),
):
    maker = MakeRequirementDiagram()
    maker.make_requirement_diagram(
        req,
        target,
        title,
        detail,
        debug,
        upper,
        lower,
        left_to_right,
        width,
        output,
    )


if __name__ == "__main__":
    app()
