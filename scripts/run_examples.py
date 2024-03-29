#!/usr/bin/env python3
from difflib import unified_diff
from typing import List

import click
import glob
import json
import os
import pathlib
import re
import tempfile
import textwrap
from tempfile import TemporaryDirectory
import time
import docker
import markdown
from bs4 import BeautifulSoup
from deepdiff import DeepDiff
from docker.errors import ContainerError, ImageNotFound
from tabulate import tabulate

from shared import LanguagesAndSpecs, ExamplesAndSpecs, _get_languages_and_specs, bcolors


def _compare_example(tmpdir: TemporaryDirectory, examples_path: pathlib.Path, example: str, spec: str, language: str):
    print(
        f"{bcolors.HEADER}-> _compare_example("
        f"{bcolors.OKBLUE}{language=}{bcolors.HEADER}, "
        f"{bcolors.OKBLUE}{spec=}{bcolors.HEADER}, "
        f"{bcolors.OKBLUE}{example=}{bcolors.HEADER}"
        f"{bcolors.ENDC}"
    )

    examples_to_compare_against = sorted(
        [pathlib.Path(x).name for x in glob.glob(f"{examples_path}/{example}/{spec}/pacts/*")]
    )

    # Start off assuming success until proven otherwise
    result = 0

    if not examples_to_compare_against:
        result = 1
        print(f"{bcolors.WARNING}No Pacts were found in the example to verify against!")

    example_pacts = sorted([pathlib.Path(x).name for x in glob.glob(f"{tmpdir.name}/pacts/*")])
    print(f"Found Pacts generated by tests: {bcolors.OKBLUE}{example_pacts=}{bcolors.ENDC}")

    for example_to_compare_against in examples_to_compare_against:
        print(f"Looking to see if {example_to_compare_against=} is provided by one of {example_pacts=}")

        for example_pact in example_pacts:
            if example_to_compare_against.replace("LANGUAGE", language).lower() in example_pact.lower():
                with open(f"{examples_path}/{example}/{spec}/pacts/{example_to_compare_against}") as json_expected:
                    expected = json.load(json_expected)
                with open(f"{tmpdir.name}/pacts/{example_pact}") as json_actual:
                    actual = json.load(json_actual)

                    # TODO: Big dislike, we have some mangling of the actual to remove to make match due to language/implementation differences
                    # Remove from both actual and expected, if they are present so they don't cause "differences"
                    for data in [actual, expected]:
                        data["metadata"].pop("pact-js", None)
                        data["metadata"].pop("pactRust", None)
                        data["metadata"].pop("pactSpecification", None)

                        # Pact-JS seems to automatically include Content-Type, while Python does not
                        # TODO: What to do about header differences?
                        if "interactions" in data:
                            num_interactions = len(data["interactions"])
                            for interaction in range(num_interactions):
                                data["interactions"][interaction]["response"]["headers"].pop("Content-Type", None)

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
                    print(f"{bcolors.OKBLUE}actual:{bcolors.ENDC}")
                    print(json.dumps(actual, indent=4))
                    print(f"{bcolors.OKBLUE}expected:{bcolors.ENDC}")
                    print(json.dumps(expected, indent=4))
                    result = 1
                else:
                    print(f"{bcolors.OKGREEN}Pacts matched!{bcolors.ENDC}")
                    break
        else:
            result = 1

    colour = bcolors.OKGREEN if result == 0 else bcolors.FAIL
    print(f"{bcolors.HEADER}<- _compare_example, returning:  {colour}{result=}{bcolors.ENDC}")
    return result


def _run_example(language: str, spec: str, example_dir: pathlib.Path, tmpdir: TemporaryDirectory):
    start = time.time()

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
        if container and result != 0:
            print(f"{bcolors.HEADER}Container output{bcolors.ENDC}")
            print(container.logs().decode("unicode_escape"))
            container.remove()

    colour = bcolors.OKGREEN if result == 0 else bcolors.FAIL

    end = time.time()
    duration = end - start
    print(f"{bcolors.HEADER}<- _run_example, {duration=:.1f}s, returning:  {colour}{result=}{bcolors.ENDC}")
    return result


def _extract_first_paragraph(source, example="", suite=""):
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
            description = [x.text for x in list(soup.children) if x.name in ["ul", "p"]][0].replace("\n", "<br/>")

        example_link = f"**[{example}](examples/{suite}/{example})**"
    else:
        description = f"No example README.md found"
        # The README doesn't exist, so don't try to link to it
        example_link = f"**{example}**"

    return description, example_link


