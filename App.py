import csv
import os
import time
import copy

from EON.Network import Network, TYPE
from OptimalizationFunctions import *
from EON.Supercanal import Supercanal


class App:
    def __init__(self):
        self.demands_no = 100
        self.network = None
        self.best = []
        self.superchannels = []

    def first_fit(self):
        return [0] * self.demands_no

    def calculate_network_sch(self, best):
        buffer_network = copy.deepcopy(self.network)
        for i, path in enumerate(best):
            self.network.demands[i].selected_path = self.network.demands[i].possible_paths[path]

        superchannels = []
        for i, demand in enumerate(self.network.demands):
            superchannels.append(Supercanal(i, [demand]))

        self.network.spectrum_aware_merge_fast(superchannels)

        number_of_transceivers = len(superchannels) * 2

        average_number_of_transceivers = number_of_transceivers

        for channel in superchannels:
            channel.select_modulation_with_min_transceivers()

        self.network.allocate_network_slots_sch(superchannels)

        possible = True
        blocked = 0
        for channel in superchannels:
            if channel.blocked:
                possible = False
                blocked += len(channel.demands)

        # possible = self.network.check_limitations()
        self.network = buffer_network
        return average_number_of_transceivers, blocked

    def simulated_annealing_algorithm(self, i, previous_transceivers):
        requests = []

        if i == 0 or previous_transceivers == 9999:
            for demand in self.network.demands:
                paths = OptimalizationFunctions.convert_path(demand.possible_paths)
                requests.append(paths)
            start = time.perf_counter()
            containts, path_id = OptimalizationFunctions.prepare_data(requests)
            # best, best_score, blocked = OptimalizationFunctions.simulated_annealing_weighted(requests, containts,
            #                                                                                  path_id,
            #                                                                                  self.calculate_network_sch,
            #                                                                                  )
            best, best_score = OptimalizationFunctions.simulated_annealing_fast(requests, contains=containts,
                                                                                path_id=path_id)
            # best = self.first_fit()
            self.best = best
            end = time.perf_counter()
            print(f"TIme: {end - start:.6f} s")

        for i, path in enumerate(self.best):
            self.network.demands[i].selected_path = self.network.demands[i].possible_paths[path]

        superchannels = []
        for i, demand in enumerate(self.network.demands):
            superchannels.append(Supercanal(i, [demand]))

        superchannels = self.network.spectrum_aware_merge_fast(superchannels)

        for channel in superchannels:
            channel.select_modulation_with_min_transceivers()

        number_of_transceivers = len(superchannels) * 2

        average_number_of_transceivers = number_of_transceivers

        # self.network.allocate_network_slots_sch(superchannels)
        self.network.allocate_network_slots_sch_best_fit(superchannels)

        possible = True
        blocked = 0
        for channel in superchannels:
            if channel.blocked:
                possible = False
                blocked += len(channel.demands)

        if possible:
            return average_number_of_transceivers, blocked
        else:
            return average_number_of_transceivers, blocked

    def iteration_action(self):

        transceivers_list = []
        avg_blocked = 0
        transceivers = 0
        for i in range(288):
            network_copy = copy.deepcopy(self.network)
            app.network.reset_slots()
            for demand in self.network.demands:
                demand.set_bitrate(demand.list_of_bitrates[i])
            transceivers_no, blocked_no = app.simulated_annealing_algorithm(i, transceivers)
            transceivers = transceivers_no
            # blocked_no = 0
            # if not possible:
            #     transceivers = 0
            #     for demand in self.network.demands:
            #         if not demand.grooming:
            #             if demand.selected_slots_idx == []:
            #                 blocked_no += len(demand.groomings_demands) + 1
            # i-=1
            # print("Dupa")
            # continue
            # if blocked_no/self.demands_no * 100 > 0.2:
            #     transceivers = 9999
            #     i-=1
            # print(transceivers_no)
            self.print_function(transceivers_no, i, self.demands_no, blocked_no)
            avg_blocked += blocked_no
            transceivers_list.append(transceivers_no)
            self.network = network_copy
        transceivers = sum(transceivers_list) / len(transceivers_list)
        print(f"Average Blocked: {avg_blocked / 288}")
        return transceivers, avg_blocked / 288
        # return math.ceil(transceivers / self.demands_no)

    def print_function(self, transceivers, iteration, demands_no, blocked_no):
        print(
            f"Demands: {demands_no}, Iteration: {iteration}, Blocked: {blocked_no}, Transceivers: {transceivers}")


if __name__ == '__main__':
    app = App()

    file_path_base = r"C:\pythonProject\results"
    file_path = file_path_base + r"\POL12_AG.csv"

    avg_blocked = [0] * 10
    avg_transceivers = [0] * 10
    bitrates_no = 2
    list_of_bitrates = [750, 1000]
    # list_of_bitrates = [500, 750, 1000]

    result = False
    for j in range(1):
        # avg_transceivers = 0
        # list_of_bitrates = [999]
        for i in range(bitrates_no):
            app = App()
            app.demands_no = list_of_bitrates[i]
            app.network = Network()
            app.network.load_data(TYPE.US26, j, app.demands_no)
            app.network.reset_slots()
            transceivers, blocked = app.iteration_action()

            if_file_exists = os.path.isfile(file_path)

            with open(file_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                if not if_file_exists:
                    writer.writerow(["Folder", "Demands_no", "Average_Transceivers", "Average_blocked"])

                writer.writerow([f"demands_{j}", list_of_bitrates[i], transceivers, blocked])

            avg_blocked[i] += blocked
            avg_transceivers[i] += transceivers

    new_avg_blocked = [x / 10 for x in avg_blocked]
    new_avg_transceivers = [x / 10 for x in avg_transceivers]
    for i in range(bitrates_no):
        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([f"Average", list_of_bitrates[i], new_avg_transceivers[i],
                             (new_avg_blocked[i] / list_of_bitrates[i]) * 100])
    # for blocked, transceivers in zip(avg_blocked, avg_transceivers):

    # print(f"Transceivers {app.iteration_action()}")
