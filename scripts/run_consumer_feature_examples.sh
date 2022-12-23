#!/bin/sh

pip -q install testcontainers docker
scripts/run_consumer_feature_examples.py
mdformat ./output
