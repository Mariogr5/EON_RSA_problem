

class Edge:
    def __init__(self, source_node, destination_node, weight):
        self.source_node = source_node
        self.destination_node = destination_node
        self.weight = weight
        self.slots = [-1]*320
        self.all_demands_slots = 0