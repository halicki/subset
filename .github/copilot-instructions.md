# AI Coding Assistant Instructions

## Project Overview

This is a Python project called "subset" using modern Python 3.13+ with **uv** as the package manager and dependency resolver. The project focuses on data validation using **Pandera with Polars** backend for high-performance data processing.

**Key Innovation**: Implements automatic subset validation using **metaclass-based superset validation** - subset DataFrameModels are automatically validated against a central superset schema at class definition time.

## Key Technologies & Architecture

- **Package Manager**: `uv` (not pip) - all dependency management through `uv.lock`
- **Data Framework**: Pandera with Polars backend for schema validation and data processing
- **Python Version**: 3.13+ (strict requirement in `pyproject.toml`)
- **Virtual Environment**: `.venv` managed by uv
- **Static Analysis**: `ty` for advanced type checking, `ruff` for linting/formatting

## Development Workflow

### Environment Setup

```bash
# Use uv for all package operations, not pip
uv sync                    # Install dependencies from uv.lock
uv add <package>          # Add new dependencies
uv remove <package>       # Remove dependencies
uv run python main.py     # Run the application
```

### Project Structure Patterns

- **Single module approach**: Currently using `main.py` as entry point
- **Minimal dependencies**: Only essential packages (pandera[polars])
- **Modern Python**: Leveraging Python 3.13 features and type hints

## Metaclass-Based Subset Validation Pattern

This project implements a novel approach for **automatic validation of subset schemas against superset schemas**:

### Core Pattern

```python
# 1. Define central superset schema
class FullUserDataModel(DataFrameModel):
    user_id: int = pa.Field(ge=1)
    name: str
    email: str
    age: int
    salary: float
    department: str
    created_at: str

    class Config:
        strict = "filter"  # Auto-removes extra columns

# 2. Define subset models with automatic validation
class ContactDataModel(DataFrameModel, metaclass=ValidatedSubsetMeta, superset=FullUserDataModel):
    user_id: int = pa.Field(ge=1)
    name: str
    email: str

    class Config:
        strict = "filter"
```

### Key Benefits

- **Automatic validation**: Subset columns validated against superset at class definition time
- **No manual calls**: No need to call `validate_subset_columns()` manually
- **Immediate feedback**: Invalid subsets fail fast during import/definition
- **Pandera integration**: Full compatibility with Pandera's validation and `strict='filter'`
- **Helper methods**: Auto-generated `get_subset_columns()` and `get_superset_model()` methods

### Usage Rules

- Subset models MUST use `metaclass=ValidatedSubsetMeta, superset=SupersetModel`
- All subset columns must exist in the specified superset model
- Use `strict='filter'` in Config to automatically remove extra columns from DataFrames

## Development Conventions

- **Entry point**: Use `main.py` with `if __name__ == "__main__":` pattern
- **Dependencies**: Always update `pyproject.toml` and run `uv sync`
- **Python version**: Code must be compatible with Python 3.13+
- **Type hints**: Expected for all new code (modern Python practices)

## Build & Run Commands

```bash
uv run python main.py     # Run demonstration of metaclass validation pattern
uv run ty check main.py   # Static type checking with ty
uv run ruff check main.py # Lint checking with ruff
uv run ruff format main.py # Code formatting with ruff
uv sync                   # Update dependencies from lock file
uv lock                   # Regenerate lock file after dependency changes
```

## Important Notes

- **Never use pip** - this project uses uv exclusively
- **No test suite yet** - consider adding pytest with `uv add pytest --dev`
- **Empty README** - project documentation needs development
- **Git ignores**: Standard Python patterns plus `.venv` exclusion

## Common Tasks

- Adding data processing: Extend with Polars DataFrames and Pandera schemas
- Testing: Set up with `uv add pytest --dev` and create `tests/` directory
- Documentation: Populate `README.md` with project purpose and usage examples
