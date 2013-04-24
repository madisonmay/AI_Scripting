from os import listdir
from re import match
from scheduler import *
import pickle
import itertools
from copy import deepcopy

#checking for redundancy
solutions = set()
result = []

#get list of all files and sort by which were found first
files = listdir('.')
files = sorted([f for f in files if match(r'[0-9]+.p$', f)], key = lambda f: int(f.split('.')[0]))

#keeping track of progress -- there are a lot of permutations
count = 0

f = open('result.p', 'rb')
schedule_set = pickle.load(f)

for solution in schedule_set:

    #progress monitor
    count += 1
    print count, '/', len(schedule_set)

    #check if the solution has already been encountered as a permutation of another solution
    if solution.hashable() in solutions: continue

    #if it hasn't been encountered yet, add to the result list
    boards = [i for i in range(solution.num_boards)]
    permutations = tuple([tuple(p) for p in itertools.permutations(boards)])
    result.append(solution)

    for p in permutations:
        #check for permutations in which boards were played
        new_solution = deepcopy(solution)
        for week in range(solution.num_weeks):
            for i in range(solution.num_boards):
                new_solution.weeks[week].early[i].match = solution.weeks[week].early[p[i]].match
                new_solution.weeks[week].late[i].match = solution.weeks[week].late[p[i]].match
        solutions.add(new_solution.hashable())

        even_newer_solution = deepcopy(new_solution)
        for week in range(solution.num_weeks):
            #early/late reversed and boards permuted
            even_newer_solution.weeks[week].late = new_solution.weeks[week].early
            even_newer_solution.weeks[week].early = new_solution.weeks[week].late
        solutions.add(even_newer_solution.hashable())

#Save result to pickle file
print '\n', len(result), ' unique solutions from ', len(schedule_set), ' solutions'
print '\n', len(solutions), ' permutations checked'

#write string representations to text file
f = open('result9.txt', 'w+')
count = 0
for solution in result:
    count += 1
    f.write('\n\nSolution ' + str(count) + ':\n' + str(solution))
f.close()




