# France Property Insight: Analysis and Predictions

Academic project in Master 2 Statistique pour l'Evaluation et la Prevision 2025-2026.

This is a predictive analysis application developped fully in Python to help owners estimate their properties' values or future buyers to find and predict a property's value in the following years.

The predictive models will use Machine Learning and the dataset is from the French "Ministere de l'Economie, des Finances et de l'Industrie".
Dataset used: ["Demandes de valeurs foncieres"](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/)

## Table of Contents

- [France Property Insight: Analysis and Predictions](#france-property-insight-analysis-and-predictions)
  - [Table of Contents](#table-of-contents)
  - [Database](#database)
  - [Data Flow Diagram (DFD)](#data-flow-diagram-dfd)
  - [Repository Structure](#repository-structure)
  - [Installation and Usage](#installation-and-usage)
    - [Method 1: with Docker Desktop](#method-1-with-docker-desktop)
    - [Method 2: by installing Python and uv first](#method-2-by-installing-python-and-uv-first)
  - [Current state](#current-state)
  - [Git Workflow Diagram](#git-workflow-diagram)
  - [Contributors](#contributors)
  - [License](#license)

## Database

Dataset used: [Demandes de valeurs foncieres](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/)

Public official dataset from the French government. Tracks real estate transactions over the French territory from 2020 to 2024.
More infos (origin, localization, methods, variable glossary...) in docs/metadata-fr.pdf

## Data Flow Diagram (DFD)

```mermaid

---
config:
  theme: base
  layout: dagre
---
flowchart BT
 subgraph Frontend["Frontend — User Interaction (Streamlit)"]
        A["User (inputs via Streamlit)"]
        B["Validation Layer (Pydantic)"]
  end
 subgraph Backend["Backend — Core Application Logic"]
        C["Processing Layer (Analysis / Prediction / Visualization)"]
        D["Database Access Layer (SQLAlchemy)"]
  end
 subgraph DataPipeline["Data Preparation Pipeline"]
        E["Raw Data (Demandes de Valeurs Foncières)"]
        F["Validation & Cleaning (Pydantic + Scripts)"]
        G["Filtered Dataset (Analysis-Ready)"]
  end
 subgraph Database["Local Database"]
        H["SQLite Database"]
  end
    E --> F
    F --> G
    G --> H
    A -- User Input (parameters, filters) --> B
    B -- Validated Request --> C
    C -- CRUD / Query Operations --> D
    D -- Interacts with --> H
    H -- Query Results --> D
    D -- Returns Data --> C
    C -- Validated Response --> B
    B -- Displayed Results --> A

```

## Repository Structure

- **data/**
  - **raw/** raw data
  - **validated/** validated by pydantic schemas
  - **cleaned/** cleaned (duplicates, missing values, renaming...)
  - **filtered/** ready for analysis, visualization, modeling

- **docs/**
  - **references/** references from teacher and past projects

- **src/** contains the python functions and scripts to run our app, analysis and models
  - **analysis/**
  - **data_pipelines/** data import, format conversion, validation, cleaning, filtering
  - **interface/**
  - **models/**
  - **utils/**
  - main.py

- **tests/** contains our unit tests made with pytest

- .gitignore: Prevents unwanted files from being tracked by git.
- .python-version
- pyproject.toml: Project metadata, dependency ranges, and command lines shortcuts (project.scripts).
- README.md: This very same file.
- uv.lock: Lockfile with exact dependency versions for reproducibility.

## Installation and Usage

### Method 1: with Docker Desktop

1. Install **Docker Desktop**: From [www.docker.com](https://www.docker.com/products/docker-desktop/)
Make sure Docker Desktop is **running** before continuing.

2. Clone the Git repository to your local machine:

```bash
git clone https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight.git
```

3. Navigate to the cloned directory:

```bash
cd gpd-m2sep-france-property-insight
```

4. Build and run our app (Docker Desktop has to be on):

```bash
docker compose -f .devcontainer/compose.yaml run --rm -it server
```

5. (Optional) To remove all stopped container created by this project:

```bash
docker compose -f .devcontainer/compose.yaml down
```

### Method 2: by installing Python and uv first

1. Install **Python 3.13**: From [Python.org](https://www.python.org/).

2. Install **uv**: From [https://docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).

3. Clone the Git repository to your local machine:

```bash
git clone https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight.git
```

4. Navigate to the cloned directory:

```bash
cd gpd-m2sep-france-property-insight
```

5. Run our app

```bash
uv run main
```

## Current state

CURRENT STATE: Sprint 1
This project will go through 5 sprints with reviews and demonstration.

## Git Workflow Diagram

Noone is allowed to push on main, any development has to be done on a separate branch.
When ready, the features are merged on staging, a clone branch of main used a safety layer, before being merged to main.

```mermaid

---
config:
  layout: elk
  theme: default
title: Merge Request Workflow (feature -> staging -> main)
---
flowchart TD
 subgraph Merge["When feature is ready"]
        D["Clean feature history"]
        E["Rebase staging onto feature"]
        F["Resolve conflicts if any"]
        G["Test staging build"]
        H["Push (--force) staging"]
        I["Open MR: staging → main"]
  end
 subgraph CI["CI pipeline on push / MR"]
    direction TB
        CI1["pre-commit hooks<br>ruff lint & format"]
        CI2["mypy typecheck"]
        CI3["pip-audit dependency checks"]
        CI4["pytest unit & doctests<br>+ behave tests"]
  end
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    CI1 --> CI2
    CI2 --> CI3
    CI3 --> CI4
    Note["staging is a branch clone of main <br>It's a safety layer before merging into main"]
     D:::local
     E:::local
     F:::local
     G:::local
     H:::remote
     I:::remote
     CI1:::ci
     CI2:::ci
     CI3:::ci
     CI4:::ci
     Note:::note
    classDef local fill:#86c0ff,stroke:#004085,color:#004085
    classDef remote fill:#afdeba,stroke:#155724,color:#155724
    classDef ci fill:#fff2cc,stroke:#b58900,color:#8a5d00,font-weight:bold
    classDef note fill:#bdbdbd,stroke:#6c757d,color:#212529,font-weight:bold

```

## Contributors

- Daniel PHAN: Product Owner/Scrum Master
- Perle NDAYIZEYE: Data Analyst
- Kim Ngan THAI: Front End
- Nicolas COLLIN: Data Engineer
- Claudy LINCY: Data Scientist

**HONORABLE MENTIONS**

- Hideo Kojima

## License

This project is licensed under the **MIT License**: you’re free to use, modify, and share it, with attribution and no warranty.
