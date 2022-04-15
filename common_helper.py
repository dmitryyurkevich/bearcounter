import itertools


def get_from_multilevel_dict(multilevel_dict, key):
    if key in multilevel_dict:
        return multilevel_dict[key]

    for k, v in multilevel_dict.items():
        if isinstance(v, dict):
            value = get_from_multilevel_dict(v, key)
            if value is not None:
                return value


def get_subdicts(**kwargs) -> dict:
    for i in range(len(kwargs)):
        for ks in itertools.combinations(kwargs.keys(), i+1):
            yield {k: kwargs.get(k) for k in ks}


def get_sublists(*args):
    for i in range(len(args)):
        yield from itertools.combinations(args, i+1)

