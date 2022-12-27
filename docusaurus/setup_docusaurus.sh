#!/bin/sh

. ./.env.colours.sh

if [ ! -d "pact-examples-docusaurus" ]; then
  wcho "- ${BLUE}Creating initial docusaurus installation${SGR0}"
  npx create-docusaurus@latest pact-examples-docusaurus classic
fi


echo "- ${BLUE}Clean out unused files${SGR0}"
rm -Rf pact-examples-docusaurus/blog pact-examples-docusaurus/docs/tutorial* pact-examples-docusaurus/docs/intro.md
rm -f pact-examples-docusaurus/static/img/undraw_docusaurus_tree.svg pact-examples-docusaurus/static/img/undraw_docusaurus_react.svg pact-examples-docusaurus/static/img/undraw_docusaurus_mountain.svg

echo "- ${BLUE}Copy the output from running the examples${SGR0}"
rm -Rf pact-examples-docusaurus/docs/output # Always refresh this
cp -R output pact-examples-docusaurus/docs
cp -R README.md pact-examples-docusaurus/docs/pact-examples.md

echo "- ${BLUE}Replace some of the default docusaurus config with our own${SGR0}"
cp docusaurus/docusaurus.config.js pact-examples-docusaurus/docusaurus.config.js
cp docusaurus/HomepageFeatures/index.js pact-examples-docusaurus/src/components/HomepageFeatures/index.js
cp docusaurus/pages/index.js pact-examples-docusaurus/src/pages/index.js
cp docusaurus/favicon.ico pact-examples-docusaurus/static/img/favicon.ico
