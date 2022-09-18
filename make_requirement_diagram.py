import click
import json
import subprocess
from src.manage_graph import ManageGraph
from src.convert_puml_code import ConvertPumlCode


@click.command()
@click.option("-r", "--req", help="path to the requirements json file", required=True)
@click.option("-t", "--target", help="target node as unique_id")
@click.option("-u", "--upper", help="upper level from target", default=100)
@click.option("-l", "--lower", help="lower level from target", default=100)
def main(req, target, upper, lower):
    with open(req, "r", encoding="UTF-8") as f:
        requirements = json.load(f)
    manager = ManageGraph()
    graph = manager.make_graph(requirements)

    if target:
        related_nodes = manager.get_target_connected_nodes(graph, target, upper, lower)
        print(related_nodes)
        graph = manager.shrink_graph(graph, related_nodes)

    converter = ConvertPumlCode({})
    puml = converter.convert_to_puml(graph)
    print(puml)

    with open("sample.puml", "w", encoding="UTF-8") as f:
        f.writelines(puml)

    subprocess.run(["plantuml", "sample.puml"])


if __name__ == "__main__":
    main()
