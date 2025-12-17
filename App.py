import time
import copy

from EON.Network import Network, TYPE
from OptimalizationFunctions import *

class App:
    def __init__(self):
        self.demands_no = 100
        # self.used_sets = [used_sets_template] * self.demands_no
        self.network = None
        # self.network = Network()
        # self.network.load_data(TYPE.POL12, 1, self.demands_no)
        self.best = []

    def first_fit(self, max_retries):
        rerouting = False
        for demand in self.network.demands:
            demand.selected_path = demand.possible_paths[0]

        demand_copy = copy.deepcopy(self.network.demands)
        edge_list_copy = copy.deepcopy(self.network.edges_container)

        for attempt in range(max_retries):
            self.network.demands = demand_copy
            self.network.edges_container = edge_list_copy
            self.network.reset_slots()
            if rerouting:
                random.shuffle(self.network.demands)
            for i, demand in enumerate(self.network.demands):
                demand_ok = False
                for path in demand.possible_paths:
                    demand.selected_path = path
                    demand.path_lenght = path.path_lenght
                    self.network.check_number_of_groomings_and_mark()
                    self.network.select_modulation_logic()
                    slots_allocation_possible = self.network.allocate_network_slots()
                    network_limitations_possible = self.network.check_limitations()
                    if slots_allocation_possible and network_limitations_possible:
                        demand_ok = True
                        break
                if demand_ok == False:
                    demand.selected_path = demand.possible_paths[0]
                    rerouting = True
                    break
                else:
                    rerouting = False
                    break

            if rerouting == False:
                break

        if rerouting == True:
            return 9999

        transceivers = 0
        for demand in self.network.demands:
            if demand.bitrate_with_gromming != 0:
                transceivers += demand.number_of_transceivers

        return transceivers

    def simulated_annealing_algorithm(self, i, previous_transceivers):

        requests = []
        for demand in self.network.demands:
            paths = OptimalizationFunctions.convert_path(demand.possible_paths)
            requests.append(paths)

        if i == 0 or previous_transceivers == 9999:
            start = time.perf_counter()

            containts, path_id = OptimalizationFunctions.prepare_data(requests)

            best, best_score = OptimalizationFunctions.simulated_annealing_fast(requests, contains=containts,
                                                                                path_id=path_id)

            # best, best_score = OptimalizationFunctions.simulated_annealing(requests)

            self.best = best
            end = time.perf_counter()
            print(f"TIme: {end - start:.6f} s")

        for i, path in enumerate(self.best):
            self.network.demands[i].selected_path = self.network.demands[i].possible_paths[path]

        self.network.check_number_of_groomings_and_mark()
        self.network.select_modulation_logic()
        number_of_transceivers = 0
        for demand in self.network.demands:
            if demand.bitrate_with_gromming != 0:
                # print(f"Demand no:  {demand.demand_no}, Lenght: {demand.path_lenght}, bitrate: {demand.bitrate_with_gromming},"
                #       f" Modulation: {demand.selected_modulation.name},"
                #       f" Groomings: {len(demand.groomings_demands)}, Transceivers: {demand.number_of_transceivers}")
                number_of_transceivers += demand.number_of_transceivers

        # average_number_of_transceivers = math.ceil(number_of_transceivers/ len(self.network.demands))
        # average_number_of_transceivers = number_of_transceivers/ len(self.network.demands)

        average_number_of_transceivers = number_of_transceivers

        possible = self.network.allocate_network_slots()

        possible = self.network.check_limitations()

        if possible:
            return average_number_of_transceivers
        else:
            return 9999

    def iteration_action(self):

        transceivers_list = []
        transceivers = 0
        for i in range(288):

            app.network.reset_slots()
            for demand in self.network.demands:
                demand.set_bitrate(demand.list_of_bitrates[i])
            transceivers_no = app.simulated_annealing_algorithm(i, transceivers)
            transceivers = result
            # transceivers_no = app.first_fit_v2(10)
            transceivers_list.append(transceivers_no)
        transceivers = sum(transceivers_list) / len(transceivers_list)
        return transceivers
        # return math.ceil(transceivers / self.demands_no)


if __name__ == '__main__':
    app = App()

    result = False
    list_of_bitrates = [50]
    for i in range(1):
        app = App()
        app.demands_no = list_of_bitrates[i]
        app.network = Network()
        app.network.load_data(TYPE.US26, 0, app.demands_no)
        app.network.reset_slots()
        print(f"Transceivers {app.iteration_action()}")

