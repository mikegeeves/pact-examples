#!/usr/bin/env python3

import glob
import json
import os
import pathlib
import re
import tempfile
import textwrap
from tempfile import TemporaryDirectory
import sys
import docker
import markdown
from bs4 import BeautifulSoup
from deepdiff import DeepDiff
from docker.errors import ContainerError, ImageNotFound
from tabulate import tabulate

from shared import LanguagesAndSpecs, ExamplesAndSpecs, _get_languages_and_specs, bcolors


def _compare_example(tmpdir: TemporaryDirectory, examples_path: pathlib.Path, example: str, spec: str, language: str):
    examples_to_compare_against = sorted(
        [pathlib.Path(x).name for x in glob.glob(f"{examples_path}/{example}/{spec}/pacts/*")]
    )

    example_pacts = sorted([pathlib.Path(x).name for x in glob.glob(f"{tmpdir.name}/pacts/*")])[0]

    result = 0
    for example_to_compare_against in examples_to_compare_against:
        print(f"Looking to see if {example_to_compare_against=} is provided by one of {example_pacts=}")
        if example_to_compare_against.replace("LANGUAGE", language) in example_pacts:
            with open(f"{examples_path}/{example}/{spec}/pacts/{example_to_compare_against}") as json_expected:
                expected = json.load(json_expected)
            with open(f"{tmpdir.name}/pacts/{example_to_compare_against.replace('LANGUAGE', language)}") as json_actual:
                actual = json.load(json_actual)

            expected["consumer"]["name"] = expected["consumer"]["name"].replace("LANGUAGE", language)
            expected["provider"]["name"] = expected["provider"]["name"].replace("LANGUAGE", language)

            # Make request method always upper case
            # This applies for non-message Pacts
            if "interactions" in expected:
                for interaction in expected["interactions"]:
                    interaction["request"]["method"] = interaction["request"]["method"].upper()
                for interaction in actual["interactions"]:
                    interaction["request"]["method"] = interaction["request"]["method"].upper()

            diff = DeepDiff(actual, expected)
            if diff:
                print(f"{bcolors.FAIL}Pacts were not identical!{bcolors.ENDC}")
                print(diff)
                result = 1
            else:
                print(f"{bcolors.OKGREEN}Pacts matched!{bcolors.ENDC}")
        else:
            result = 1
    return result


def _run_example(language: str, spec: str, example_dir: pathlib.Path, tmpdir: TemporaryDirectory):
    print(
        f"{bcolors.HEADER}-> _run_example("
        f"{bcolors.OKBLUE}{language=}{bcolors.HEADER}, "
        f"{bcolors.OKBLUE}{spec=}{bcolors.HEADER}, "
        f"{bcolors.OKBLUE}{example_dir=}{bcolors.HEADER}"
        f"{bcolors.ENDC}"
    )
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
            tmpdir.name: {"bind": "/example/output/", "mode": "rw"},
            example_dir: {"bind": "/example/", "mode": "rw"},
        }
        print(f"going to run {image=} with: {volumes=}")
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
            detach=True,
        )
        result = container.wait()["StatusCode"]
    except ImageNotFound:
        print(f"Image {image=} does not exist, unable to run")
        result = 1
    except ContainerError as ex:
        print(f"ContainerError: {ex=}, logs: {ex.container.logs()}")

        result = 1
    finally:
        if container:
            print(f"logs: {container.logs()}")
            container.remove()

    colour = bcolors.OKGREEN if result == 0 else bcolors.FAIL
    print(f"{bcolors.HEADER}<- _run_example, returning:  {colour}{result=}{bcolors.ENDC}")
    return result


def _extract_first_paragraph(source, example=""):
    """Parse with Beautiful Soup, to extract the FIRST PARAGRAPH from the Markdown

    :param source: Full path to the Markdown file to read and process
    :param example: TODO: How is this used?
    :return: Text from the first paragraph in the Markdown file
    """

    # TODO: Using Markdown and BeautifulSoup seems a bit overkill to pull out something? Something robust is needed though
    if source.is_file():
        with open(source) as f:
            data = f.read()
            md = markdown.Markdown()
            html = md.convert(data)

            soup = BeautifulSoup(html, "html.parser")
            description = [x.text for x in list(soup.children) if x.name == "p"][0]

        example_link = f"**[{example}](examples/{example})**"
    else:
        description = f"No example README.md found"
        # The README doesn't exist, so don't try to link to it
        example_link = f"**{example}**"

    return description, example_link


