# France Property Insight: Analysis and Predictions

Online app: <https://gpd-m2sep-france-property-insight.onrender.com/>  
Online documentation: <https://france-property-insight-docs.onrender.com/fpi.html>  
GitLab repository: <https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight>  

Predictive analysis application designed to help owners estimate their properties' values or future buyers to find and predict a property's value in the following years.

The models will use Machine Learning and data from the French "Ministere de l'Économie, des Finances et de l'Industrie".  
Dataset - Demandes de valeurs foncières: <https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/>

## Table of Contents

- [France Property Insight: Analysis and Predictions](#france-property-insight-analysis-and-predictions)
  - [Table of Contents](#table-of-contents)
  - [Installation and Usage](#installation-and-usage)
    - [Method 1 (slower): with Docker Desktop](#method-1-slower-with-docker-desktop)
    - [Method 2 (faster): by installing Python and uv manually](#method-2-faster-by-installing-python-and-uv-manually)
  - [Database](#database)
    - [Data Flow Diagram (DFD)](#data-flow-diagram-dfd)
  - [Repository Structure](#repository-structure)
  - [Current state](#current-state)
    - [Changelog](#changelog)
  - [Workflow](#workflow)
    - [Git Workflow Diagram](#git-workflow-diagram)
  - [Contributors](#contributors)
  - [License](#license)

## Installation and Usage

2 ways to install: with or without Docker.  
The second method, while less reliable because of manual installation of python and uv, is much faster.

### Method 1 (slower): with Docker Desktop

1. Install **Docker Desktop**: From [www.docker.com](https://www.docker.com/products/docker-desktop/)  
Make sure Docker Desktop is **running** before continuing.

2. Clone the Git repository to your local machine and move there:

```bash
git clone https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight.git france-property-insight
cd france-property-insight
```

3. Run our app (caution: first run is slow due to building time):

```bash
docker compose -f .devcontainer/compose.yaml up --build fpi-server
```

### Method 2 (faster): by installing Python and uv manually

1. Install **Python 3.13**: From [Python.org](https://www.python.org/).

2. Install **uv**: From [https://docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).

3. Clone the Git repository to your local machine and move there:

```bash
git clone https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight.git france-property-insight
cd france-property-insight
```

4. Run our app (caution: first run is slow due to building time):

```bash
uv run fpi
```

## Database

Dataset - Demandes de valeurs foncières: <https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/>  

Public official dataset from the French government. Tracks real estate transactions over the French territory from 2020 to 2024.  
More infos (origin, localization, methods, variable glossary...) in docs/metadata-fr.pdf

### Data Flow Diagram (DFD)

<img src="docs/data-flow.png" alt="Data Flow Diagram" width="800"/>

## Repository Structure

- **.devcontainer/** contains Docker setup files

- **data/**
  - **raw/** raw data
  - **cleaned/** validated by Pydantic schemas & cleaned (duplicates, missing values, renaming...)
  - **processed/** ready for analysis, visualization, modeling

- **docs/**
  - **references/** references from teacher and past projects

- **fpi/** contains the python functions and scripts to run our app, analysis and models
  - **analysis/**
  - **data_pipelines/** data import, format conversion, validation, cleaning, filtering
  - **interface/**
  - **models/**
  - **utils/**
  - main.py

- **tests/**
  - **behave/** behave tests
  - **unit/** unit tests

- .gitignore: Prevents unwanted files from being tracked by git.
- .gitlab-ci.yml
- .pre-commit-config.yaml
- .python-version
- pyproject.toml: Project metadata, dependency ranges, and command lines shortcuts (project.scripts).
- README.md: This very same file.
- uv.lock: Lockfile with exact dependency versions for reproducibility.

## Current state

CURRENT STATE: Sprint 1  
This project will go through 5 sprints with reviews and demonstration.

### Changelog

**Sprint 1**

Major changes:

- First explorative data analysis (univariate tests)
- Online documentation
- Store data subset as SQLite .db files (Ile-de-France only) with Git LFS
- Online app
- Web client interface with Gradio
- Deployment with Docker
- gitlab CI setup + runners (mypy, pip-audit, pytest, behave)
- pre-commit setup + ruff (lint and format)

Minor changes:

- uv run shortcuts in .toml scripts
- devcontainer to reproduce dev environment
- Data Flow Diagram
- Git Workflow and branch rules

## Workflow

We protected the main branch, preventing pushing and force pushing.
As such, any feature has to developped separately on its own branch before opening a merge request to the main branch.

### Git Workflow Diagram

<img src="docs/git-mr-workflow.png" alt="Git Workflow Diagram" width="800"/>

The branch staging is a safety layer to test deployment before officially releasing to the main branch.

## Contributors

- Daniel PHAN: Product Owner/Scrum Master
- Perle NDAYIZEYE: Data Analyst
- Kim Ngan THAI: Frontend/UI
- Nicolas COLLIN: Data Engineer
- Claudy LINCY: Data Scientist

This is an academic project for our Master 2 Statistique pour l'Évaluation et la Prévision 2025-2026,  
at the University of Reims Champagne-Ardenne.

## License

This project is licensed under the **MIT License**: you’re free to use, modify, and share it, with attribution and no warranty.
