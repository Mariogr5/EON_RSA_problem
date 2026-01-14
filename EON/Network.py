import networkx as nx
from DataPreparation.DataLoader import TYPE, DataLoader
from EON.Edge import Edge
from EON.Node import Node
from EON.Supercanal import Supercanal
from numba import njit

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
            demand.possible_paths = demand.possible_paths[:25]

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
                continue
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

    # @staticmethod
    # def path_is_subset(d1, d2):
    #     """Czy ścieżka d1 zawiera się w ścieżce d2"""
    #     return set(d1.selected_path.edges).issubset(
    #         set(d2.selected_path.edges)
    #     )


    # @staticmethod
    # def is_subpath(p_short, p_long):
    #     """Sprawdza czy p_short jest podścieżką p_long"""
    #     for i in range(len(p_long) - len(p_short) + 1):
    #         if p_long[i:i + len(p_short)] == p_short:
    #             return True
    #     return False

    @staticmethod
    def is_subpath(p_short, p_long):
        edges_short = p_short.edges
        edges_long = p_long.edges

        for i in range(len(edges_long) - len(edges_short) + 1):
            if edges_long[i:i + len(edges_short)] == edges_short:
                return True
        return False

    @staticmethod
    def can_merge(sc1, sc2):
        """Czy superkanały można połączyć topologicznie"""
        if sc1.selected_path == sc2.selected_path:
            return True

        if sc1.path_lenght <= sc2.path_lenght:
            return Network.is_subpath(sc1.selected_path, sc2.selected_path)
        else:
            return Network.is_subpath(sc2.selected_path, sc1.selected_path)

    @staticmethod
    def spectral_gain(sc1, sc2):
        longer_superchannel = None
        if sc1.path_lenght > sc2.path_lenght:
            longer_superchannel = sc1
            shorter_superchannel = sc2
        else:
            longer_superchannel = sc2
            shorter_superchannel = sc1

        sc1.select_modulation_with_min_transceivers()
        sc2.select_modulation_with_min_transceivers()
        slots_before = longer_superchannel.required_slots
        # slots_before = sc1.required_slots + sc2.required_slots


        longer_superchannel.merged_bitrate += shorter_superchannel.merged_bitrate
        longer_superchannel.select_modulation_with_min_transceivers()
        slots_merged = longer_superchannel.required_slots
        longer_superchannel.merged_bitrate -= shorter_superchannel.merged_bitrate

        # path_len = max(sc1.path_lenght, sc2.path_lenght)
        # modulation = select_modulation(path_len)

        # total_bitrate = sum(sc1.bitrate) + sum(sc2.bitrate)

        # slots_merged = required_slots(total_bitrate, modulation)
        # slots_before = (
        #         required_slots(sum(sc1.bitrate), sc1.modulation) +
        #         required_slots(sum(sc2.bitrate), sc2.modulation)
        # )

        return slots_before - slots_merged

    def check_if_allocation_is_possible_sch(self, channel):
        for edge in channel.selected_path.edges:
            for edge_c in self.edges_container:
                if edge is edge_c:
                    for slot in channel.selected_slots_idx:
                        if edge_c.slots[slot] != -1:
                            return False
        return True

    def allocate_slots(self, channel):
        for edge in channel.selected_path.edges:
            for edge_c in self.edges_container:
                if edge is edge_c:
                    for slot in channel.selected_slots_idx:
                        edge_c.slots[slot] = channel.id

    def allocate_network_slots_sch(self, superchannels):

        for channel in superchannels:
            channel_ok = False
            for slot_no in range(320 - channel.required_slots + 1):
                slots = list(range(slot_no, slot_no + channel.required_slots))
                channel.selected_slots_idx = slots
                if self.check_if_allocation_is_possible_sch(channel):
                    self.allocate_slots(channel)
                    channel_ok = True
                    channel.blocked = False
                    break
                if channel_ok == False:
                    channel.selected_slots_idx = []
                    continue

    def allocate_network_slots_sch_best_fit(self, superchannels):

        superchannels.sort(key=lambda d: d.required_slots)

        TOTAL_SLOTS = 320

        for channel in superchannels:
            channel_ok = False
            best_slots = None
            best_cost = float("inf")

            for slot_no in range(TOTAL_SLOTS - channel.required_slots + 1):
                slots = list(range(slot_no, slot_no + channel.required_slots))
                channel.selected_slots_idx = slots

                if self.check_if_allocation_is_possible_sch(channel):
                    channel_ok = True
                    channel.blocked = False
                    # heurystyka kosztu – im mniejszy tym lepiej
                    left_gap = slot_no
                    right_gap = TOTAL_SLOTS - (slot_no + channel.required_slots)
                    cost = left_gap + right_gap

                    if cost < best_cost:
                        best_cost = cost
                        best_slots = slots

            if best_slots is None or not channel:
                channel.selected_slots_idx = []
                continue
            channel.selected_slots_idx = best_slots
            self.allocate_slots(channel)

        return True

    @staticmethod
    def spectrum_aware_merge_fast(superchannels):
        improved = True

        while improved:
            improved = False

            for i, sc1 in enumerate(superchannels):
                best_gain = 0
                best_j = None

                for j, sc2 in enumerate(superchannels):
                    if i == j:
                        continue

                    if not Network.can_merge(sc1, sc2):
                        continue

                    gain = Network.spectral_gain(sc1, sc2)

                    if gain >= best_gain:
                        best_gain = gain
                        best_j = j
                        break

                if best_j is not None:
                    sc2 = superchannels[best_j]

                    new_sc = Supercanal(
                        id=f"{sc1.id}_{sc2.id}",
                        demands=sc1.demands + sc2.demands
                    )

                    new_sc.selected_path = (
                        sc1.selected_path if sc1.path_lenght >= sc2.path_lenght else sc2.selected_path
                    )
                    new_sc.path_lenght = new_sc.selected_path.path_lenght
                    new_sc.select_modulation_with_min_transceivers()

                    for idx in sorted([i, best_j], reverse=True):
                        superchannels.pop(idx)

                    superchannels.append(new_sc)

                    improved = True
                    break  # restart pętli

        return superchannels

    @staticmethod
    def spectrum_aware_merge_faster(superchannels):
        i = 0
        while i < len(superchannels):
            sc1 = superchannels[i]
            merged = False

            j = i + 1
            while j < len(superchannels):
                sc2 = superchannels[j]

                if Network.can_merge(sc1, sc2):
                    gain = Network.spectral_gain(sc1, sc2)

                    if gain >= 0:  # ← zachowujemy spectral_gain
                        # wybór dłuższej ścieżki
                        if sc1.path_lenght >= sc2.path_lenght:
                            selected_path = sc1.selected_path
                        else:
                            selected_path = sc2.selected_path

                        new_sc = Supercanal(
                            id=f"{sc1.id}_{sc2.id}",
                            demands=sc1.demands + sc2.demands
                        )

                        new_sc.selected_path = selected_path
                        new_sc.path_lenght = selected_path.path_lenght
                        new_sc.select_modulation_with_min_transceivers()

                        # zastępujemy sc1, usuwamy sc2
                        superchannels[i] = new_sc
                        superchannels.pop(j)

                        merged = True
                        # i = max(i - 1, 0)
                        break  # 🔴 FIRST-FIT → koniec lokalnego szukania

                j += 1

            if not merged:
                i += 1  # przechodzimy dalej tylko jeśli nie było merge

        return superchannels