def _run_examples(
    examples_path: pathlib.Path,
    languages_and_specs: LanguagesAndSpecs,
    examples: ExamplesAndSpecs,
    tmpdir: TemporaryDirectory,
) -> list[list[str]]:
    # Construct the header row
    header = ["Example", "Description"]
    for language in languages_and_specs.languages:
        header.append(f"{language}<br/>{languages_and_specs.specs[0]}")
        for spec in languages_and_specs.specs[1:]:
            header.append(f"<br/>{spec}")
    matrix = [header]
    for example in examples:
        description_readme = examples_path.joinpath(example).joinpath("README.md")
        description, example_link = _extract_first_paragraph(description_readme, example)

        example_results = [example_link, description]
        for language in languages_and_specs.languages:
            for spec in languages_and_specs.specs:
                makefile = (
                    examples_path.joinpath(example)
                    .joinpath(spec)
                    .joinpath(f"{example}-{language}")
                    .joinpath("Makefile")
                )
                if makefile.is_file():
                    result = _run_example(language=language, spec=spec, example_dir=makefile.parent, tmpdir=tmpdir)
                    if result == 0:
                        # If the tests ran, now compare the pact for this example
                        result = _compare_example(
                            tmpdir=tmpdir, examples_path=examples_path, example=example, spec=spec, language=language
                        )
                    example_results.append("✅ Yes" if result == 0 else "❌ Error")
                else:
                    example_results.append(f"-")
        matrix.append(example_results)

    # To have something to populate in the table beyond headers when nothing is found
    if len(matrix) == 1:
        matrix.append(["No examples found!"])

    return matrix


def _get_examples(examples_path: pathlib.Path) -> list[str]:
    examples = sorted([pathlib.Path(x).name for x in glob.glob(f"{examples_path}/*") if os.path.isdir(x)])

    return examples


def _scrape_annotated_code_blocks(examples_path, examples, languages_and_specs):
    extensions = ["py", "js", "ts"]
    excluded_dirs = ["node_modules"]

    # pattern_start = re.compile('(#|//) Pact annotated code block - (.*)\n(.*)End')
    pattern_start = re.compile("(#|//)\s+Pact annotated code block - (.*)")
    pattern_end = re.compile("(#|//)\s+End Pact annotated code block")

    code_blocks = {}

    # Clunky setup dict of dicts
    for example in examples:
        code_blocks[example] = {}
        for spec in languages_and_specs.specs:
            code_blocks[example][spec] = {}
            for language in languages_and_specs.languages:
                code_blocks[example][spec][language] = {}

    for example in examples:
        print(f"{bcolors.HEADER}Looking for code blocks relating to: {bcolors.OKBLUE}{example=}{bcolors.ENDC}")
        for spec in languages_and_specs.specs:
            for language in languages_and_specs.languages:
                example_language_spec_path = (
                    examples_path.joinpath(example).joinpath(spec).joinpath(f"{example}-{language}")
                )
                print(f"{example_language_spec_path=}, exists: {os.path.exists(example_language_spec_path)}")
                if os.path.exists(example_language_spec_path):
                    source_files = []
                    for root, subdirs, files in os.walk(examples_path.joinpath(example_language_spec_path)):
                        # Don't look for e.g. .ts files under the excluded dir node_modules
                        if not any([f"/{exclude}" in root for exclude in excluded_dirs]):
                            source_files.extend(
                                [os.path.join(root, _file) for _file in files if _file.split(".")[-1] in extensions]
                            )
                    print(f"{source_files=}")

                    for source_file in source_files:
                        text = open(source_file).read()
                        matches = pattern_start.finditer(text)
                        for match in matches:
                            block_name = match.group(2)
                            end_of_matching_start_line = match.span()[1]
                            end_block = pattern_end.search(text[end_of_matching_start_line:])
                            start_of_matching_end_line = end_block.span()[0]
                            print(
                                f"{end_block=}, code snippet goes between: {end_of_matching_start_line=} and {end_of_matching_start_line+start_of_matching_end_line}"
                            )
                            code_snippet = text[
                                end_of_matching_start_line : end_of_matching_start_line + start_of_matching_end_line
                            ]
                            print(f"{code_snippet=}")

                            code_blocks[example][spec][language][block_name] = code_snippet

    return code_blocks


