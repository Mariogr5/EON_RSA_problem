import math
import random
from collections import Counter
from numba import njit
# usage = Counter(
#     path_id[(i, solution[i])] for i in range(n)
# )

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
            T0=1000.0,
            Tmin=0.1,
            alpha=0.99,
            iters_per_T=100
    ):
        import random, math

        n = len(requests)


        solution = [random.randrange(len(requests[i])) for i in range(n)]
        score = OptimalizationFunctions.grooming_score(solution, requests)
        usage = Counter(
            path_id[(i, solution[i])] for i in range(n)
        )

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

                # old_pid = path_id[(k, old)]
                # new_pid = path_id[(k, new)]

                delta = OptimalizationFunctions.delta_grooming(
                    solution, requests, k, old, new, contains, path_id)
                # + OptimalizationFunctions.delta_concentration(
                    # old_pid, new_pid, usage, weight=0.9)

                if delta > 0 or random.random() < math.exp(delta / T):
                    solution[k] = new
                    score += delta

                    # usage[old_pid] -= 1
                    # usage[new_pid] += 1

                    if score > best_score:
                        best = solution[:]
                        best_score = score

            T *= alpha

        return best, best_score


    @staticmethod
    def simulated_annealing_weighted(
            requests,
            contains,
            path_id,
            blocked_count,
            W=80.0,
            T0=500.0,
            Tmin=0.1,
            alpha=0.70,
            iters_per_T=10
    ):
        import random, math

        n = len(requests)

        # solution = [random.randrange(len(requests[i])) for i in range(n)]
        solution = [0] * n

        blocked, transceivers = blocked_count(solution)
        # grooming = OptimalizationFunctions.grooming_score(
        #     solution, requests
        # )

        score = transceivers - W * blocked
        # score = grooming


        best = solution[:]
        best_score = score

        T = T0

        while T > Tmin:
            for _ in range(iters_per_T):
                k = random.randrange(n)
                old = solution[k]
                new = random.randrange(len(requests[k]))
                # usage = Counter(path_id[(i, solution[i])] for i in range(n))
                #
                # # wybór nowej ścieżki z preferencją już używanych superkanałów
                # if random.random() < 0.7:
                #     used = list(usage.keys())
                #     candidates = [
                #         j for j in range(len(requests[k]))
                #         if path_id[(k, j)] in used and j != old
                #     ]
                #     if candidates:
                #         new = random.choice(candidates)
                #     else:
                #         new = random.randrange(len(requests[k]))
                # else:
                #     new = random.randrange(len(requests[k]))

                if new == old:
                    continue

                solution[k] = new

                new_blocked, new_transceivers = blocked_count(solution)
                # new_grooming = OptimalizationFunctions.delta_grooming(
                #     solution, requests, k, old, new, contains, path_id
                # )

                new_score = new_transceivers - W * new_blocked
                delta = new_score - score

                if delta > 0 or random.random() < math.exp(delta / T):
                    blocked = new_blocked
                    transceivers = new_transceivers
                    score = new_score

                    if score > best_score:
                        best = solution[:]
                        best_score = score
                else:
                    solution[k] = old

            T *= alpha

        return best, transceivers, blocked

