# Language and spec support for each example

For each language and spec version identified, for each suite defined, is there a corresponding Makefile within an example folder to run against.

- `Yes`: Example runs successfully, and generates the expected Pactfile (Consumer), or verifies successfully against the provided Pactfile (Provider)
- `-`: No example to test found
- `Error`: Found an example, but the test was unsuccessful

## consumer-features

This suite contains basic tests to demonstrate consumer features

| Example                                                   | Description                                                                                                            | broken<br/>v2   | <br/>v3   | js<br/>v2   | <br/>v3   | python<br/>v2   | <br/>v3   |
|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|-----------------|-----------|-------------|-----------|-----------------|-----------|
| **[example-consumer-sns](examples/example-consumer-sns)** | This example is a simple example to demonstrate the concept of feature examples, rather than anything specific to SNS! | -               | -         | -           | -         | ❌ Error        | ✅ Yes    |
| **[example-hello-world](examples/example-hello-world)**   | This is a very basic Pact example, demonstrating the simplest use of a Pact Consumer                                   | -               | -         | ❌ Error    | ✅ Yes    | ❌ Error        | -         |
| **example-provider-hello-world**                          | No example README.md found                                                                                             | -               | -         | ✅ Yes      | -         | -               | -         |

## term

This suite contains basic tests to demonstrate the example Term matchers provided in each language, illustrating any
differences.

| Example                  | Description                | broken<br/>v2   | <br/>v3   | js<br/>v2   | <br/>v3   | python<br/>v2   | <br/>v3   |
|--------------------------|----------------------------|-----------------|-----------|-------------|-----------|-----------------|-----------|
| **example-date**         | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-decimal**      | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-hexadecimal**  | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-identifier**   | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-integer**      | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-ip_address**   | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-ipv6_address** | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-time**         | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-timestamp**    | No example README.md found | -               | -         | -           | -         | -               | -         |
| **example-uuid**         | No example README.md found | -               | -         | -           | -         | -               | -         |