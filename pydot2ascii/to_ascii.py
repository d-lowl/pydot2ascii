from pydot import Dot, graph_from_dot_data
from .layout import get_graph_layout

def from_dot_string(string: str) -> str:
    # Assuming there's only one graph/digraph in the string
    return from_dot_graph(graph_from_dot_data(string)[0])

def from_dot_graph(graph: Dot) -> str:
    grid = get_graph_layout(graph)
    return ""