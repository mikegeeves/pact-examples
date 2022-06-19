#!/usr/bin/env python3
import glob
import os
import pathlib
import subprocess
from pathlib import Path
from typing import NamedTuple

from tabulate import tabulate


class LanguagesAndSpecs(NamedTuple):
    languages: list[str]
    specs: list[str]

RESULT = {
    0: 'SUCCESS',
    1: 'ERROR'
}

def _build_image(language: str, spec: str, dockerfile: Path):
    print(f'\n - Attempting to build {dockerfile=} for {language=}, {spec=}')
    command = ['docker', 'build', '.', '-t',f'pact-example-{language}-{spec}']
    print(' '.join(command))
    p = subprocess.run(command, cwd=str(dockerfile.parent))
    print(f' - Result: {RESULT[p.returncode]}')
    return p.returncode


def _build_images(languages_path: pathlib.Path, languages_and_specs: LanguagesAndSpecs) -> list[list[str]]:
    header = ['Language']
    header.extend(languages_and_specs.specs)
    matrix = [header]
    for language in languages_and_specs.languages:
        spec_results = [language]
        for spec in languages_and_specs.specs:
            dockerfile = languages_path.joinpath(language).joinpath(spec).joinpath('Dockerfile')
            if dockerfile.is_file():
                result = _build_image(language=language, spec=spec, dockerfile=dockerfile)
                spec_results.append('Yes' if result == 0 else 'Error')
            else:
                spec_results.append('No')
        matrix.append(spec_results)
    return matrix


def _get_languages_and_specs(languages_path: pathlib.Path) -> LanguagesAndSpecs:
    languages = sorted([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*") if os.path.isdir(x)])
    specs = sorted(set([pathlib.Path(x).name for x in glob.glob(f"{languages_path}/*/*") if os.path.isdir(x)]))

    return LanguagesAndSpecs(languages=languages, specs=specs)


if __name__ == "__main__":
    print('Identifying and building available Docker images')
    root_path = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'scripts' else pathlib.Path.cwd()
    languages_path = root_path.joinpath('languages')

    languages_and_specs = _get_languages_and_specs(languages_path)
    print(f'Found: {languages_and_specs=}')

    print('Attempt to build all available, and create a table of all permutations')
    languages_and_specs_table = _build_images(languages_path, languages_and_specs)

    print()
    print('=====================')
    print(' STORE BELOW IN .MD')
    print()
    print('# Language and spec support')
    print('For each language and spec version identified, is there a corresponding Dockerfile to provide an appropriate environment to run against.')
    print(' - Yes: Dockerfile available and builds successfully')
    print(' - No: No Dockerfile found')
    print(' - Error: Dockerfile found, but fails to build successfully')
    print()
    print(tabulate(languages_and_specs_table, headers="firstrow", tablefmt="github"))
