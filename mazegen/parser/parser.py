try:
    from typing import Dict
    from sys import argv
except ImportError as e:
    print(e)
    exit(0)


class ConfigError(Exception):
    """Custom exception for configuration parsing errors."""
    pass


class Data():
    """Holds lists of mandatory and optional configuration keys."""
    mandatory_keys = [
        "width",
        "height",
        "entry",
        "exit",
        "output_file",
        "perfect"
    ]
    bonus_keys = [
        "seed",
        "generative_algorithm",
        "solver_algorithm"
    ]


def get_config_keys(file: str) -> Dict[str, str]:
    """Parse config file content and validate required keys."""
    config = {}
    try:
        config = {key.lower(): value for key, value in
                  (tuple(line.split('=')) for line in file.split('\n')
                   if len(line) != 0)
                  }
    except ValueError:
        raise ConfigError("ERROR: Bad syntax in config file.\n"
                          "Make sure it follows KEY=VALUE")
    error = [key for key in Data.mandatory_keys if
             key not in config.keys()]
    if error:
        raise ConfigError(f"ERROR: Missing mandatory key(s): {error}")
    for key in config.keys():
        if key not in Data.mandatory_keys and key not in Data.bonus_keys:
            error.append(key)
    if error:
        raise ConfigError(f"ERROR: Wrong key name(s): {error}")
    return config


def parse_config() -> Dict[str, str]:
    """Parse configuration from a file specified in command-line arguments."""
    if len(argv) < 2:
        print("No input file")
        exit(0)
    elif len(argv) > 2:
        print("Too many arguments ! Excepted 'a_maze_ing.py' and"
              " 'config_file_name'")
    try:
        file = open(argv[1], 'r')
    except (PermissionError, FileNotFoundError) as e:
        print(f"ERROR: Could not open {argv[1]}: {e.__class__.__name__}")
        exit(0)
    try:
        data = get_config_keys(file.read())
        file.close()
        return data
    except ConfigError as e:
        file.close()
        print(e)
        exit()


def parse_config_from_txt() -> Dict[str, str]:
    """Parse configuration from the default 'config.txt' file."""
    try:
        file = open("config.txt", 'r')
    except (FileNotFoundError, PermissionError) as e:
        print(e)
        exit(0)
    try:
        data = get_config_keys(file.read())
        file.close()
        return data
    except ConfigError as e:
        file.close()
        print(e)
        exit()
