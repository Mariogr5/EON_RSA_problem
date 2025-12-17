class Path:
    def __init__(self, edges):
        self.edges = edges
        self.path_lenght = self.calculate_path_lenght()

    def calculate_path_lenght(self):
        path_lenght = 0
        for edge in self.edges:
            path_lenght += edge.weight

        return path_lenght

    def print_path(self):

        nodes = [self.edges[0].source_node]
        for edge in self.edges:
            nodes.append(edge.destination_node)

        print(nodes)

