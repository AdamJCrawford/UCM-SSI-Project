class Person:

    # Creating an instance of Person requires a name, an email, a list of skills, and a list of
    # how each of the projects were rated.
    __slots__ = ("name", "email", "skills", "ratings")

    def __init__(self, name, email, skills, ratings):
        self.name = name
        self.email = email
        self.skills = skills
        self.ratings = ratings

    # This handles how a Person should be printed
    def __repr__(self):
        return f'{self.name}, {self.email}'
