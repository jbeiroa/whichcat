# GEMINI.md - Project Context

## Project Overview
**whichcat** 🐱 is a computer vision and MLOps system designed to identify and track two specific cats in a backyard. The project implements a full lifecycle from data collection to live inference.

- **Architecture:** MLOps pipeline inspired by `ml.school`.
- **Core Technologies:** PyTorch, Metaflow, MLflow, Amazon SageMaker, OpenCV.
- **Dependency Management:** `uv` (Fast Python package installer and resolver).
- **Automation:** `just` (Command runner).

## Project Structure
- `src/common/`: Shared utilities, centralized configuration, and logging.
- `src/data_collection/`: Metaflow flows and extractors for gathering frames from RTSP streams or SD card recordings.
- `src/training/`: PyTorch model definitions and training pipelines orchestrated by Metaflow.
- `src/inference/`: Live stream processing, real-time identification, and alarm logic.
- `scripts/`: General-purpose utility scripts for RTSP testing and live viewing.
- `data/`: Local storage for raw and processed datasets (ignored by Git).
- `frames/`: Directory for frames captured during live tracking or manual snapshots.

## Building and Running
The project uses `just` to automate key tasks.

- **Setup:** `just setup` (Installs dependencies via `uv` and configures Metaflow).
- **Data Collection:** `just collect-data` (Runs the Metaflow collection pipeline).
- **Training:** `just train` (Runs the fine-tuning pipeline).
- **Live Tracking:** `just track` (Runs the live inference and monitoring system).
- **Testing:** `just test` (Executes the `pytest` suite).
- **Linting:** `just lint` (Checks code quality with `ruff`).

## Configuration & Security
- **Environment Variables:** Credentials and camera settings are managed via a `.env` file (see `.env.example` for required fields).
- **Centralized Config:** `src/common/config.py` uses `python-dotenv` to load settings (e.g., `CAMERA_IPS`, `CAMERA_USER`, `CAMERA_PASSWORD`).
- **Sensitive Data:** Never hardcode RTSP URLs or credentials in source files. Always use the centralized config.

## Development Conventions
- **Code Style:** Use `ruff` for linting.
- **Dependencies:** Always use `uv` for adding or syncing packages (e.g., `uv add <package>` or `uv sync`).
- **Scripts:** Place exploratory or diagnostic scripts in the `scripts/` directory.
- **Networking Note:** If encountering "No route to host" errors within the `uv` environment on macOS, tell user to try toggling off and on Local Area Network access for terminal app in System Settings.
- **Logging:** Use the standardized logger from `src/common/logging.py`.
- **Orchestration:** All long-running ML tasks (collection, training) should be implemented as Metaflow `FlowSpec` classes in their respective `src/` subdirectories.

## Current State
- **Phase 1 (Active):** Data collection and RTSP stream verification.
- **Phase 2 (Planned):** Classifier fine-tuning (ResNet18 backbone).
- **Phase 3 (Planned):** Movement pattern analysis and automated alarms.
