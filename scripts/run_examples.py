#!/usr/bin/env python3

import glob
import os
import pathlib
import tempfile
import textwrap
from  tempfile import TemporaryDirectory
import docker
from docker.errors import ContainerError, ImageNotFound
from tabulate import tabulate

from shared import LanguagesAndSpecs, ExamplesAndSpecs, _get_languages_and_specs


def _compare_example(tmpdir: TemporaryDirectory, examples_path: pathlib.Path, example:str, spec:str,language:str):
    examples = sorted([pathlib.Path(x).name for x in glob.glob(f"{tmpdir.name}/*")])
    print(f'found examples to compare: {examples=}')

    result = 0
    return result


def _run_example(language: str, spec: str, example_dir: pathlib.Path, tmpdir: TemporaryDirectory):
    print(f'-> _run_example({language=}, {spec=}, {example_dir=}')
    client = docker.from_env()

    image = f"pact-examples-{language}-{spec}"
    try:
        volumes = [f'{example_dir}:/example/', f'{tmpdir.name}:/example/pacts/']
        print(f'going to run {image=} with: {volumes=}')
        container = client.containers.run(
            # remove=True,
            volumes=volumes,
            image=image,
            # environment=envs,
            command=f"sh -c 'cd /example/; make test'",
            tty=True,
            stderr=True,
            stdout=True,
            detach=True
        )
        result = container.wait()['StatusCode']
    except ImageNotFound:
        print(f'Image {image=} does not exist, unable to run')
        result = 1
    except ContainerError as ex:
        print(f'ContainerError: {ex=}, logs: {ex.container.logs()}')

        result = 1
    finally:
        print(f'logs: {container.logs()}')
        container.remove()

    print(f'<- _run_example, returning: {result=}')
    return result


def _run_examples(examples_path: pathlib.Path, languages_and_specs: LanguagesAndSpecs, examples: ExamplesAndSpecs, tmpdir: TemporaryDirectory) -> list[list[str]]:
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
                    result = _run_example(language=language, spec=spec, example_dir=makefile.parent, tmpdir=tmpdir)
                    if result == 0:
                        # If the tests ran, now compare the pact for this example
                        result = _compare_example(tmpdir=tmpdir, examples_path=examples_path, example=example, spec=spec,language=language)
                    example_results.append('✅ Yes' if result == 0 else '❌ Error')
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
    tmpdir = tempfile.TemporaryDirectory()
    print('Attempt to build all available, and create a table of all permutations')
    languages_and_examples_and_specs_table = _run_examples(examples_path, languages_and_specs, examples, tmpdir=tmpdir)

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
