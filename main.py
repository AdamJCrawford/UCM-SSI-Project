from random import shuffle

from person import Person
from team import Team
import config
import process_data
import globals


def swaps(first, second, repeat):
    # The first argument is the score the first person who is going to get has.
    # The second is score we want the first person to have.
    # The third is whether or not we should swap people who would end up with the same ratings after the swap. Example: 2 people on different project both have a 3. If this is a 1 then we should swap them. This is done in an effect in increase the number of swaps that will be done.

    num_swaps = 0
    for team1 in config.TEAMS:
        for member1 in team1.team_members:
            possible_projects = []
            if member1.ratings[team1.index] == first:
                for i, rating in enumerate(member1.ratings):
                    if rating == second:
                        possible_projects.append(
                            sorted(config.TEAMS, key=lambda x: x.team_number)[i])
                cont = True
                for team2 in possible_projects:
                    if cont:
                        for member2 in team2.team_members:
                            if member2.ratings[team1.index] >= member2.ratings[team2.index]:
                                team1.add_teammate(member2)
                                team2.add_teammate(member1)
                                team1.team_members.remove(member1)
                                team2.team_members.remove(member2)
                                if team1.required_skills_copy != team1.recalculate_skills() or team2.required_skills_copy != team2.recalculate_skills():
                                    team1.add_teammate(member1)
                                    team2.add_teammate(member2)
                                    team1.team_members.remove(member2)
                                    team2.team_members.remove(member1)
                                else:
                                    num_swaps += 1
                                    cont = False
                                    break
    if num_swaps:
        # If we did at least 1 swaps then check if we can do more swaps.
        # These swaps increase the avg rating of projects.
        swaps(3, 5, 1)
        swaps(3, 4, 1)
        swaps(3, 5, 1)
        swaps(4, 5, 1)
        if repeat:
            # Increase the chances of swaps happening.
            # These swaps dont increase the avg rating. We swaps a person who has a project they rated a 3 with a different project they rated a 3.
            swaps(5, 5, 0)
            swaps(4, 4, 0)
            swaps(3, 3, 0)


def print_ratings(ratings, avg):
    for i in range(1, 6):
        print(f'{ratings[i - 1]} people got a project they rated a {i}')
    print(f'The average rating is: {avg:.3f}')

# If the student did not enter anything for one of the project rankings assign it a 3.


def process_rankings(rankings):
    for i in range(len(rankings)):
        if rankings[i] == "":
            rankings[i] = 3
        else:
            rankings[i] = int(rankings[i])

# If an email appears twice remove the entries before the last one


def remove_duplicates():
    emails = []
    # Loops through the list backwards as to remove entries before the last one submitted.
    for i in range(len(config.PEOPLE) - 1, -1, -1):
        if config.PEOPLE[i].email not in emails:
            emails.append(config.PEOPLE[i].email)
        else:
            config.PEOPLE.remove(config.PEOPLE[i])


def correct_rankings(rankings):
    duplicates = config.duplicate_indices
    offset = 0
    for index, duplicate in enumerate(duplicates):
        rankings.insert(duplicate + offset, rankings[duplicate + offset])
        offset += 1
    return rankings

# Creates all of the people classes. Before a person class is created I check to make sure
# That the survery was completed. For an intance of the person class to be created you must
# supply a name, an email, the skills they entered, and the ratings they have to the projects
# I also exclude people who did not enter a name or an email.


def generate_people():
    data = process_data.fetch_data()
    for line in data:
        if line[-1] != "" and line[-2] != "":
            process_rankings(line[2])
            rankings = correct_rankings(line[2])
            config.PEOPLE.append(Person(line[-2], line[-1],
                                        line[1], rankings))

    remove_duplicates()
    config.LENGTH_PEOPLE = len(config.PEOPLE)

# Retuns a list of people who have a certain skill


def people_with_skill(people, skill):
    return [person for person in people if skill in person.skills]


