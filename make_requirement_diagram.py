import click
import json
import subprocess
from src.manage_graph import ManageGraph
from src.convert_puml_code import ConvertPumlCode


@click.command()
@click.option("-r", "--req", help="path to the requirements json file", required=True)
def main(req):
    with open(req, "r", encoding="UTF-8") as f:
        requirements = json.load(f)
    manager = ManageGraph()
    graph = manager.make_graph(requirements)
    print(graph.nodes(data=True))

    converter = ConvertPumlCode({})
    puml = converter.convert_to_puml(graph)
    print(puml)

    with open("sample.puml", "w", encoding="UTF-8") as f:
        f.writelines(puml)

    subprocess.run(["plantuml", "sample.puml"])


if __name__ == "__main__":
    main()
