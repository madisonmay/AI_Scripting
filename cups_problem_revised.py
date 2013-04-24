from string import ascii_uppercase
from itertools import permutations
from random import randint

'''A script for solving the cup pouring problem.

Problem description:
A player is given n cups, each with a given capacity.
The player needs to produce a given volume of water by
following a simple set of rules. At each time step, the
player can either fill a cup to its maximum volume,
pour out all the water in a cup, or transfer as much water
as possible from one cup to another without overfilling the
recipient cup.
'''


def shortest_path_search(start, successors, is_goal):
    ''' A generic shortest path search algorithm.
    Returns a list of alternating states and actions

    Takes the following arguments:
    start: A tuple representing the starting state
    sucessors: A function that produces the set of
    states than can be reached from a given state
    is_goal: A function that checks to see whether
    the goal state has been reached.
    '''

    # base case: the start state is the goal state
    if is_goal(start):
        return [start]

    # keeps track of visited states
    explored = set()

    # a list of paths that have not yet been followed
    frontier = [[start]]

    # while paths still exist
    while frontier:

        # remove first path from the queue
        # breadth first search - FIFO implementation
        path = frontier.pop(0)

        # each path is a list of states and actions
        # remove the current state from the end of the path
        current_state = path[-1]

        # generate a list of actions and the states
        # reached by taking each action
        for action, state in successors(current_state).items():

            explored.add(current_state)
            if state not in explored:
                # newly found states are added to the frontier
                frontier.append(path + [action, state])

            # function terminates and returns if a solution is found
            # the path returned is always the shortest path
            # because a breadth first search pattern is used
            if is_goal(state):
                return path + [action, state]

    # failure mode: no path can be found
    return []


def cups_problem(max_volumes, start=None, goal=None, print_output=False):
    ''' Returns a list of alternating states and actions that represents
    the shortest path from the start state to the goal state.

    Take the following arguments:
    max_volumes: a tuple of cup sizes
    start: tuple of starting volumes
    goal: a single value representing the desired volume
    '''

    # list of uppercase letters for representing cups
    upper = ascii_uppercase

    # problem generalized to n cups
    n = len(max_volumes)

    # Set start to default of all zeros if no
    # explicit starting configuration is specified.
    if start == None:
        start = tuple([0 for i in range(n)])

    # if no goal is specified, generate a random one.
    if goal == None:
        goal = randint(1, max(max_volumes))

    if print_output:
        # Print statements for a more well struction output
        print 'Goal Volume: ' + str(goal) + '\n'
        for i in range(n):
            print 'Size of cup ' + str(upper[i]) + ': ' + str(max_volumes[i])

        print '\nStarting configuration'
        for i in range(n):
            print 'Cup ' + str(upper[i]) + ': ' + str(start[i])

    def successors(current_volumes):
        '''Returns a dictionary of state/action pairs that can be
        reached from the given configuration of cups.

        Takes the following arguments:
        current_volumes: a tuple of volumes representing the
        amount of water currently in each cup
        '''

        # dictionary for storing action/state pairs
        d = {}

        # the result of filling or emptying any one cup
        for i in range(n):

            # copy current volumes to mutable list
            new_volumes = list(current_volumes)

            # set volume i to max
            new_volumes[i] = max_volumes[i]

            # add action/state pair to dictionary
            # reconvert new_volumes to tuple so it can be hashed
            # in the shortest path search implementation
            d[upper[i] + ' --> max'] = tuple(new_volumes)

            # set volume i to minimum and repeat for the
            # action of emptying any given cup
            new_volumes[i] = 0
            d[upper[i] + ' --> 0'] = tuple(new_volumes)

        # a list of cup indices
        cups = list(range(n))

        # a list of cup pairings
        pairs = permutations(cups, 2)

        # for every permutation of cup pairings
        # add to the dictionary the action of pouring
        # cup1 into cup2 and its resultant state
        for pair in pairs:
            new_volumes = list(current_volumes)

            # cup indices
            cup1 = pair[0]
            cup2 = pair[1]

            # current cup volumes
            volume1 = new_volumes[cup1]
            volume2 = new_volumes[cup2]

            # maximum cup capacities
            capacity1 = max_volumes[cup1]
            capacity2 = max_volumes[cup2]

            # if pouring from cup1 to cup2 would cause overflow,
            # stop pouring when cup2 is full
            if volume1 + volume2 > capacity2:
                new_volumes[cup1] = volume1 - (capacity2 - volume2)
                new_volumes[cup2] = capacity2

            # otherwise, pour the entire contents of cup1 into cup2
            else:
                new_volumes[cup1] = 0
                new_volumes[cup2] = volume1 + volume2

            # cast state to tuple and record action/state pair in dictionary
            d[upper[cup1] + ' --> ' + upper[cup2]] = tuple(new_volumes)

        # return the created dictionary
        return d

    def is_goal(current_volumes):
        '''Checks whether a goal state has been reached.
        Returns a simple boolean (T/F).

        Takes the following arguments:
        current_volumes: a tuple of volumes representing the
        amount of water currently in each cup.
        '''
        return goal in current_volumes

    # apply shortest path search to problem
    shortest_path = shortest_path_search(start, successors, is_goal)

    if print_output:
        # Well structured solution
        print '\nPath to goal:'
        print shortest_path

    return shortest_path

if __name__ == '__main__':
    # Example problem
    cups_problem(max_volumes=(5, 9, 14), print_output=True)
