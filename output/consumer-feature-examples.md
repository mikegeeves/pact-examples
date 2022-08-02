# Language and spec support for each example

For each language and spec version identified, is there a corresponding Makefile within an example folder to run against.

- `Yes`: Example runs successfully, and generates the expected Pactfile (Consumer), or verifies successfully against the provided Pactfile (Provider)
- `-`: No example to test found
- `Error`: Found an example, but the test was unsuccessful

| Example                                                   | Description                                                                                                            | broken<br/>v2   | <br/>v3   | js<br/>v2   | <br/>v3   | python<br/>v2   | <br/>v3   |
|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|-----------------|-----------|-------------|-----------|-----------------|-----------|
| **[example-consumer-sns](examples/example-consumer-sns)** | This example is a simple example to demonstrate the concept of feature examples, rather than anything specific to SNS! | -               | -         | -           | -         | ❌ Error        | ✅ Yes    |
| **[example-hello-world](examples/example-hello-world)**   | This is a very basic Pact example, demonstrating the simplest use of a Pact Consumer                                   | -               | -         | ✅ Yes      | -         | ✅ Yes          | -         |
| **example-provider-hello-world**                          | No example README.md found                                                                                             | -               | -         | ✅ Yes      | -         | -               | -         |
