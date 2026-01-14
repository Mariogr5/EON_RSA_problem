import math

from EON.Path import Path
from EON.ModulationFormat import ModulationFormat


class Demand:
    def __init__(self, demand_no, source_node, destination_node, list_of_bitrates):

        self.demand_no = demand_no

        self.source_node = source_node
        self.destination_node = destination_node
        self.list_of_bitrates = list_of_bitrates

        self.actual_bitrate = 0
        self.number_of_supercanals = 0
        self.number_of_transceivers = self.number_of_supercanals * 2
        self.selected_path = []
        self.possible_paths = []
        self.selected_slots_idx = []
        self._path_lenght = 0

        # self.MODULATION_FORMATS = [
        #     ModulationFormat("QPSK", 9999999, 200, 6),
        #     ModulationFormat("8-QAM", 9999999, 400, 9),
        #     ModulationFormat("16-QAM", 800, 400, 6),
        #     ModulationFormat("16-QAM", 1600, 600, 9),
        #     ModulationFormat("32-QAM", 200, 800, 9),
        # ]

        self.selected_modulation = None
        # self.possible_modulations = self.get_candidates_modulation()

        self.required_slots = 0

        self.bitrate_with_gromming = self.actual_bitrate
        # self.grooming = False
        # self.groomed_to = None
        # self.groomings_demands = []

    @property
    def path_lenght(self):
        return self._path_lenght

    @path_lenght.setter
    def path_lenght(self, value):
        self._path_lenght = value
        # self.possible_modulations = self.get_candidates_modulation()
        # self.select_modulation_with_min_transceivers()

    def set_bitrate(self, bitrate):
        self.actual_bitrate = bitrate
        self.bitrate_with_gromming = 0
        self.grooming = False
        self.groomings_demands = []
        self.groomed_to = None
        self.required_slots = 0
        self.selected_slots_idx = []
        self.selected_modulation = None
        self.possible_modulations = []
        self.number_of_transceivers = 0
        self.number_of_supercanals = 0
        # self.path_lenght = 0

    # def get_candidates_modulation(self):
    #     candidates_modulation = self.MODULATION_FORMATS
    #
    #     for modulation in self.MODULATION_FORMATS:
    #         if self.path_lenght > modulation.max_lenght:
    #             candidates_modulation.remove(modulation)
    #     return candidates_modulation

    # def select_modulation(self, modulation):
    #     if modulation in self.possible_modulations:
    #         self.selected_modulation = modulation
    #     else:
    #         raise Exception("Enter valid modulation")
    #     if self.bitrate_with_gromming < self.selected_modulation.bitrate:
    #         self.number_of_supercanals = 1
    #     else:
    #         self.number_of_supercanals = math.ceil(self.bitrate_with_gromming / self.selected_modulation.bitrate)
    #
    #     self.required_slots = self.selected_modulation.number_of_slots * self.number_of_supercanals
    #     self.number_of_transceivers = self.number_of_supercanals * 2

    # def select_modulation_with_min_transceivers(self):
    #     min_transceivers = 999999
    #     selected_modulation = None
    #     required_slots = 99999
    #
    #     for modulation in self.possible_modulations:
    #         self.select_modulation(modulation)
    #         if self.number_of_transceivers < min_transceivers:
    #             min_transceivers = self.number_of_transceivers
    #             required_slots = self.required_slots
    #             selected_modulation = modulation
    #         elif self.number_of_transceivers == min_transceivers:
    #             if self.required_slots < required_slots:
    #                 required_slots = self.required_slots
    #                 selected_modulation = modulation
    #
    #     self.select_modulation(selected_modulation)

    # def allocate_slots(self, slots_idx, edge_container):
    #
    #     for edge in self.selected_path.edges:
    #         for edge_c in edge_container:
    #             if edge is edge_c:
    #                 for slot in self.selected_slots_idx:
    #                     edge_c.slots[slot] = self.demand_no
    #
    # def check_if_allocation_is_possible(self, edge_container):
    #     for edge in self.selected_path.edges:
    #         for edge_c in edge_container:
    #             if edge is edge_c:
    #                 for slot in self.selected_slots_idx:
    #                     if edge_c.slots[slot] != -1:
    #                         return False
    #     return True

    def convert_path(self, possible_paths, edges_container):
        converted_possible_paths = []
        for path in possible_paths:
            path_edges = []
            for node in range(len(path) - 1):
                for edge in edges_container:
                    if path[node] == edge.source_node and path[node + 1] == edge.destination_node:
                        path_edge = edge
                        path_edges.append(path_edge)
            converted_path = Path(path_edges)
            converted_possible_paths.append(converted_path)
        converted_possible_paths.sort(key=lambda x: x.path_lenght)
        return converted_possible_paths
