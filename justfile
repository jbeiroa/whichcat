# whichcat justfile

# Setup the development environment
setup:
    uv sync
    uv run metaflow configure

# Run the data collection flow
collect-data:
    uv run python src/data_collection/flow.py run

# Run the training flow
train:
    uv run python src/training/flow.py run

# Start the live tracking system
track:
    uv run python src/inference/live_tracker.py

# Open the live feed of all cameras
live:
    uv run python scripts/live_viewer.py

# Run tests
test:
    uv run pytest

# Lint the code
lint:
    uv run ruff check .
