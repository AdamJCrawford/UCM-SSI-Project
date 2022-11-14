from team import Team
import process_data


# This file contains some of the global variables. This file also does a little
# processing of the data. That probably should be moved to a different file.
PEOPLE = []

NAMES = process_data.get_project_names()
PROJECT_NAMES = NAMES.copy()

data = process_data.get_project_data()
skills = [row[1] for row in data]
unique_identifiers = [row[-1] for row in data]
duplicate_indices = []

# This handles how the teams are numbered. A project that has 2 instances should
# have the same project number so we need to account for all of the duplicate
# projects as projects are getting numbered.
offset = 0
for index, group in enumerate(data):
    if group[0] != 1:
        duplicate_indices.append(index)
    while group[0] != 1:
        PROJECT_NAMES.insert(index + offset, NAMES[index])
        skills.insert(index + offset, data[index][1])
        group[0] -= 1
        offset += 1

LENGTH_PROJECT = len(PROJECT_NAMES)
LENGTH_PEOPLE = 0

offset = 0
TEAMS = []

for i in range(LENGTH_PROJECT):
    if i != 0 and PROJECT_NAMES[i - 1] == PROJECT_NAMES[i]:
        offset += 1
    # This is a very import check to ensure that the length of a list that is supposed
    # to be empty returns 0. ie len(['']) == 1 but len([]) == []
    if skills[i] == ['']:
        skills[i] = []
    TEAMS.append(
        Team(i + 1 - offset, PROJECT_NAMES[i], skills[i], unique_identifiers[i]))

for i in range(len(TEAMS)):
    TEAMS[i].index = i
