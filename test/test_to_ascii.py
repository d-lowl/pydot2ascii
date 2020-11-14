from pydot2ascii import *

simplest_dot = "graph G { 0 }"
simplest_ascii = (
    "+---+\n"
    "| 0 |\n"
    "+---+\n"
)

def test_simplest_dot():
    assert from_dot_string(simplest_dot) == simplest_ascii