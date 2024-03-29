# pact-examples

Placeholder for starting a central point to collate Pact examples

The goal is to be able to provide an ongoing set of examples across the various languages, whereby each "feature" can be
demonstrated across each available language.

Where there is no test for a particular "feature", it will then indicate either a test needs to be written or updated to
cover it, or the functionality is not supported.

The reasoning behind trying to collate into a single repo is that it makes it a much lower barrier to entry for making
changes to a test which illustrates a feature. For example if it is found that a test is "incomplete" in demonstrating
behaviour, it would be more feasible for a PR to make minor changes across the various languages, than a developer to
make multiple PRs.

This would hopefully also then lower the barrier to code reviews, since if a PR covers many languages it is more
feasible for a developer to "get the gist" of changes in other languages, if they appear to be correct, for the
languages outside their core skillset.

Currently, it is very unclear exactly how much functionality is provided by the different languages, and if the
implementation is the same, or different (e.g. pact-python message does not appear to be the same as others).

For (potential) maintainers to be able to contribute to fill in gaps, it needs to be understood what is or is not
needed. An example of this is with the FFI implementations, "implement FFI" without understanding of what is needed
requires much time going through implementations in other languages, trying to understand what they do and how they
work.

This provides a framework such that a new "version" can be defined, and functionality implemented in a language as a
reference example. By providing examples of Pacts which a language must be able to be capable of generating to be
compliant (proven by the reference example tests), there is then a checklist to work against of what does or doesn't
work.

## Structure

### Languages

TODO: What to do with spec versions? To an extent "will people care"? It gets very confusing what version is where, e.g.
message is technically v3 but the pact-python current release of 1.5.2 doesn't "support" v3 but does support message.

Each language supported should provide a Dockerfile to build an environment where the Pact tests can be run which will
support that particular spec version. This may mean identical builds for backwards compatibility, or it may diverge as
newer releases remove support for previous functionality (?) (or it may be unhelpful in which case it can be removed!).

Current structure and purpose:

```
- languages
    - broken                <-- the 'language'
        - v3                <-- the spec
            - Dockerfile    <-- the actual Dockerfile to build
    - python
        - v2
            - Dockerfile
        - v3
            - Dockerfile
    - js
        - v2
            - Dockerfile
```

In this case, three Docker images will be built and tagged:

```
- pact-examples-python-v2
- pact-examples-python-v3
- pact-examples-js-v2
```

An additional Dockerfile which _would_ generate `pact-examples-broken-v3` is present, but does not build successfully.

### Examples

- Build all images, and run all the examples: `make examples`
- Run specific test(s) \[TODO: maybe use make and pass params instead?\].
  In this case use the js image(s), for spec v2 only, running all of suite *specs*
  - `./scripts/run_examples.py --suite specs --language js --spec v2`

#### Consumer Features

Each example demonstrating a particular feature \[currently just looking at Pact consumers\], and the expected Pact file
it should generate are contained withing the `Examples` dir.

Current structure and purpose:

```
- Examples
    - consumer-features                              <-- the feature description/name
        - README.md                                  <-- containing details about the feature. TODO: How much info to put here and how to use?
        - example-hello-world                        <-- dir containing the implementation, in this case for python
          - v2                                       <-- the spec version it is for, indicating which spec version of the Docker image to run
            - example-hello-world-python             <-- python implementation
              - Makefile                             <-- containing a 'make test' which will run the tests
            - example-hello-world-js                 <-- js implementation
            - example-hello-world-js-jest-pact       <-- js implementation, 'jest-pact' flavour
            - pacts
                - bearserviceclient-bearservice.json <-- expected pact(s)
```

In this case, `python`, `js` and `js` using `jest-pact` implement this example for spec `v2`. A single `pact` is expected to be generated.

```
TODO: Currently naming with a hardcoded string of `LANGUAGE` which is replaced to verify the pact matches, seems clunky
```

- Each example is expected to contain a `Makefile`, from which a `make test` can be performed using the identified Docker
  image.
