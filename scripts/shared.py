import glob
import os
import pathlib
from typing import NamedTuple


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class LanguagesAndSpecs(NamedTuple):
    languages: list[str]
    specs: list[str]


class ExamplesAndSpecs(NamedTuple):
    examples: list[str]
    specs: list[str]


RESULT = {0: "SUCCESS", 1: "ERROR"}


def _get_languages_and_specs(languages_path: pathlib.Path) -> LanguagesAndSpecs:
    languages = sorted([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*") if os.path.isdir(x)])
    specs = sorted(set([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*/*") if os.path.isdir(x)]))

    return LanguagesAndSpecs(languages=languages, specs=specs)


def _get_examples_and_specs(languages_path: pathlib.Path) -> LanguagesAndSpecs:
    examples = sorted([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*") if os.path.isdir(x)])
    specs = sorted(set([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*/*") if os.path.isdir(x)]))

    return LanguagesAndSpecs(examples=examples, specs=specs)
