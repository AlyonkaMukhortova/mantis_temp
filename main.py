import dataclasses
import typing
import numpy as np

from mantis.constants import P, M, P_INVERSE
from mantis.utils import permute, int2matrix


def forward_pass(state):
    result = state + state
    result = permute(result.ravel(), P).reshape((4, 4))
    result = M.dot(result)
    result = result + state
    result = permute(result.ravel(), P).reshape((4, 4))
    result = M.dot(result)

    return result


def backward_pass(state):
    result = M.dot(state)
    result = permute(result.ravel(), P_INVERSE).reshape((4, 4))
    result = result + state
    result = M.dot(result)
    result = permute(result.ravel(), P_INVERSE).reshape((4, 4))
    result = result + state

    return result


def backward_pass3(state):
    result = M.dot(state)
    result = permute(result.ravel(), P_INVERSE).reshape((4, 4))
    result = result + state

    return result


def find_zero_intersect(state: np.ndarray[int], states: list[np.ndarray[int]]) -> dict[int, int]:
    results = {}
    for i, s in enumerate(states):
        nz_amount = state.size - np.count_nonzero(s + state)
        if nz_amount > 0:
            results[i] = nz_amount

    return results


def get_all_states_iterator(ncells: int):
    return (int2matrix(i, 1, ncells, 4) for i in range(1, 2 ** ncells))


def number_of_ones(state: np.ndarray[int]) -> int:
    return np.sum(state.ravel())


@dataclasses.dataclass
class State:
    zeros_amount: int
    initial_state: np.ndarray[int]
    final_state: np.ndarray[int]


def main():
    states = get_all_states_iterator(16)
    states_forward = []

    print('--- forward pass:')
    for state in states:
        if number_of_ones(state) < 1:
            continue

        result = forward_pass(state)
        zeros_amount = np.sum(result == 0)

        if zeros_amount > 0:
            states_forward.append(State(zeros_amount, state, result))
            # print(f'state:\n{state}')
            # print(f'result:\n{result}\n')

    states = get_all_states_iterator(16)
    states_backward = []

    print('--- backward pass:')
    for i, state in enumerate(states):
        if number_of_ones(state) < 1:
            continue

        result = backward_pass(state)
        zeros_amount = np.sum(result == 0)

        if zeros_amount > 0:
            indices = find_zero_intersect(result, [s.final_state for s in states_forward])
            if len(indices) > 0:
                for k, v in indices.items():
                    if v > 3:
                        print(v)
                        indices2 = find_zero_intersect(state, [states_forward[k].initial_state])
                        if len(indices2) > 0:
                            if indices2[0] >= 8:
                                print(indices2[0])
                                print(f'state_forward:')
                                print(states_forward[k].initial_state)
                                print(f'state_backward:')
                                print(state)
                                print(v)

    # print(np.max(zeros_amount))


if __name__ == '__main__':
    main()

