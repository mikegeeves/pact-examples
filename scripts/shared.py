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
    flavours: list[str]


class ExamplesAndSpecs(NamedTuple):
    examples: list[str]
    specs: list[str]


RESULT = {0: "SUCCESS", 1: "ERROR"}


def _get_languages_and_specs(
    languages_path: pathlib.Path, languages=None, specs=None, examples_path=None
) -> LanguagesAndSpecs:
    if not languages:
        # Find the languages, ignoring any directories which end with 'skip'
        languages = sorted(
            [
                pathlib.Path(x).name
                for x in glob.glob(f"{languages_path}/*")
                if os.path.isdir(x) and not pathlib.Path(x).name.endswith("skip")
            ]
        )
    if not specs:
        specs = sorted(set([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*/*") if os.path.isdir(x)]))

    # Try and find any additional flavours, i.e. variations of a language
    # This will find e.g. consumer-features/v2/example-hello-world-js-jest-pact and identify v2-js-jest-pact
    if examples_path:
        flavours = set()
        for spec in specs:
            for language in languages:
                additional_flavours = sorted(
                    set(
                        [
                            f'{spec}-{language}-{pathlib.Path(x).name.split(f"-{language}-")[1]}'
                            for x in glob.glob(f"{examples_path}/*/{spec}/*")
                            if os.path.isdir(x) and f"-{language}-" in x
                        ]
                    )
                )
                for additional_flavour in additional_flavours:
                    flavours.add(additional_flavour)

    else:
        flavours = []
    return LanguagesAndSpecs(languages=languages, specs=specs, flavours=list(flavours))


def _get_examples_and_specs(languages_path: pathlib.Path, examples, specs) -> LanguagesAndSpecs:
    if not examples:
        examples = sorted([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*") if os.path.isdir(x)])
    if not specs:
        specs = sorted(set([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*/*") if os.path.isdir(x)]))

    return LanguagesAndSpecs(examples=examples, specs=specs)
