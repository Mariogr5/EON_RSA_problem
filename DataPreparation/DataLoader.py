from enum import Enum
from EON.Demand import Demand
import os


class TYPE(Enum):
    POL12 = 1
    US26 = 2


class DataLoader:
    def __init__(self, type: TYPE):
        name = type.name
        self.data_dir_path = r"C:\pythonProject\RSA_time_varying_traffic-20251128T180422Z-1-001\RSA_time_varying_traffic"
        self.network_topology_file_path = self.data_dir_path + fr"\{name}\{name.lower()}.net"
        self.routing_paths_file_path = self.data_dir_path + fr"\{name}\{name.lower()}.pat"
        self.demands_folder_path = self.data_dir_path + fr"\{name}\demands_"

    def interprete_network_topology_file(self):
        with open(self.network_topology_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.rstrip("\n")
                lines[i] = line.split("\t")

        number_of_nodes = int(lines[0][0])
        number_of_links = int(lines[1][0])

        edges_in_node = []
        for line in lines[2:]:
            edges_in_node.append([int(x) for x in line])

        return number_of_nodes, number_of_links, edges_in_node

    def get_demands(self, number_of_demand, number_of_handled_demands=499):

        demand_folder_path = self.demands_folder_path + f"{number_of_demand}"

        # list_of_files = os.listdir(demand_folder_path)[:number_of_handled_demands]
        list_of_files = sorted(os.listdir(demand_folder_path), key=lambda x: int(x.split('.')[0]))
        list_of_files = list_of_files[:number_of_handled_demands]

        list_of_demands = []

        for file in list_of_files:
            with open(demand_folder_path + fr"\{file}", "r", encoding="utf-8") as f:
                lines = f.readlines()
            source_node = lines[0].rstrip("\n")
            destination_node = lines[1].rstrip("\n")
            bitrate_list = lines[3:]
            demand_no = int(file.rstrip(".txt"))

            bitrate_list = [float(line.replace("\n", "")) for line in bitrate_list]
            # print(source_node)
            # print(destination_node)
            # print(bitrate_list)
            list_of_demands.append(Demand(demand_no, source_node, destination_node, bitrate_list))

        return list_of_demands

    # def interprete_path_file(self, node_list, edge_container):
    #     with open(self.network_topology_file_path, "r", encoding="utf-8") as f:
    #         lines = f.readlines()
    #         for i, line in enumerate(lines):
    #             line = line.rstrip("\n")
    #             lines[i] = line.split("\t")
    #     possible_paths = lines[1:]
    #     edge_counts = [len(node.edges) for node in node_list]
    #
    #     edge_dictionary = {}
    #
    #     node_no = "0"
    #     for i, char in enumerate(line.split("\t")):
    #         edge_dictionary[node_no] =
    #
    #     path_list = []
    #
    #     index = 0
    #     for node in node_list:
    #
    #             for edge in node.edges:
    #
    #                     for i in range(edge_counts[int(node.name)]):
    #
    #
    #         for i in range(0, 30):
    #             possible_path = []
    #             for i, char in enumerate(line.split("\t")):
    #                 if int(char) == 1:





if __name__ == '__main__':
    loader = DataLoader(TYPE.POL12)
    loader.get_demands(0, 1)