def _run_examples(
    suite: str,
    examples_path: pathlib.Path,
    languages_and_specs: LanguagesAndSpecs,
    examples: ExamplesAndSpecs,
) -> list[list[str]]:
    # Construct the header row
    header = ["Example", "Description"]
    for language in languages_and_specs.languages:
        header.append(f"{language}<br/>{languages_and_specs.specs[0]}")

        # Look for any additional variations of a language which have an example
        # This will look for e.g. 'js-v3-jest-pact'
        # and add 'v3-jest-pact' along with the v2, v3 spec
        flavours = [
            x.replace(f"{language}-", "")
            for x in languages_and_specs.flavours
            if x.startswith(f"{languages_and_specs.specs[0]}-{language}-")
        ]
        for flavour in flavours:
            header.append(f"<br/>{flavour}")

        for spec in languages_and_specs.specs[1:]:
            header.append(f"<br/>{spec}")

            # Look for any additional variations of a language which have an example
            # This will look for e.g. 'js-v3-jest-pact'
            # and add 'v3-jest-pact' along with the v2, v3 spec
            flavours = [
                x.replace(f"{language}-", "")
                for x in languages_and_specs.flavours
                if x.startswith(f"{spec}-{language}-")
            ]
            for flavour in flavours:
                header.append(f"<br/>{flavour}")
    matrix = [header]
    for example in examples:
        description_readme = examples_path.joinpath(example).joinpath("README.md")
        description, example_link = _extract_first_paragraph(source=description_readme, suite=suite, example=example)

        example_results = [example_link, description]
        for language in languages_and_specs.languages:
            for spec in languages_and_specs.specs:
                # Possible flavours will be like e.g. -jest-pact
                # Note the leading -, and the default of empty string for no flavour
                possible_flavours = [""] + [
                    x.replace(f"{spec}-{language}", "")
                    for x in languages_and_specs.flavours
                    if x.startswith(f"{spec}-{language}-")
                ]
                makefiles = []
                for flavour in possible_flavours:
                    makefile = (
                        examples_path.joinpath(example)
                        .joinpath(spec)
                        .joinpath(f"{example}-{language}{flavour}")
                        .joinpath("Makefile")
                    )
                    makefiles.append(makefile)

                for makefile in makefiles:
                    if makefile.is_file():
                        tmpdir = tempfile.TemporaryDirectory()
                        result = _run_example(language=language, spec=spec, example_dir=makefile.parent, tmpdir=tmpdir)
                        if result == 0:
                            # If the tests ran, now compare the pact for this example
                            result = _compare_example(
                                tmpdir=tmpdir,
                                examples_path=examples_path,
                                example=example,
                                spec=spec,
                                language=language,
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
                possible_flavours = [""] + [
                    x.replace(f"{spec}-{language}", "")
                    for x in languages_and_specs.flavours
                    if x.startswith(f"{spec}-{language}-")
                ]

                for flavour in possible_flavours:
                    code_blocks[example][spec][f"{language}{flavour}"] = {}

    for example in examples:
        print(f"{bcolors.HEADER}Looking for code blocks relating to: {bcolors.OKBLUE}{example=}{bcolors.ENDC}")
        for spec in languages_and_specs.specs:
            for language in languages_and_specs.languages:
                # Look for any additional variations of a language which have an example
                # Possible flavours will be like e.g. -jest-pact
                # Note the leading -, and the default of empty string for no flavour
                possible_flavours = [""] + [
                    x.replace(f"{spec}-{language}", "")
                    for x in languages_and_specs.flavours
                    if x.startswith(f"{spec}-{language}-")
                ]

                for flavour in possible_flavours:
                    example_language_spec_path = (
                        examples_path.joinpath(example).joinpath(spec).joinpath(f"{example}-{language}{flavour}")
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
                                print("code snippet START")
                                for line in code_snippet.split("\n"):
                                    print(line)
                                print("code snippet END")

                                code_blocks[example][spec][f"{language}{flavour}"][block_name] = code_snippet

    return code_blocks


def _remove_leading_trailing_blank_lines_and_whitespace(block_lines) -> List[str]:
    """Given a List of strings representing lines of text, remove leading/trailing empty lines and leading whitespace padding.

    :param block_lines: Lines to clean
    :return: cleaned block_lines
    """
    # In case the first or last line is empty, remove them
    search = True
    while search:
        if len(block_lines[0].strip()) == 0:
            block_lines = block_lines[1:]
        else:
            search = False
    search = True
    while search:
        if len(block_lines[len(block_lines) - 1].strip()) == 0:
            block_lines.pop()
        else:
            search = False

    # Find the leading whitespace on every line, if any
    lpad = min([len(block_line) - len(block_line.lstrip()) for block_line in block_lines if block_line != ""])

    # Strip leading whitespace
    block_lines = [block_line[lpad:].rstrip() for block_line in block_lines]

    return block_lines


def _generate_example_docs(root_path, examples_path, examples, languages_and_specs, suite):
    print()
    print(f"{bcolors.HEADER}{bcolors.BOLD}Generating example docs{bcolors.ENDC}")
    os.makedirs(root_path.joinpath("output").joinpath("Examples").joinpath(suite), exist_ok=True)

    code_blocks = _scrape_annotated_code_blocks(examples_path, examples, languages_and_specs)
    print("code_blocks:")
    print(json.dumps(code_blocks, indent=4))

    pattern = re.compile("<!-- Annotated code block - (.*) -->")

    for example in examples:
        print(f"{bcolors.HEADER}Example: {example}{bcolors.ENDC}")
        input_path = examples_path.joinpath(example).joinpath("README.md")
        output_path = root_path.joinpath("output").joinpath("Examples").joinpath(suite).joinpath(f"{example}.mdx")
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
                                        output_readme.write(f"```{language.split('-')[0]}")
                                        block_lines = code_blocks[example][spec][language][block_name].split("\n")

                                        block_lines = _remove_leading_trailing_blank_lines_and_whitespace(block_lines)

                                        output_readme.write("\n")
                                        for block_line in block_lines:
                                            output_readme.write(f"{block_line}\n")

                                        output_readme.write("\n```\n")
                                        output_readme.write("</TabItem>\n")

                                        found_any = True

                            if not found_any:
                                output_readme.write(f'<TabItem value="None available" label="None available">\n\n')
                                output_readme.write("TODO: No code snippets available for this section\n")
                                output_readme.write("</TabItem>\n")

                            output_readme.write("</Tabs>\n")

                            # if example in code_blocks:
                            #     output_readme.write(f"found these blocks: {code_blocks[example]}")
                            # else:
                            #     output_readme.write("TODO: No code examples available for this section")
                        else:
                            output_readme.write(line)

                    # Add the contents of the Pact for each spec
                    output_readme.write("\n## Pacts\n\n")
                    output_readme.write("<Tabs>\n")
                    for idx in range(len(languages_and_specs.specs)):
                        spec = languages_and_specs.specs[idx]

                        pacts = [pathlib.Path(x) for x in glob.glob(f"{examples_path}/{example}/{spec}/pacts/*")]

                        output_readme.write(f'<TabItem value="{spec}" label="{spec}">\n\n')
                        if pacts[0].is_file():
                            # Write the contents of the Pact, in a json code block
                            output_readme.write("```json\n")
                            with open(pacts[0], "r") as p:
                                spec_pact_lines = p.readlines()
                                for line in spec_pact_lines:
                                    output_readme.write(line)
                            output_readme.write("```\n")
                        else:
                            output_readme.write(f"None available\n")
                        output_readme.write("</TabItem>\n\n")

                        # If there is another spec after this one, show a diff
                        if idx + 1 < len(languages_and_specs.specs):
                            next_spec = languages_and_specs.specs[idx + 1]

                            next_pacts = [
                                pathlib.Path(x) for x in glob.glob(f"{examples_path}/{example}/{next_spec}/pacts/*")
                            ]
                            if next_pacts[0].is_file():
                                # Read in the next spec
                                with open(next_pacts[0], "r") as p:
                                    next_spec_pact_lines = p.readlines()

                                # Write the diff between the two Pact files in a TabItem
                                output_readme.write(
                                    f'<TabItem value="{spec}-{next_spec} diff" label="{spec}-{next_spec} diff">\n\n'
                                )
                                output_readme.write("```diff\n")
                                output_readme.writelines(
                                    unified_diff(spec_pact_lines, next_spec_pact_lines, fromfile=spec, tofile=next_spec)
                                )
                                output_readme.write("```\n")
                                output_readme.write("</TabItem>\n\n")
                    output_readme.write("</Tabs>\n")


def run_suite(root_path, suites_path, suite, languages=None, specs=None, examples=None):
    print(f"{bcolors.HEADER}{bcolors.BOLD}Attempting to run examples for suite: {bcolors.OKBLUE}{suite}{bcolors.ENDC}")

    examples_path = suites_path.joinpath(suite)

    languages_path = root_path.joinpath("languages")

    languages_and_specs = _get_languages_and_specs(
        languages_path, languages=languages, specs=specs, examples_path=examples_path
    )

    print(f"{bcolors.OKBLUE}{languages_and_specs=}{bcolors.ENDC}")

    if not examples:
        examples = _get_examples(examples_path)
    print(f"Found: {examples=}")

    print("Attempt to build all available, and create a table of all permutations")
    languages_and_examples_and_specs_table = _run_examples(suite, examples_path, languages_and_specs, examples)

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
        f.write("\n")
        f.write(suite_readme_description)
        f.write("\n")
        f.write("\n")
        f.write(results)
        f.write("\n")
        f.write("\n")

    _generate_example_docs(root_path, examples_path, examples, languages_and_specs, suite)


def prepare_output(root_path):
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


@click.command()
@click.option("--suite", default="all", help="Which suite to run, by default all suites will be run")
@click.option("--language", help="Which language to run, multiple may be provided", multiple=True)
@click.option("--spec", help="Which spec to run, multiple may be provided", multiple=True)
@click.option("--example", help="Which example, multiple may be provided", multiple=True)
def main(suite, language, spec, example):
    print(f"{bcolors.HEADER}{bcolors.BOLD}Identifying and running available examples{bcolors.ENDC}")
    root_path = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == "scripts" else pathlib.Path.cwd()

    prepare_output(root_path)

    suites_path = root_path.joinpath("suites")

    if suite != "all":
        suites = [suite]
    else:
        suites = _get_examples(suites_path)

    for suite in suites:
        run_suite(
            root_path=root_path,
            suites_path=suites_path,
            suite=suite,
            languages=list(language),
            specs=list(spec),
            examples=list(example),
        )


if __name__ == "__main__":
    main()
