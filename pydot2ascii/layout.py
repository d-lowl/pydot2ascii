import numpy as np

def _reaches(node, edges):
    reaches = []
    queue = [node]
    while (len(queue) > 0):
        current = queue.pop()
        if current != node:
            reaches.append(current)
        for edge in edges:
            if edge.get_source() != current:
                continue
            next_node = edge.get_destination()
            if next_node not in reaches and next_node not in queue and next_node != node:
                    queue.append(next_node)
    return set(reaches)

def _get_all_node_names(graph):
    return list(set(
        [x.get_name() for x in graph.get_nodes()] +
        [x.get_source() for x in graph.get_edges()] +
        [x.get_destination() for x in graph.get_edges()] 
    ))

def _get_ranked_nodes(graph):
    reachability = {x: _reaches(x, graph.get_edges()) for x in _get_all_node_names(graph)}
    reachability = {source : set([target for target in targets if source not in reachability[target]]) for source, targets in reachability.items()}
    ranks = {x: 0 for x in _get_all_node_names(graph)}
    adjusted = True
    while adjusted:
        adjusted = False
        for source, targets in reachability.items():
            for target in targets:
                if ranks[source] >= ranks[target]:
                    ranks[target] = ranks[source] + 1
                    adjusted = True
    return ranks, [[node for node, rank in ranks.items() if rank == x] for x in sorted(set(ranks.values()))]

def _is_edge(graph, s, t):
    if isinstance(s, tuple) and isinstance(t, tuple):
        return s == t
    elif isinstance(s, tuple):
        return s[1] == t
    elif isinstance(t, tuple):
        return s == t[0]
    else:
        return len(graph.get_edge(s, t)) > 0
    
def _sparse_to_row(sparse, ncols):
    row = np.ndarray((ncols,), dtype=object)
    sparse = sorted(sparse, key=lambda x: x[1])
    for node, i in sparse:
        new_pos = i
        while row[new_pos] is not None:
            new_pos = (new_pos + 1) % ncols
        
        row[new_pos] = node
    return row

def _single_pass(grid, graph, ncols):
    if len(grid) <= 1:
        return grid
    for i, row in enumerate(grid):
        sparse = []
        for j, node in enumerate(row):
            if node is None:
                continue
            _n = 0
            _sum = 0
            if i != 0:
                for _j, parent in enumerate(grid[i-1]):
                    if _is_edge(graph, parent, node):
                        _n += 1
                        _sum += _j
            if i == 0:
                for _j, child in enumerate(grid[i+1]):
                    if _is_edge(graph, node, child):
                        _n += 1
                        _sum += _j
            if _n > 0:
                sparse.append((node, int(np.floor(_sum/_n))))
            else:
                sparse.append((node, j))
        grid[i] = _sparse_to_row(sparse, ncols)
    return grid

def _horizontal_layouting(grid, graph, ncols, max_iter=5):
    i = 0
    adjusted = True
    while (i < max_iter) and adjusted:
        new_grid = _single_pass(grid.copy(), graph, ncols)
        adjusted = (grid != new_grid).any()
        grid = new_grid
        i += 1
    return grid

"""
Get layered graph layout

Params:
graph: pydot.Dot -- graph to transform

Returns:
np.ndarray -- grid with strings representing nodes of a graph
"""
def get_graph_layout(graph):
    # Get vertical node ranking
    ranks, ranked_nodes = _get_ranked_nodes(graph)

    # Add auxilary nodes
    for edge in graph.get_edge_list():
        s = edge.get_source()
        srank = ranks[s]
        t = edge.get_destination()
        trank = ranks[t]
        for i in range(srank+1, trank):
            ranked_nodes[i].append((s, t))

    # Construct grid
    nrows = len(ranked_nodes)
    ncols = max((len(x) for x in ranked_nodes))
    grid = np.ndarray((nrows, ncols), dtype=object)
    for i, row in enumerate(ranked_nodes):
        grid[i, :len(row)] = row

    # Adjust nodes horizontally
    grid = _horizontal_layouting(grid, graph, ncols)

    # Remove auxilary nodes and return layout
    return np.array([[None if isinstance(x,tuple) else x for x in row] for row in grid])