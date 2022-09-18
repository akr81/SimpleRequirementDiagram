import click
import json
from src.manage_graph import ManageGraph


@click.command()
@click.option("-r", "--req", help="path to the requirements json file", required=True)
def main(req):
    with open(req, "r", encoding="UTF-8") as f:
        requirements = json.load(f)
    manager = ManageGraph()
    graph = manager.make_graph(requirements)
    print(graph.nodes)
    pass


if __name__ == "__main__":
    main()
