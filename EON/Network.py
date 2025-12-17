import networkx as nx
from DataPreparation.DataLoader import TYPE, DataLoader
from EON.Edge import Edge
from EON.Node import Node

SLOT_CAPACITY = 12.5


class Network(nx.DiGraph):
    def __init__(self):
        super().__init__()
        self.demands = []
        self.edges_container = []
        self.nodes_container = []

    def load_data(self, type: TYPE, number_of_demands_dir, count_of_demands_to_handle):
        data = DataLoader(type)
        number_of_nodes, number_of_edges, edges_in_node = data.interprete_network_topology_file()
        self.load_network_structure(edges_in_node)

        for i in range(number_of_nodes):
            self.nodes_container.append(Node(str(i)))

        for edge in self.edges_container:
            self.nodes_container[int(edge.source_node)].edges.append(edge)
        # data.interprete_path_file(self.nodes_container, self.edges_container)

        self.demands = data.get_demands(number_of_demands_dir, count_of_demands_to_handle)
        for demand in self.demands:
            demand.possible_paths = demand.convert_path(list(
                nx.all_simple_paths(self, source=str(demand.source_node), target=str(demand.destination_node))),
                self.edges_container)
            demand.possible_paths = demand.possible_paths[:10]

    def load_network_structure(self, edges_in_node):

        for u_node, node in enumerate(edges_in_node):
            for v_node, weight in enumerate(node):
                if weight != 0:
                    self.add_edge(str(u_node), str(v_node), weight=weight, slots=[-1] * 320)
        for edge in self.edges:
            weight = self[edge[0]][edge[1]]["weight"]
            self.edges_container.append(Edge(edge[0], edge[1], weight))


    def check_limitations(self):
        for demand in self.demands:
            if demand.grooming:
                return True
            if demand.selected_slots_idx == []:
                return False
            for i in range(1, len(demand.selected_slots_idx)):
                if demand.selected_slots_idx[i] != demand.selected_slots_idx[i - 1] + 1:
                    return False
            for edge in demand.selected_path.edges:
                if edge.slots[demand.selected_slots_idx[0]:demand.selected_slots_idx[0] + demand.required_slots] != [
                    demand.demand_no] * demand.required_slots:
                    return False
        return True

    def reset_slots(self):
        for edge in self.edges_container:
            edge.slots = [-1] * 320

    def check_number_of_groomings_and_mark(self):
        for demand in self.demands:
            if demand.grooming:  # TODO: NEW
                continue
            for demand_to_groom in self.demands:
                if demand_to_groom == demand or demand_to_groom == demand.groomed_to:
                    continue
                not_groomed = False
                for edge in demand.selected_path.edges:
                    if not edge in demand_to_groom.selected_path.edges:
                        not_groomed = True
                        break
                if not not_groomed:
                    demand.grooming = True
                    if not demand_to_groom.groomed_to is None:
                        demand.groomed_to = demand_to_groom.groomed_to
                        demand_to_groom.groomed_to.groomings_demands.append(demand)
                        break

                    demand.groomed_to = demand_to_groom
                    demand_to_groom.groomings_demands.append(demand)
                    break
        number_of_groomings = 0

        # Process recurention in groomings
        next = True
        while (next):
            next = False
            for demand in self.demands:
                if demand.grooming and len(demand.groomings_demands) != 0:
                    next = True
                    if demand.groomed_to in demand.groomings_demands:
                        demand.groomings_demands.remove(demand.groomed_to)
                        demand.groomed_to.grooming = False
                    for groomed_demand in demand.groomings_demands:
                        demand.groomings_demands.remove(groomed_demand)
                        groomed_demand.groomed_to = demand.groomed_to
                        demand.groomed_to.groomings_demands.append(groomed_demand)

        ####

        # for demand in self.demands:
        #     if demand.grooming:
        #         number_of_groomings += 1
        #         # demand.selected_path.print_path()
        #         # print("Groomed: " + str(demand.groomed_to.demand_no))
        #         # print("Groommings: " + str([demand.demand_no for demand in demand.groomings_demands]))
        #     else:
        #         pass
        #         # print("Not groomed:")
        #         # demand.selected_path.print_path()
        #         # print("Groommings: " + str([demand.demand_no for demand in demand.groomings_demands]))

        # print(f"Groomings: {number_of_groomings}")

    def select_modulation_logic(self):

        for demand in self.demands:
            if demand.actual_bitrate == 0:
                continue
            demand.bitrate_with_gromming += demand.actual_bitrate
            demand.actual_bitrate = 0
            for groomed_demand in demand.groomings_demands:
                demand.bitrate_with_gromming += groomed_demand.actual_bitrate
                groomed_demand.actual_bitrate = 0
            demand.path_lenght = demand.selected_path.path_lenght

    def allocate_network_slots(self):
        for demand in self.demands:
            demand_ok = False
            if demand.bitrate_with_gromming == 0:
                continue
            for slot_no in range(320 - demand.required_slots):
                slots = list(range(slot_no, slot_no + demand.required_slots))
                demand.selected_slots_idx = slots
                if demand.check_if_allocation_is_possible(self.edges_container):
                    demand.allocate_slots(slots, self.edges_container)
                    demand_ok = True
                    break
            if demand_ok == False:
                return False
            return True

if __name__ == '__main__':
    graph = Network()
    graph.load_data(TYPE.POL12, 0, 200)
    print(len(graph.edges_container))
