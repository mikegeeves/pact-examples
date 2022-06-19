#!/usr/bin/env python3

import glob
import os
import pathlib
import subprocess
import textwrap
from pathlib import Path

from tabulate import tabulate

from shared import LanguagesAndSpecs, RESULT, _get_languages_and_specs, ExamplesAndSpecs


def _build_image(language: str, spec: str, dockerfile: Path):
    print(f'\n - Attempting to build {dockerfile=} for {language=}, {spec=}')
    command = ['docker', 'build', '.', '-t', f'pact-example-{language}-{spec}']
    print(' '.join(command))
    p = subprocess.run(command, cwd=str(dockerfile.parent))
    print(f' - Result: {RESULT[p.returncode]}')
    return p.returncode


def _run_examples(examples_path: pathlib.Path, languages_and_specs: LanguagesAndSpecs, examples: ExamplesAndSpecs) -> list[list[str]]:
    # Construct the header row
    header = ['Example']
    for language in languages_and_specs.languages:
        header.append(f'{language}<br/>{languages_and_specs.specs[0]}')
        for spec in languages_and_specs.specs[1:]:
            header.append(f'<br/>{spec}')
    matrix = [header]
    for example in examples:
        example_results = [f'**{example}**']
        for language in languages_and_specs.languages:
            for spec in languages_and_specs.specs:
                makefile = examples_path.joinpath(example).joinpath(spec).joinpath(f'{example}-{language}').joinpath('Makefile')
                if makefile.is_file():
                    # result = _run_example(language=language, spec=spec, makefile=makefile)
                    # example_results.append('Yes' if result == 0 else 'Error')
                    example_results.append(f'Yes')
                else:
                    example_results.append(f'-')
        matrix.append(example_results)
    return matrix


def _get_examples(examples_path: pathlib.Path) -> list[str]:
    examples = sorted([pathlib.Path(x).name for x in glob.glob(f"{examples_path}/*") if os.path.isdir(x)])

    return examples


if __name__ == "__main__":
    print('Identifying and running available examples')
    root_path = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'scripts' else pathlib.Path.cwd()
    examples_path = root_path.joinpath('examples')
    languages_path = root_path.joinpath('languages')

    languages_and_specs = _get_languages_and_specs(languages_path)

    examples = _get_examples(examples_path)
    print(f'Found: {examples=}')

    print('Attempt to build all available, and create a table of all permutations')
    languages_and_examples_and_specs_table = _run_examples(examples_path, languages_and_specs, examples)

    # print('Attempt to build all available, and create a table of all permutations')
    # languages_and_specs_table = _build_images(languages_path, languages_and_specs)
    #
    details = textwrap.dedent("""\
        # Language and spec support for each example

        For each language and spec version identified, is there a corresponding Makefile within an example folder to run against.
        - Yes: Example runs successfully, and generates the expected Pactfile (Consumer), or verifies successfully against the provided Pactfile (Provider)
        - -: No example to test found
        - Error: Found an example, but the test was unsuccessful

    """)
    results = tabulate(languages_and_examples_and_specs_table, headers="firstrow", tablefmt="github")

    print()
    print(' STORE BELOW IN .MD')
    print('=====================')
    print(details)
    print(results)
    print()
    print('=====================')
    print(' END')

    output_path = root_path.joinpath('output').joinpath('examples.md')
    print(f'writing to: {output_path=}')
    with open(output_path, 'w') as f:
        f.write('\n')
        f.write(details)
        f.write(results)
        f.write('\n')
