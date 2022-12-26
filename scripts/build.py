#!/usr/bin/env python3

# Generally, this will be run via a "make build" which in turn calls wrapper script build.sh

import os
import pathlib
import subprocess
import textwrap
from pathlib import Path

from tabulate import tabulate

from shared import LanguagesAndSpecs, RESULT, _get_languages_and_specs, bcolors


def _build_image(language: str, spec: str, dockerfile: Path):
    print(
        f"\n{bcolors.HEADER} - Attempting to build {dockerfile=} for {bcolors.OKBLUE}{language=}{bcolors.HEADER}, {bcolors.OKBLUE}{spec=}{bcolors.ENDC}"
    )
    command = ["docker", "build", ".", "-t", f"pact-examples-{language}-{spec}"]
    print(" ".join(command))
    p = subprocess.run(command, cwd=str(dockerfile.parent))

    colour = bcolors.OKGREEN if p.returncode == 0 else bcolors.FAIL
    print(f"{colour} - Result: {RESULT[p.returncode]}{bcolors.ENDC}")
    return p.returncode


def _build_images(languages_path: pathlib.Path, languages_and_specs: LanguagesAndSpecs) -> list[list[str]]:
    header = ["Language"]
    header.extend(languages_and_specs.specs)
    matrix = [header]
    for language in languages_and_specs.languages:
        spec_results = [f"**{language}**"]
        for spec in languages_and_specs.specs:
            dockerfile = languages_path.joinpath(language).joinpath(spec).joinpath("Dockerfile")
            if dockerfile.is_file():
                result = _build_image(language=language, spec=spec, dockerfile=dockerfile)
                spec_results.append("✅ Yes" if result == 0 else "❌ Error")
            else:
                spec_results.append("-")
        matrix.append(spec_results)
    return matrix


if __name__ == "__main__":
    print(f"{bcolors.HEADER}{bcolors.BOLD}Identifying and building available Docker images{bcolors.ENDC}")
    root_path = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == "scripts" else pathlib.Path.cwd()
    languages_path = root_path.joinpath("languages")

    languages_and_specs = _get_languages_and_specs(languages_path)
    print(f"Found: {languages_and_specs=}")

    print("Attempt to build all available, and create a table of all permutations")
    languages_and_specs_table = _build_images(languages_path, languages_and_specs)

    details = textwrap.dedent(
        """\
        # Language and spec support

        For each language and spec version identified, is there a corresponding Dockerfile to provide an appropriate environment to run against.

        - `Yes`: Dockerfile available and builds successfully
        - `-`: No Dockerfile found
        - `Error`: Dockerfile found, but fails to build successfully

    """
    )
    results = tabulate(languages_and_specs_table, headers="firstrow", tablefmt="github")

    print()
    print(" STORE BELOW IN .MD")
    print("=====================")
    print(details)
    print(results)
    print()
    print("=====================")
    print(" END")

    os.makedirs(root_path.joinpath("output"), exist_ok=True)
    output_path = root_path.joinpath("output").joinpath("build.md")
    print(f"writing to: {output_path=}")
    with open(output_path, "w") as f:
        f.write(details)
        f.write(results)
        f.write("\n")
