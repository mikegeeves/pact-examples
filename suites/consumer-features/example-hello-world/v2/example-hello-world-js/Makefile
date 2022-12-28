export SHELL:=/bin/bash

.ONESHELL:

.PHONY: cleanup
cleanup:
	# Clean up the linked files, if e.g. node_modules existed already as a dir this won't succeed
	echo "Cleaning up..."
	rm node_modules package.json package-lock.json || echo "Cleanup incomplete!"

.PHONY: test
test:
	function cleanupFn {
		$(MAKE) cleanup
	}
	trap cleanupFn EXIT

	# For running in a docker image, with pre-built node_modules, we just need to link rather than install
	# These files will be present in the /deps dir from the image
	if [ -d "node_modules" ]; then echo "node_modules already exists!"; else ln -s /deps/node_modules/ node_modules; fi
	ln -s /deps/package.json package.json || echo "package.json already exists!"
	ln -s /deps/package-lock.json package-lock.json || echo "package-lock.json already exists!"

	npm run test-mocha
