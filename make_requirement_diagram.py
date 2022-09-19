import click
import json
import re
from src.manage_graph import ManageGraph
from src.convert_puml_code import ConvertPumlCode


@click.command()
@click.option("-r", "--req", help="path to the requirements json file", required=True)
@click.option("-t", "--target", help="target node as unique_id or title")
@click.option("-u", "--upper", help="upper level from target", default=100)
@click.option("-l", "--lower", help="lower level from target", default=100)
@click.option("-ti", "--title", help="title of diagram", default="")
@click.option(
    "-lr",
    "--left_to_right",
    help="change plot direction left to right",
    is_flag=True,
    default=False,
)
@click.option(
    "-d", "--detail", help="display text information", is_flag=True, default=False
)
@click.option("-w", "--width", help="entity char width", default=24)
@click.option(
    "-o", "--output", help="path to output puml file", default="./sample.puml"
)
def main(req, target, upper, lower, title, left_to_right, detail, width, output):
    with open(req, "r", encoding="UTF-8") as f:
        requirements = json.load(f)
    manager = ManageGraph()
    graph = manager.make_graph(requirements)

    if target:
        # Target specified as title -> get unique_id
        if not re.match("[0-9]{8}_[0-9]{6}", target):
            target = manager.get_unique_id_from_title(graph, target)

        related_nodes = manager.get_target_connected_nodes(graph, target, upper, lower)
        graph = manager.shrink_graph(graph, related_nodes)

    converter = ConvertPumlCode(
        {"detail": detail, "width": width, "left_to_right": left_to_right}
    )
    if not title:
        if not target:
            title = '"req Requirements [all]"'
        else:
            target_title = graph.nodes(data=True)[target]["title"]
            title = f'"req {target_title} ' + 'related requirements"'
    else:
        title = f'"req {title}"'
    puml = converter.convert_to_puml(graph, title)

    with open(output, "w", encoding="UTF-8") as f:
        f.writelines(puml)


if __name__ == "__main__":
    main()