def main():
    counter = 0
    current_rating = 5
    generate_people()
    avg_rating = 0

    # This is the loop that runs until the average rating for the project that was assigned
    # is larger than a given value
    while avg_rating <= current_rating:
        counter += 1
        if counter % globals.NUM_ITERATIONS == 0:
            current_rating -= 0.05
        if current_rating < globals.MIN_AVERAGE_TEAM_SCORE:
            current_rating = 5
        avg_rating = 0

       # Need to clear remove previous team member every loop
        for team in config.TEAMS:
            team.clear_team()

        people_copy = config.PEOPLE.copy()
        # All of the code with "restart" is to eliminate someone from getting a project they rated a 2 or 1. If the best we can do is to assign someone to a project they gave a 2 or 1 we need to restart the loop that assigns people.
        restart = False
        # This is the loop that handles skills. It runs 5 times because at most we only
        # assign 5 people to a project
        for i in range(globals.MAX_TEAM_SIZE):
            # Randomize the order of the teams
            shuffle(config.TEAMS)
            for team in config.TEAMS:
                # If there are no more skills needed, pass.
                if len(team.required_skills_copy) == 0:
                    continue
                else:
                    # Creates a list of all of the people who have not been assigned
                    # who posses a skill that the team needs
                    available_people = people_with_skill(
                        people_copy, team.required_skills_copy[0])
                    # Pick a person with the skill who gave the project that highest rating
                    available_people = sorted(
                        available_people, key=lambda x: x.ratings[team.index], reverse=True)

                    # If there are no people with the required skills move the skill
                    # to the back of the list that way we can still search for skills
                    # that come later in the list.
                    if len(available_people) == 0:
                        team.required_skills_copy.append(
                            team.required_skills_copy[0])
                        team.required_skills_copy = team.required_skills_copy[1:]

                    else:
                        # If there is someone who has the skill add the person who has
                        # the highest fitness for that project.
                        if available_people[0].ratings[team.index] > 2:
                            team.add_teammate(available_people[0])
                            people_copy.remove(available_people[0])
                        else:
                            restart = True
                            break
            if restart:
                break
        if restart:
            continue
        # This loop makes sure all of the teams have the minumum number of people.
        for i in range(globals.MIN_TEAM_SIZE):
            shuffle(config.TEAMS)
            for team in config.TEAMS:
                if len(team) >= globals.MIN_TEAM_SIZE:
                    continue
                people_copy = sorted(
                    people_copy, key=lambda x: x.ratings[team.index], reverse=True)
                if people_copy[0].ratings[team.index] > 2:
                    team.add_teammate(people_copy[0])
                    people_copy = people_copy[1:]
                else:
                    restart = True
                    break
            if restart:
                break
        if restart:
            continue
        # This is the loop that fills in the remaining openings in the projects
        # This assignment is based only on the rating they gave the project. In theory
        # all of the projects already have the required skills so taking into account
        # the skills is not necessary.
        while len(people_copy) != 0:
            shuffle(config.TEAMS)
            maxed_teams = True
            for group in config.TEAMS:
                if len(group) < globals.MAX_TEAM_SIZE:
                    maxed_teams = False
                    break
            for team in config.TEAMS:
                if len(people_copy) == 0:
                    break

                if len(team) < globals.MAX_TEAM_SIZE or maxed_teams:
                    people_copy = sorted(
                        people_copy, key=lambda x: x.ratings[team.index], reverse=True)
                    if people_copy[0].ratings[team.index] > 2:
                        team.add_teammate(people_copy[0])
                        people_copy = people_copy[1:]
                    else:
                        restart = True
                        break
            if restart:
                break
        if restart:
            continue

        # Calculate the ratings of the teams and see if it is greater than the
        # threshold.
        ratings = [0, 0, 0, 0, 0]
        for team in config.TEAMS:
            for member in team.team_members:
                for i in range(1, 6):
                    if member.ratings[team.index] == i:
                        ratings[i - 1] += 1
        for i, rating in enumerate(ratings):
            avg_rating += (i + 1) * ratings[i]

        if avg_rating:
            # Swaps that increase the avg_ratings
            swaps(3, 5, 1)
            swaps(3, 4, 1)
            swaps(4, 5, 1)
            for i in range(10):
                # Swaps that dont increase the avg ratings. These swaps swap people with the same ratings in the hopes of having more swaps.
                shuffle(config.TEAMS)
                swaps(5, 5, 0)
                swaps(4, 4, 0)
                swaps(3, 3, 0)
            ratings = [0, 0, 0, 0, 0]
            avg_rating = 0
            for team in config.TEAMS:
                for member in team.team_members:
                    for i in range(1, 6):
                        if member.ratings[team.index] == i:
                            ratings[i - 1] += 1
            for i, rating in enumerate(ratings):
                avg_rating += (i + 1) * ratings[i]
        avg_rating /= config.LENGTH_PEOPLE

    config.TEAMS = sorted(config.TEAMS, key=lambda x: x.team_number)
    print_ratings(ratings, avg_rating)
    # # If there are any projects that don't have all of there needed skills print out
    # # the project and the skill(s) needed

    if globals.PRINT_TEAMS_WITHOUT_SKILLS:
        for team in config.TEAMS:
            if team.required_skills_copy:
                print(team, team.required_skills_copy)

    # Generate the output files
    process_data.fill_files()


if __name__ == "__main__":
    main()
