PYTHON_MAJOR_VERSION := 3.9

sgr0 := $(shell tput sgr0)
red := $(shell tput setaf 1)
green := $(shell tput setaf 2)

.PHONY: help
help: ## Show this help message
	@echo "usage: make [target] ..."
	@echo ""
	@echo 'targets:'
	@egrep '^(.+)\:.*##\ (.+)' ${MAKEFILE_LIST} | column -t -c 2 -s ':#'


#==============================================================================
# For setting up pre-commits etc
#==============================================================================
pci: ## Install pre-commit git hook scripts
	@echo "\n$(green)Install pre-commit git hook scripts$(sgr0)"
	pre-commit install
	pre-commit install --hook-type commit-msg # this is for commitizen to work
	pre-commit install --hook-type pre-push # this is for a pytest on push to work

pca: ## Run pre-commit hooks against all the files
	@echo "\n$(green)Run pre-commit hooks against all the files$(sgr0)"
	pre-commit run --all-files

setup: pci pca deps ## Install packages and git hook scripts, and run them
	@echo "\n$(green)Install packages and git hook scripts, and run them$(sgr0)"


#==============================================================================
# For setting up the framework to be able to run the builds and examples
#==============================================================================
deps: ## Install any dependencies for running the examples
	pip install -r requirements.txt

venv: ## Create a pyenv .venv to run in
	@if [ -d "./.venv" ]; then echo "$(red).venv already exists, not continuing!$(sgr0)"; exit 1; fi
	@type pyenv >/dev/null 2>&1 || (echo "$(red)pyenv not found$(sgr0)"; exit 1)

	@echo "\n$(green)Try to find the most recent minor version of the major version specified$(sgr0)"
	$(eval PYENV_VERSION=$(shell pyenv install -l | grep "\s\s$(PYTHON_MAJOR_VERSION)\.*" | tail -1 | xargs))
	@echo "$(PYTHON_MAJOR_VERSION) -> $(PYENV_VERSION)"

	@echo "\n$(green)Install the Python pyenv version if not already available$(sgr0)"
	pyenv install $(PYENV_VERSION) -s

	@echo "\n$(green)Make a .venv dir$(sgr0)"
	~/.pyenv/versions/${PYENV_VERSION}/bin/python3 -m venv ${CURDIR}/.venv

	@echo "\n$(green)Make it 'available' to pyenv$(sgr0)"
	ln -sf ${CURDIR}/.venv ~/.pyenv/versions/${PROJECT}

	@echo "\n$(green)Use it! (populate .python-version)$(sgr0)"
	pyenv local ${PROJECT}


#==============================================================================
# Targets to build the images used and run the various examples
#==============================================================================
build: ## Build the various Docker images
	scripts/build.sh

consumer-feature-examples: deps build ## Run the various Pact Consumer feature examples
	scripts/run_consumer_feature_examples.sh

examples: build consumer-feature-examples ## Run all the examples

serve-docusaurus: examples ## Build the examples then spin up a docker docusaurus, with the output dir available
	@echo "\n${green}Docs will be available under:${sgr0}"
	@echo " - http://localhost:3000/docs/pact-examples"
	@echo " - http://localhost:3000/docs/output/build"
	@echo " - http://localhost:3000/docs/output/consumer-feature-examples"
	@echo
	cd docusaurus && docker-compose up
