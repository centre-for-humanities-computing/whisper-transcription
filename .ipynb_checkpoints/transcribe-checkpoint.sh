#!/bin/bash

# Install dependencies
pip install -r ./700623/requirements.txt

# Run the Python script
python ./700623/whisper_generic_options.py "$@"