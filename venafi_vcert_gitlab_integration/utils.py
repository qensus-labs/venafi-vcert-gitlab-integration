import envparse


class AbortException(Exception):
    pass


def check_config_option_set(name, val):
    if val is None:
        raise envparse.ConfigurationError(
            f"'{name}' must be set.")


def check_one_of_two_config_options_set(name1, val1, name2, val2):
    if val1 is not None and val2 is not None:
        raise envparse.ConfigurationError(
            f"Only one of '{name1}' or '{name2}' may be set, but not both.")
    if val1 is None and val2 is None:
        raise envparse.ConfigurationError(
            f"One of '{name1}' or '{name2}' must be set.")


def create_dataclass_inputs_from_env(schema):
    env = envparse.Env(**schema)
    result = {}
    for key in schema.keys():
        result[key.lower()] = env(key)
    return result


def cast_bool(val):
    if val is None:
        return False
    else:
        return str(val).lower() in ('t', 'true', 'yes', 'y', '1', 'on')
