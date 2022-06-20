
# Language and spec support for each example

For each language and spec version identified, is there a corresponding Makefile within an example folder to run against.
- Yes: Example runs successfully, and generates the expected Pactfile (Consumer), or verifies successfully against the provided Pactfile (Provider)
- -: No example to test found
- Error: Found an example, but the test was unsuccessful

| Example                          | broken<br/>v2   | <br/>v3   | js<br/>v2   | <br/>v3   | python<br/>v2   | <br/>v3   |
|----------------------------------|-----------------|-----------|-------------|-----------|-----------------|-----------|
| **example-consumer-sns**         | -               | -         | -           | -         | -               | ✅ Yes    |
| **example-provider-hello-world** | -               | -         | ✅ Yes      | -         | -               | -         |
