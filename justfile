# whichcat justfile

# Setup the development environment
setup:
    uv sync
    uv run metaflow configure

# Run the data collection flow
collect-data *ARGS:
    PYTHONPATH=. uv run python src/data_collection/flow.py run {{ARGS}}

# Run the training flow
train *ARGS:
    PYTHONPATH=. uv run python src/training/flow.py run {{ARGS}}

# Start the live tracking system
track:
    PYTHONPATH=. uv run python src/inference/live_tracker.py

# Open the live feed of all cameras
live:
    PYTHONPATH=. uv run python scripts/live_viewer.py

# Launch the labeling UI to categorize captured frames
label:
    PYTHONPATH=. uv run python scripts/label_ui.py

# Run tests
test:
    uv run pytest

# Lint the code
lint:
    uv run ruff check .
