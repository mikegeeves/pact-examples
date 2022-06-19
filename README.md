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

TODO: What to do with spec versions? To an extent "will people care"? It gets very confusing what version is where, e.g.
message is technically v3 but the pact-python current release of 1.5.2 doesn't "support" v3 but does support message.

Each language supported should provide a Dockerfile to build an environment where the Pact tests can be run which will
support that particular spec version. This may mean identical builds for backwards compatibility, or it may diverge as
newer releases remove support for previous functionality (?). Or it may be unhelpful in which case it can be removed!
