def sps(start, successors, is_goal):
    if is_goal(start):
        return [start]
    explored = set()
    frontier = [ [start] ]
    while frontier:
        path = frontier.pop(0)
        s = path[-1]
        for action, state in successors(s).items():
            explored.add(s)
            if state not in explored:
                frontier.append(path + [action, state])
            if is_goal(state):
                return path + [action, state]
    return []

def successors(state):
    d = {'A --> max': (3, state[1]),
            'B --> max': (state[0], 5),
            'A --> 0': (0, state[1]),
            'B --> 0': (state[0], 0),
            'A --> B': (state[0] - (5-state[1]), 5) if (state[0] + state[1]) > 5 else (0, state[0] + state[1]),
            'B --> A': (3, state[1] - (3-state[0])) if (state[0] + state[1]) > 3 else (state[0] + state[1], 0)}
    return d

def init_goal(goal):

    def is_goal(state):
        return goal in state
    return is_goal

def init_successors(c1, c2):

    def successors(state):
        d = {'A --> max': (c1, state[1]),
                'B --> max': (state[0], c2),
                'A --> 0': (0, state[1]),
                'B --> 0': (state[0], 0),
                'A --> B': (state[0] - (c2-state[1]), c2) if (state[0] + state[1]) > c2 else (0, state[0] + state[1]),
                'B --> A': (c1, state[1] - (c1-state[0])) if (state[0] + state[1]) > c1 else (state[0] + state[1], 0)}
        return d

    return successors

def cups_problem(start, goal):
    is_goal = init_goal(goal)
    successors = init_successors(start[0], start[1])
    return sps(start, successors, is_goal)

if __name__ == '__main__':
    print cups_problem((637,17), 31)
