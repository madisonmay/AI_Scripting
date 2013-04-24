from itertools import combinations
from copy import deepcopy
import pickle


#Note: an exhaustive search for n = 9 is likely not possible with this implementation,
#however, using a depth-first search generates a reasonable number of solutions
#(a few dozen).  Total number of solutions is probably in the thousands for n = 9,
#since an exhaustive search for n = 5 turned up approx. 250 unique solutions,
#for some definitions of unique.  Unique in this case means that although interchanging
#any player for any other player would not result in a valid solution, only one solution of
#each form is returned.  This script does not currently take into account redundancy introduced by
#switching the early/late sections, or by switching the numbers of the chess boards.  That
#process of removing redundancy is instead handled by redundancy.py

#Solutions are found by placing matches into time slots, and pruning the state tree as often as possible.

def flatten(l):
    #used for hashing function
    out = []
    for item in l:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out

class Player():
    #Player class: handles some pruning conditions
    def __init__(self, id, num_weeks):
        self.id = id
        self.times  = [0, 0]
        self.boards = [0, 0, 0, 0]
        self.weeks = [0 for i in range(num_weeks)]

    def __str__(self):
        return str(self.id)

class Board():
    #Board class: also handles pruning conditions
    def __init__(self, match=None):
        self.match = match
        self.has_match = False

    def __str__(self):
        return str(self.match)

class Week():
    #An array of boards
    def __init__(self, week_number, num_boards):
        self.early = [Board() for i in range(num_boards)]
        self.late = [Board() for i in range(num_boards)]
        self.times = 0
        self.number = week_number

    def __str__(self):
        return 'Early: ' + ', '.join(str(board) for board in self.early) + \
        '\nLate:  ' + ', '.join(str(board) for board in self.late) + '\n'


class Schedule():
    #Container class for a state
    def __init__(self, num_weeks):
        self.num_weeks = num_weeks
        self.num_boards = (num_weeks - 1)/2
        self.weeks = []
        self.matches = []
        self.players = {}
        num_players = num_weeks

        #initialize weeks
        for i in range(num_weeks):
            self.weeks.append(Week(i, self.num_boards))

        #initialize players
        for i in range(num_players):
            self.players[i] = Player(i, num_weeks)

        #initialize matches
        self.matches = [tuple(combo) for combo in combinations([x for x in range(num_players)], 2)]
        self.matches_left = len(self.matches)

    def add_match(self, week, early, board, i=0, match=None):

        #match is passed as argument
        if not match:
            match = self.matches[i]
            self.matches.pop(i)
            self.matches_left -= 1
        #match index is passed as argument
        else:
            i = self.matches.index(match)
            self.matches.pop(i)
            self.matches_left -= 1

        if early:
            #update schedule
            self.weeks[week].early[board].match = match
            self.weeks[week].times += 1
            self.players[match[0]].times[0] += 1
            self.players[match[1]].times[0] += 1
        else:
            #late session
            #update schedule
            self.weeks[week].late[board].match = match
            self.weeks[week].times += 1
            self.players[match[0]].times[1] += 1
            self.players[match[1]].times[1] += 1

        #update player data
        self.players[match[0]].boards[board] += 1
        self.players[match[1]].boards[board] += 1
        self.players[match[0]].weeks[week] += 1
        self.players[match[1]].weeks[week] += 1

        # print str(self) + 'Player times: ', self.players[0].times, self.players[1].times, self.players[2].times, '\n\n'

    def __str__(self):
        return '\n'.join([str(week) for week in self.weeks])# + \
        # "\nUnused Matches:\n" + '\n'.join([str(match) for match in self.matches]) + '\n'

    def hashable(self):

        #returns a tuple of values that represents a state -- used to ensure states are only visited once
        res = []
        for i in range(self.num_weeks):
            res.append((tuple([x.match for x in self.weeks[i].early]), tuple([y.match for y in self.weeks[i].late])))
        return tuple(flatten(res))

def is_goal(schedule):

    #once no more matches need to be placed
    #we can assume success
    if schedule.matches_left == 0:
        return True
    return False

def successors(schedule):
    res = []

    #enclosed in try/except statement to handle the case that position is a solution
    #to the constraints but more paths still exist in the frontier
    #better to ask forgiveness than permission
    try:
        match = schedule.matches[0]
        p1 = schedule.players[match[0]]
        p2 = schedule.players[match[1]]
        num_boards = schedule.num_boards
        for week in schedule.weeks:

            #conditions for a valid position
            #assume that player take a bye on the week corresponding to their number
            if p1.weeks[week.number] or p2.weeks[week.number]: continue

            #each division plays a number of games equal to the number of boards
            if week.times >= num_boards: continue

            #the person with a bye cannot play a match
            if week.number in match: continue

            for time in [0, 1]:

                #each person must have 50% early and 50% late games
                if (p1.times[time] >= num_boards) or (p2.times[time] >= num_boards):
                    continue

                for board in range(num_boards):

                    #each player can play on each board twice
                    if (p1.boards[board] < 2) and (p2.boards[board] < 2):

                        #continue with next iteration of loop if position is filled
                        if time:
                            if schedule.weeks[week.number].late[board].match: continue
                        else:
                            if schedule.weeks[week.number].early[board].match: continue

                        #create copy of schedule to add to branch
                        new_schedule = deepcopy(schedule)
                        new_schedule.add_match(week=week.number, early=(1-time), board=board, i=0)
                        res.append(new_schedule)

    #should be explicit for error catching here
    except:
        pass
    return res

def sps(start, successors, is_goal):
    #A shortest path search implementation

    #Used for keeping track of progress
    record = start.matches_left

    #Resulting solutions stored in res
    res = []

    #Base case
    if is_goal(start):
        return [start]

    #Begin core code of shortest path search
    explored = set()
    frontier = [ [start] ]

    #while some paths still need to be checked
    while frontier:

        #depth first search -- frontier is a stack
        path = frontier.pop()
        s = path[-1]

        count = 0
        #generate next states and iterate
        for state in successors(s):

            #using a set for speed
            explored.add(s.hashable())

            #converting to tuples so hashing can occur
            if (state.hashable()) not in explored:

                #monitoring progress
                if state.matches_left < record:
                    record = state.matches_left
                    print "Distance from solution: ", record, "matches"
                frontier.append(path + [state])

            #handles successfully found solutions
            if is_goal(state):
                count += 1
                res.append(path + [state])

                #pickle and save results in unique files
                f = open(str(count) + '.p', 'wb')
                pickle.dump(state, f)
                f.close()

                #all solutions found
                if len(frontier) == 0:
                    return res
    return res

if __name__ == '__main__':
    n = 9

    #if all solutions are found, write str representations to txt file
    f = open('result' + str(n) + '.txt', 'w+')

    schedule = Schedule(n)
    result = sps(schedule, successors, is_goal)

    #writing to file
    for i in range(len(result)):
        f.write('\n\nSchedule ' + str(i) + ':\n' + str(result[i][-1]))
    f.close()

    #total number of solutions -- does not account for interchangeability of early/late sections