- Pact files Pacts are expected to be outputted to `output/pacts` dir within the example dir (mounted via Docker), and will be
  compared against the pact file in the `pacts` dir.

#### Verifier

```
TODO: ruby vs rust, cli, docker, ..maven etc?
```

#### Pact Broker

```
TODO: features such as tags? envs? etc?
```

## Additional generated artifacts

### Docusaurus

Since each example has a single README, it can be shared across the various languages.
This is done by commenting in the README where an expected code block would go,
and then annotating lines marking the start and end of a code block.

In the example README, the annotation looks like:

`<!-- Pact annotated code block - Setting up the Consumer -->` for TypeScript/Javascript, or

`# Pact annotated code block - Setting up the Consumer` for Python

Here, the title of the block is "Setting up the Consumer".

A corresponding code block in python would then look like, for example:

```python
# Pact annotated code block - Setting up the Consumer
pact = Consumer("BearServiceClient").has_pact_with(
    Provider("BearService"),
    host_name=PACT_MOCK_HOST,
    port=PACT_MOCK_PORT,
    pact_dir=PACT_DIR,
    log_dir=LOG_DIR,
)
# End Pact annotated code block
```

When running the examples, .md and .mdx file containing the information, tables,
Tabs etc are generated under output.

For a particular suite, a file will be generated for each test, containing the
annotated blocks where found as well as the Pact files and the diffs between Pact
spec versions.

To build, run examples, and spin up Docusaurus locally to serve the results: `make serve`

For a GitHub build, a pact-examples dir will be created which will contain the docusaurus site to deploy.

### Killercoda

```
TODO:
    Would there be some way to spin up examples for these? Maybe if the README
    was structured in steps? You can generate a structure.json of courses and
    scenarios
```

### Logs

```
TODO:
    It might be helpful to store the log output, maybe not something to commit
    but it could be useful to be able to see how the various logs look like for
    each language run against
```

## Usage

### Languages

To attempt to build the available Docker images for the various languages and spec versions: `make build`

This will additionally generate `output/build.md` containing a matrix of all languages and spec versions found, and if
they can be successfully built or not.

For example, in this case:

| Language   | v2     | v3       |
| ---------- | ------ | -------- |
| **broken** | -      | ❌ Error |
| **js**     | ✅ Yes | -        |
| **python** | ✅ Yes | ✅ Yes   |

### Examples

#### Consumer Features

To attempt to run the provided examples: `make examples`

This will additionally generate `output/examples.md` containing a matrix of all examples against the languages and spec
versions found, and if they match or not.

When running, the `pacts` dir for each example is mapped to a tmp dir, where the pacts can then be compared against the
provided and expected output.

For example, in this case:

| Example                  | Description                                                                                                            | broken<br/>v2 | <br/>v3 | js<br/>v2 | <br/>v3 | python<br/>v2 | <br/>v3 |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------- | ------------- | ------- | --------- | ------- | ------------- | ------- |
| **example-consumer-sns** | This example is a simple example to demonstrate the concept of feature examples, rather than anything specific to SNS! | -             | -       | -         | -       | ❌ Error      | ✅ Yes  |

Here the v2 and v3 pact files expected are identical apart from the version contained in them, where v2 requires v2. As
a result the python v2 fails.

From the logs (TODO: logging levels)

```
Pacts were not identical!
{'values_changed': {"root['metadata']['pactSpecification']['version']": {'new_value': '2.0.0', 'old_value': '3.0.0'}}}
```

### Pre-requisites:

- Currently needing to use Node v14. More recent versions have problems with the
  npx docusaurus.

  For example using nvm: `nvm use lts/fermium`

### TODO:

- Coloured output from Actions directly or via Makefile doesn't work in GitHub currently
- find out where everywhere else outputs pacts to, e.g. python does pacts and (?) for logs, js does pact/pacts and pacts/logs
- how to actually do the build and versions, dependabot? -> How to handle e.g. different JVM branch versions, we kind of want the Pact version to be more fixed and not auto upgrade
