# whichcat 🐱

Computer vision system to identify and track my two cats in the backyard.

## Architecture

This project follows an MLOps architecture inspired by [ml.school](https://github.com/jbeiroa/ml.school):

- **Framework:** PyTorch
- **Orchestration:** Metaflow
- **Experiment Tracking:** MLflow
- **Deployment:** Amazon SageMaker
- **Dependency Management:** uv
- **Automation:** just

## Project Structure

- `src/data_collection/`: Metaflow pipeline to extract and filter frames from camera recordings.
- `src/training/`: PyTorch model definitions and Metaflow training pipeline.
- `src/inference/`: Live stream processing and alarm system.
- `src/common/`: Shared utilities.

## Getting Started

1. Install `uv` and `just`.
2. Run `just setup` to install dependencies and configure Metaflow.
3. Use `just collect-data` to start gathering images for annotation.
4. Once annotated, use `just train` to fine-tune the model.
5. Use `just track` to run the live identification and alarm system.

## Phases

- **Phase 1:** Extract frames from live feed and filter those with cats using a pre-trained model.
- **Phase 2:** Fine-tune a PyTorch classifier to identify each specific cat and deploy to SageMaker.
- **Phase 3:** Implement live tracking and an alarm system based on movement patterns.
