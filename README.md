# pact-examples
Placeholder for starting a central point to collate Pact examples

The goal is to be able to provide an ongoing set of examples across the various languages, whereby each "feature" can be
demonstrated across each available language.

Where there is no test for a particular "feature", it will then indicate either a test needs to be written or updated to
cover it, or the functionality is not supported.

The reasoning behind trying to collate into a single repo is that it makes it a much lower barrier to entry for making
changes to a test. For example if it is found that a test is "incomplete" in demonstrating behaviour, it would be more
feasible for a PR to make minor changes across the various languages, than a developer to make multiple PRs.

This would hopefully also then lower the barrier to code reviews, since if a PR covers many languages it is more
feasible for a developer to "get the gist" of changes in other languages, if they appear to be correct, for the
languages outside their core skillset.


## Structure

### Languages

TODO: What to do with spec versions? To an extent "will people care"? It gets very confusing what version is where, e.g.
message is technically v3 but the pact-python current release of 1.5.2 doesn't "support" v3 but does support message.

Each language supported should provide a Dockerfile to build an environment where the Pact tests can be run which will
support that particular spec version. This may mean identical builds for backwards compatibility, or it may diverge as
newer releases remove support for previous functionality (?) (or it may be unhelpful in which case it can be removed!).

Current structure and purpose:

    - languages
        - broken <- the 'language'
            - v3 <- the spec
                - Dockerfile <- the actual Dockerfile to build
        - python
            - v2
                - Dockerfile
            - v3
                - Dockerfile
        - js
            - v2
                - Dockerfile

In this case, three Docker images will be built and tagged:

    - pact-examples-python-v2
    - pact-examples-python-v3
    - pact-examples-js-v2

An additional Dockerfile which *would* generate `pact-examples-broken-v3` is present, but does not build successfully.

### Examples

Each example demonstrating a particular feature [currently just looking at Pact consumers], and the expected Pact file
it should generate are contained withing the `examples` dir.

Current structure and purpose:

    - examples
        - example-consumer-sns <- the feature description/name
            - v2 <- the spec version it is for, indicating which spec version of the Docker image to run
                - example-consumer-sns-python <- dir containing the implementation, in this case for python
                - pacts
                    - pact-example-consumer-sns-LANGUAGE-pact-example-provider-sns-LANGUAGE.json <- expected pact(s)
            - v3
                - example-consumer-sns-python
                - pacts
                    - pact-example-consumer-sns-LANGUAGE-pact-example-provider-sns-LANGUAGE.json

In this case, only `python` implements this example for spec `v3`. A single `pact` is expected to be generated.

TODO: Currently naming with a hardcoded string of `LANGUAGE` which is replaced to verify the pact matches, seems clunky

Each example is expected to contain a `Makefile`, from which a `make test` can be performed using the identified Docker
image. Pacts are expected to be outputted to the `pacts` dir within the example dir.

## Usage

### Languages

To attempt to build the available Docker images for the various languages and spec versions: `make build`

This will additionally generate `output/build.md` containing a matrix of all languages and spec versions found, and if
they can be successfully built or not.

For example, in this case:

| Language   | v2     | v3       |
|------------|--------|----------|
| **broken** | -      | ❌ Error |
| **js**     | ✅ Yes | -        |
| **python** | ✅ Yes | ✅ Yes   |


### Examples

To attempt to run the provided examples: `make examples`

This will additionally generate `output\examples.md` containing a matrix of all examples against the languages and spec
versions found, and if they match or not.

When running, the `pacts` dir for each example is mapped to a tmp dir, where the pacts can then be compared against the
provided and expected output.

For example, in this case:

| Example                          | broken<br/>v2   | <br/>v3   | js<br/>v2   | <br/>v3   | python<br/>v2   | <br/>v3   |
|----------------------------------|-----------------|-----------|-------------|-----------|-----------------|-----------|
| **example-consumer-sns**         | -               | -         | -           | -         | ❌ Error        | ✅ Yes    |

Here the v2 and v3 pact files expected are identical apart from the version contained in them, where v2 requires v2. As
a result the python v2 fails.
