import enum


class Role(enum.Enum):
    client = 1
    developer = 2
    bot = 4
    moderator = 5
    admin = 8
    superuser = 10
