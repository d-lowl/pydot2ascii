from pydot import Dot, graph_from_dot_data

def from_dot_string(string: str) -> str:
    return from_dot_graph(graph_from_dot_data(string))

def from_dot_graph(graph: Dot) -> str:
    return ""