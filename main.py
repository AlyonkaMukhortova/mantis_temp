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


def main():
    states = (int2matrix(i, 1, 16, 4) for i in range(1, 2 ** 16))
    good_states = []
    results = []
    zeros_amount = np.zeros(2 ** 16)

    print('--- forward pass:')
    for i, state in enumerate(states):
        if np.sum(state.ravel()) != 4:
            continue

        result = forward_pass(state)
        zeros_amount[i] = np.sum(result == 0)

        if zeros_amount[i] > 0:
            good_states.append(state)
            results.append(result)

            # print(f'state:\n{state}')
            # print(f'result:\n{result}\n')

    states = (int2matrix(i, 1, 16, 4) for i in range(1, 2 ** 16))

    print('--- backward pass:')
    for i, state in enumerate(states):
        if np.sum(state.ravel()) != 5:
            continue

        result = backward_pass(state)
        if np.sum(result == 0) > 0:
            indices = find_zero_intersect(result, results)
            if len(indices) > 0:
                for k, v in indices.items():
                    indices2 = find_zero_intersect(state, [good_states[k]])
                    if len(indices2) > 0:
                        if indices2[0] >= 8:
                            print(indices2[0])
                            print(f'state_forward:')
                            print(good_states[k])
                            print(f'state_backward:')
                            print(state)
                            print(v)

    print(np.max(zeros_amount))


if __name__ == '__main__':
    main()

