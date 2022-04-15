import random
import string

from allpairspy import AllPairs
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from enum import Enum

MIN_BEAR_AGE = 0.0
MAX_BEAR_AGE = 50.0
MAX_BEAR_AGE_PRECISION = 1

MIN_BEAR_NAME_LEN = 5
MAX_BEAR_NAME_LEN = 10


class BearType(Enum):
    POLAR = "POLAR"
    BROWN = "BROWN"
    BLACK = "BLACK"
    GUMMY = "GUMMY"

    @property
    def is_real(self):
        return self != BearType.GUMMY

    def __str__(self):
        return self.value


@dataclass_json
@dataclass
class Bear:
    bear_id: int = None
    bear_type: str = field(default_factory=lambda: get_random_bear_type())
    bear_name: str = field(default_factory=lambda: get_random_name())
    bear_age: float = field(default_factory=lambda: get_random_age())

    def set_id(self, bear_id):
        self.bear_id = bear_id
        return self

    def set_type(self, bear_type):
        if isinstance(bear_type, BearType):
            bear_type = bear_type.value
        self.bear_type = bear_type
        return self

    def set_name(self, bear_name):
        self.bear_name = bear_name
        return self

    def set_age(self, bear_age):
        self.bear_age = bear_age
        return self

    @staticmethod
    def get_real():
        real_type = random.choice([t.value for t in BearType if t.is_real])
        return Bear().set_type(bear_type=real_type)

    @staticmethod
    def get_magic():
        real_type = random.choice([t.value for t in BearType if not t.is_real])
        return Bear().set_type(bear_type=real_type)


def get_random_bear_type() -> str:
    return random.choice([bt.value for bt in BearType])


def get_random_name(min_name_len: int = MIN_BEAR_NAME_LEN, max_name_len: int = MAX_BEAR_NAME_LEN) -> str:
    if min_name_len <= 0:
        raise RuntimeError(f"incorrect minimal len value: {max_name_len}")

    name_len = random.randint(min_name_len, max_name_len)
    return "".join(random.choices(string.ascii_uppercase, k=name_len))


def get_random_age(min_age: float = MIN_BEAR_AGE,
                   max_age: float = MAX_BEAR_AGE,
                   precision: int = MAX_BEAR_AGE_PRECISION) -> float:

    if min_age < 0:
        raise RuntimeError(f"incorrect minimal len value: {min_age}")

    return round(random.uniform(min_age, max_age), precision)


def get_pairwise_bear_data():
    names = ("", "TEDDY", "LONG TEDDY")
    ages = (MIN_BEAR_AGE, MAX_BEAR_AGE, (MIN_BEAR_AGE + MAX_BEAR_AGE)/2)
    types = ("POLAR", "BROWN", "BLACK")

    yield from AllPairs(parameters=(names, types, ages))

