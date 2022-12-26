#!/bin/bash

source .env.colours.sh
echo
echo "${BOLD}${MAGENTA}$0 starting up"

rm -R ./output
mkdir ./output

# Run all suites, or only a single suite if requested
if [ -z "$1" ]
  then
    echo "${BOLD}${MAGENTA}Running all available suites"
    scripts/run_examples.py
else
    echo "${BOLD}${MAGENTA}Running single suite: ${BLUE}$1"
    scripts/run_examples.py "$1"
fi

mdformat ./output
