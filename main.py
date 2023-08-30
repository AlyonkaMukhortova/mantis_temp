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


def main():
    states = (int2matrix(i, 1, 16, 4) for i in range(1, 2 ** 16))
    good_states = []
    results = []
    zeros_amount = np.zeros(2 ** 16)

    print('--- forward pass:')
    for i, state in enumerate(states):
        if np.sum(state.ravel()) < 5:
            continue

        result = forward_pass(state)
        zeros_amount[i] = np.sum(result == 0)

        if zeros_amount[i] > 0:
            good_states.append(state)
            results.append(result)

            # print(f'state:\n{state}')
            # print(f'result:\n{result}\n')

    print('--- backward pass:')
    for result_, state_ in zip(results, good_states):
        result = backward_pass3(state_)

        if np.min(result) == 0:
            if np.min(result + result_) == 0:
                print(f'state:\n{state_}')
                print(f'forward-pass result:\n{result_}')
                print(f'backward-pass result:\n{result}\n')

    print(np.max(zeros_amount))


if __name__ == '__main__':
    main()
