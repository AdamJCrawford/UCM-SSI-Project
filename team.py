class Team:

    # Creating an instance of Team requires a team number, a team name, and a list
    # of required skills.
    __slots__ = ("team_name", "team_number", "required_skills",
                 "required_skills_copy", "team_members", "index", "skills1", "skills2", "identifier")

    def __init__(self, team_number, team_name, required_skills, identifier):
        self.team_name = team_name
        self.team_number = team_number
        self.required_skills = required_skills
        self.required_skills_copy = required_skills.copy()
        self.team_members = []
        self.index = 0
        self.skills1 = []
        self.skills2 = []
        self.identifier = identifier

    # This handles how a team should be printed.
    def __repr__(self):
        team_names = [self.team_members[i].name for i in range(
            len(self))]
        return f'{self.team_number}, {self.team_name},  {team_names}'
    # This handles what the built-int "len" should return.

    def __len__(self):
        return len(self.team_members)

    # This adds a teammate to the team and removes the skills this person has
    # from the skills that are still required.

    def add_teammate(self, teammate):
        self.team_members.append(teammate)
        for skill in teammate.skills:
            if skill in self.required_skills_copy:
                self.required_skills_copy.remove(skill)

    def clear_team(self):
        # Resets the working list that contains the skills that are still needed
        # and clears the previous team members from this team.
        self.required_skills_copy = self.required_skills.copy()
        self.team_members = []

    def recalculate_skills(self):
        self.skills1 = []
        self.skills2 = []
        for member in self.team_members:
            for skill in member.skills:
                self.skills1.append(skill)
        self.skills1 = list(set(self.skills1))
        for skill in self.required_skills:
            if skill not in self.skills1:
                self.skills2.append(skill)
        return self.skills2