def _generate_example_docs(root_path, examples_path, examples, languages_and_specs):
    print()
    print(f"{bcolors.HEADER}{bcolors.BOLD}Generating example docs{bcolors.ENDC}")
    os.makedirs(root_path.joinpath("output").joinpath("examples"), exist_ok=True)

    code_blocks = _scrape_annotated_code_blocks(examples_path, examples, languages_and_specs)
    print(code_blocks)

    pattern = re.compile("<!-- Annotated code block - (.*) -->")

    for example in examples:
        print(f"{bcolors.HEADER}Example: {example}{bcolors.ENDC}")
        input_path = examples_path.joinpath(example).joinpath("README.md")
        output_path = root_path.joinpath("output").joinpath("examples").joinpath(f"{example}.mdx")
        print(f"reading from: {input_path}, writing to: {output_path=}")

        if os.path.exists(input_path):
            with open(input_path, "r") as input_readme:
                with open(output_path, "w") as output_readme:
                    output_readme.write('import Tabs from "@theme/Tabs";\n')
                    output_readme.write('import TabItem from "@theme/TabItem";\n\n')

                    for line in input_readme:
                        block = pattern.match(line)
                        if block:
                            found_any = False
                            block_name = block.group(1)

                            output_readme.write("<Tabs>\n")
                            for spec in code_blocks[example]:
                                for language in code_blocks[example][spec]:
                                    if block_name in code_blocks[example][spec][language]:
                                        output_readme.write(
                                            f'<TabItem value="{language}-{spec}" label="{language}-{spec}">\n\n'
                                        )
                                        output_readme.write(f"```{language}")
                                        output_readme.write(code_blocks[example][spec][language][block_name].rstrip())
                                        output_readme.write("\n```\n")
                                        output_readme.write("</TabItem>\n")

                                        found_any = True

                            if not found_any:
                                output_readme.write(f'<TabItem value="None available" label="None available">\n\n')
                                output_readme.write("TODO: No code snippets available for this example\n")
                                output_readme.write("</TabItem>\n")

                            output_readme.write("</Tabs>\n")

                            # if example in code_blocks:
                            #     output_readme.write(f"found these blocks: {code_blocks[example]}")
                            # else:
                            #     output_readme.write("TODO: No code examples available for this section")
                        else:
                            output_readme.write(line)

        # with open(output_path, 'w') as f:
        #     f.write('\n')
        #     f.write(details)
        #     f.write(results)
        #     f.write('\n')


def run_suite(root_path, suites_path, suite):
    examples_path = suites_path.joinpath(suite)

    languages_path = root_path.joinpath("languages")

    languages_and_specs = _get_languages_and_specs(languages_path)
    print(f"{languages_and_specs=}")

    examples = _get_examples(examples_path)
    print(f"Found: {examples=}")
    tmpdir = tempfile.TemporaryDirectory()
    print("Attempt to build all available, and create a table of all permutations")
    languages_and_examples_and_specs_table = _run_examples(examples_path, languages_and_specs, examples, tmpdir=tmpdir)

    # print('Attempt to build all available, and create a table of all permutations')
    # languages_and_specs_table = _build_images(languages_path, languages_and_specs)
    #

    results = tabulate(languages_and_examples_and_specs_table, headers="firstrow", tablefmt="github")

    print()
    print(" STORE BELOW IN .MD")
    print("=====================")
    print(results)
    print()
    print("=====================")
    print(" END")

    output_path = root_path.joinpath("output").joinpath("examples.md")
    print(f"writing to: {output_path=}")
    with open(output_path, "a") as f:
        suite_readme = suites_path.joinpath(suite).joinpath("README.md")
        suite_readme_description, _ = _extract_first_paragraph(suite_readme)

        f.write(f"## {suite}")
        f.write("\n")
        f.write(suite_readme_description)
        f.write("\n")
        f.write("\n")
        f.write(results)
        f.write("\n")

    _generate_example_docs(root_path, examples_path, examples, languages_and_specs)


def prepare_output():
    """Create the output examples.md file, populating with some header info, so it is ready for the contents of each suite being run."""
    details = textwrap.dedent(
        """\
        # Language and spec support for each example

        For each language and spec version identified, for each suite defined, is there a corresponding Makefile within an example folder to run against.

        - `Yes`: Example runs successfully, and generates the expected Pactfile (Consumer), or verifies successfully against the provided Pactfile (Provider)
        - `-`: No example to test found
        - `Error`: Found an example, but the test was unsuccessful

    """
    )

    print()
    print(" STORE BELOW IN .MD")
    print("=====================")
    print(details)
    print()
    print("=====================")
    print(" END")

    output_path = root_path.joinpath("output").joinpath("examples.md")
    print(f"writing to: {output_path=}")
    with open(output_path, "w") as f:
        f.write(details)
        f.write("\n")


if __name__ == "__main__":
    print(f"{bcolors.HEADER}{bcolors.BOLD}Identifying and running available examples{bcolors.ENDC}")
    root_path = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == "scripts" else pathlib.Path.cwd()

    prepare_output()

    suites_path = root_path.joinpath("suites")

    if len(sys.argv) > 1:
        suites = [sys.argv[1]]
    else:
        suites = _get_examples(suites_path)

    for suite in suites:
        run_suite(root_path, suites_path, suite)
