import math
import random


class OptimalizationFunctions:

    @staticmethod
    def convert_path(possible_paths):

        paths = []

        for path in possible_paths:
            new_path = []
            for edge in path.edges:
                new_path.append(edge.source_node)
                new_path.append(edge.destination_node)
            paths.append(new_path)
        return paths

    @staticmethod
    def is_subpath(shorter, longer):
        n, m = len(shorter), len(longer)
        for i in range(m - n + 1):
            if longer[i:i + n] == shorter:
                return True
        return False

    @staticmethod
    def grooming_score(solution, requests):
        paths = [
            requests[i][solution[i]] for i in range(len(solution))
        ]

        score = 0
        n = len(paths)

        for i in range(n):
            for j in range(i+1,n):
                if i != j and OptimalizationFunctions.is_subpath(paths[i], paths[j]):
                    score += 1

        return score

    @staticmethod
    def simulated_annealing(
            requests,
            T0=100.0,
            Tmin=0.1,
            alpha=0.95,
            iters_per_T=100
    ):
        n = len(requests)

        current = [
            random.randrange(len(requests[i])) for i in range(n)
        ]
        current_score = OptimalizationFunctions.grooming_score(current, requests)

        best = current[:]
        best_score = current_score

        T = T0

        while T > Tmin:
            for _ in range(iters_per_T):
                # generowanie sąsiada
                neighbor = current[:]
                i = random.randrange(n)
                neighbor[i] = random.randrange(len(requests[i]))

                neighbor_score = OptimalizationFunctions.grooming_score(neighbor, requests)
                delta = neighbor_score - current_score

                if delta > 0 or random.random() < math.exp(delta / T):
                    current = neighbor
                    current_score = neighbor_score

                    if current_score > best_score:
                        best = current[:]
                        best_score = current_score

            T *= alpha

        return best, best_score

    @staticmethod
    def prepare_data(requests):
        all_paths = []
        path_id = {}

        for i, paths in enumerate(requests):
            for j, p in enumerate(paths):
                pid = len(all_paths)
                all_paths.append(p)
                path_id[(i, j)] = pid
        M = len(all_paths)
        contains = [[False] * M for _ in range(M)]

        for i in range(M):
            for j in range(M):
                if i != j:
                    contains[i][j] = OptimalizationFunctions.is_subpath(all_paths[i], all_paths[j])
        return contains, path_id

    @staticmethod
    def delta_grooming(solution, requests, k, old_idx, new_idx, contains, path_id):
        delta = 0
        n = len(solution)

        old_pid = path_id[(k, old_idx)]
        new_pid = path_id[(k, new_idx)]

        for i in range(n):
            if i == k:
                continue

            pid_i = path_id[(i, solution[i])]

            # k ⊆ i
            if contains[old_pid][pid_i]:
                delta -= 1
            if contains[new_pid][pid_i]:
                delta += 1

            # i ⊆ k
            if contains[pid_i][old_pid]:
                delta -= 1
            if contains[pid_i][new_pid]:
                delta += 1

        return delta

    @staticmethod
    def simulated_annealing_fast(
            requests,
            contains,
            path_id,
            T0=3000.0,
            Tmin=0.1,
            alpha=0.99,
            iters_per_T=1000
    ):
        import random, math

        n = len(requests)

        solution = [random.randrange(len(requests[i])) for i in range(n)]
        score = OptimalizationFunctions.grooming_score(solution, requests)

        best = solution[:]
        best_score = score

        T = T0

        while T > Tmin:
            for _ in range(iters_per_T):
                k = random.randrange(n)
                old = solution[k]
                new = random.randrange(len(requests[k]))

                if new == old:
                    continue

                delta = OptimalizationFunctions.delta_grooming(
                    solution, requests, k, old, new, contains, path_id
                )

                if delta > 0 or random.random() < math.exp(delta / T):
                    solution[k] = new
                    score += delta

                    if score > best_score:
                        best = solution[:]
                        best_score = score

            T *= alpha

        return best, best_score

