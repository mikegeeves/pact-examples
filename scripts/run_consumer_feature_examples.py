#!/usr/bin/env python3
from bs4 import BeautifulSoup

import pypandoc
import glob
import json
import os
import pathlib
import tempfile
import textwrap
from tempfile import TemporaryDirectory
import docker
from docker.errors import ContainerError, ImageNotFound
from tabulate import tabulate
from deepdiff import DeepDiff
from shared import LanguagesAndSpecs, ExamplesAndSpecs, _get_languages_and_specs
from mdutils.fileutils.fileutils import MarkDownFile
from docker.types import Mount
import markdown
def _compare_example(tmpdir: TemporaryDirectory, examples_path: pathlib.Path, example: str, spec: str, language: str):
    examples_to_compare_against = sorted([pathlib.Path(x).name for x in glob.glob(f"{examples_path}/{example}/{spec}/pacts/*")])

    example_pacts = sorted([pathlib.Path(x).name for x in glob.glob(f"{tmpdir.name}/pacts/*")])[0]

    result = 0
    for example_to_compare_against in examples_to_compare_against:
        print(f'Looking to see if {example_to_compare_against=} is provided by one of {example_pacts=}')
        if example_to_compare_against.replace('LANGUAGE', language) in example_pacts:
            with open(f"{examples_path}/{example}/{spec}/pacts/{example_to_compare_against}") as json_expected:
                expected = json.load(json_expected)
            with open(f"{tmpdir.name}/pacts/{example_to_compare_against.replace('LANGUAGE', language)}") as json_actual:
                actual = json.load(json_actual)

            expected['consumer']['name'] = expected['consumer']['name'].replace('LANGUAGE', language)
            expected['provider']['name'] = expected['provider']['name'].replace('LANGUAGE', language)

            diff = DeepDiff(actual, expected)
            if diff:
                print('Pacts were not identical!')
                print(diff)
                result = 1
        else:
            result = 1
    return result


def _run_example(language: str, spec: str, example_dir: pathlib.Path, tmpdir: TemporaryDirectory):
    print(f'-> _run_example({language=}, {spec=}, {example_dir=}')
    client = docker.from_env()

    image = f"pact-examples-{language}-{spec}"
    container = None
    try:
        # The Ruby Pact Mock Service seems to get unhappy if it is unable to write a log.
        # Unable to nicely get just a single file from the dir mounted as tmpfs, come back to this one...
        # Couldn't get this to mount:
        # pact_mock_log = f'{tmpdir.name}/pact-mock-service.log'
        # open(pact_mock_log, 'a').close()

        # pact-python message doesn't support specifying the log_dir to output to
        # As a result, we will need the main dir to be writable
        volumes = {
            tmpdir.name: {'bind': '/example/output/', 'mode': 'rw'},
            example_dir: {'bind': '/example/', 'mode': 'rw'},
        }
        print(f'going to run {image=} with: {volumes=}')
        container = client.containers.run(
            # So we don't get mixed up perms and have files we can't delete, use the current uid
            user=os.getuid(),
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
        if container:
            print(f'logs: {container.logs()}')
            container.remove()

    print(f'<- _run_example, returning: {result=}')
    return result


def _run_examples(examples_path: pathlib.Path, languages_and_specs: LanguagesAndSpecs, examples: ExamplesAndSpecs, tmpdir: TemporaryDirectory) -> list[
    list[str]]:
    # Construct the header row
    header = ['Example','Description']
    for language in languages_and_specs.languages:
        header.append(f'{language}<br/>{languages_and_specs.specs[0]}')
        for spec in languages_and_specs.specs[1:]:
            header.append(f'<br/>{spec}')
    matrix = [header]
    for example in examples:
        description_readme = examples_path.joinpath(example).joinpath('README.md')

        # TODO: Using Markdown and BeautifulSoup seems a bit overkill to pull out something? Something robust is needed though
        if description_readme.is_file():
            with open(description_readme) as f:
                data = f.read()
                md = markdown.Markdown()
                html = md.convert(data)

                # Parse with Beautiful Soup
                # This will extract the FIRST PARAGRAPH from the Markdown
                soup = BeautifulSoup(html, 'html.parser')
                description = [x.text for x in list(soup.children) if x.name == 'p'][0]
        else:
            description = f'No example README.md found'
        example_results = [f'**{example}**',description]
        for language in languages_and_specs.languages:
            for spec in languages_and_specs.specs:
                makefile = examples_path.joinpath(example).joinpath(spec).joinpath(f'{example}-{language}').joinpath('Makefile')
                if makefile.is_file():
                    result = _run_example(language=language, spec=spec, example_dir=makefile.parent, tmpdir=tmpdir)
                    if result == 0:
                        # If the tests ran, now compare the pact for this example
                        result = _compare_example(tmpdir=tmpdir, examples_path=examples_path, example=example, spec=spec, language=language)
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
    examples_path = root_path.joinpath('consumer-features')
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

    output_path = root_path.joinpath('output').joinpath('consumer-feature-examples.md')
    print(f'writing to: {output_path=}')
    with open(output_path, 'w') as f:
        f.write('\n')
        f.write(details)
        f.write(results)
        f.write('\n')
