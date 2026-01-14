import math

from EON.ModulationFormat import ModulationFormat


class Supercanal:
    def __init__(self, id, demands):
        self.id = id
        self.demands = demands
        self.selected_path = self.demands[0].selected_path
        self.path_lenght = self.selected_path.path_lenght
        self.bitrate = [f.actual_bitrate for f in self.demands]
        self.merged_bitrate = sum(self.bitrate)
        self.theoritical_bitrate = 0
        self.modulation = None

        self.MODULATION_FORMATS = [
            ModulationFormat("QPSK", 9999999, 200, 6),
            ModulationFormat("8-QAM", 9999999, 400, 9),
            ModulationFormat("16-QAM", 800, 400, 6),
            ModulationFormat("16-QAM", 1600, 600, 9),
            ModulationFormat("32-QAM", 200, 800, 9),
        ]
        self.selected_modulation = None
        self.possible_modulations = self.get_candidates_modulation()


        self.required_slots = 0
        self.number_of_supercanals = 0
        self.number_of_transceivers = 0


        self.selected_slots_idx = []
        self.blocked = True

    def get_candidates_modulation(self):
        candidates_modulation = self.MODULATION_FORMATS
        for modulation in self.MODULATION_FORMATS:
            if self.path_lenght > modulation.max_lenght:
                candidates_modulation.remove(modulation)
        return candidates_modulation


    def select_modulation(self, modulation):
        if modulation in self.possible_modulations:
            self.selected_modulation = modulation
        else:
            raise Exception("Enter valid modulation")
        if self.merged_bitrate < self.selected_modulation.bitrate:
            self.number_of_supercanals = 1
        else:
            self.number_of_supercanals = math.ceil(self.merged_bitrate / self.selected_modulation.bitrate)

        self.required_slots = self.selected_modulation.number_of_slots * self.number_of_supercanals
        self.number_of_transceivers = self.number_of_supercanals * 2

    def select_modulation_with_min_transceivers(self):
        min_transceivers = 999999
        selected_modulation = None
        required_slots = 99999

        for modulation in self.possible_modulations:
            self.select_modulation(modulation)
            if self.number_of_transceivers < min_transceivers:
                min_transceivers = self.number_of_transceivers
                required_slots = self.required_slots
                selected_modulation = modulation
            elif self.number_of_transceivers == min_transceivers:
                if self.required_slots < required_slots:
                    required_slots = self.required_slots
                    selected_modulation = modulation

        self.select_modulation(selected_modulation)
