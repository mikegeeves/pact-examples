# About

This contains an uber Javascript image, with all dependencies used by the
various flavours, for example, jest as well as mocha dependencies.

This is to be able to perform the single build of an image, and ensure that
exactly the same libraries and files are available for all tests claiming to be
using the same implementation.

Additionally, if each test installs dependencies that would very quickly result
in a very long build time!

Otherwise, there is a risk of different examples using e.g. different Pact
versions unintentionally, and giving misleading results.

It is possible that there may be conflicts between dependencies, for example on
the Python side, there are many extensions to Flask, which all work well by
themselves, but when trying to combine can result in issues.
Understanding what dependencies cause a conflict and are not possible could be
beneficial.

# Usage

- Add additional dependencies to `package.json`
- `npm install` to update the `package-lock.json`

When rebuilding, Docker will detect the files have changed and rebuild.
