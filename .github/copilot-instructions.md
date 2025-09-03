# AI Coding Assistant Instructions

## Project Overview

This is a Python project called "subset" - a production-ready library for automatic subset validation using **metaclass-based superset validation**. Subset DataFrameModels are automatically validated against central superset schemas at class definition time.

**Built with modern Python 3.13+ using uv package manager and Pandera with Polars backend for high-performance data validation.**

## Key Technologies & Architecture

- **Package Manager**: `uv` (not pip) - all dependency management through `uv.lock`
- **Data Framework**: Pandera with Polars backend for schema validation and data processing
- **Python Version**: 3.13+ (strict requirement in `pyproject.toml`)
- **Virtual Environment**: `.venv` managed by uv
- **Static Analysis**: `ty` for type checking, `ruff` for linting/formatting
- **Testing**: `pytest` with comprehensive test suite
- **Build System**: `Makefile` for standardized development workflow

## Project Structure

```
/Users/arek/code/subset/
├── subset.py          # Core library module (ValidatedSubsetMeta, ValidatedSubset)
├── main.py           # Demo/example usage
├── tests/            # Comprehensive test suite
│   ├── test_subset_validation.py  # 12 test cases
│   └── schemas.py    # Example superset/subset models
├── Makefile          # Development workflow commands
├── pyproject.toml    # Project configuration
├── uv.lock          # Locked dependencies
└── README.md        # Project documentation
```

## Development Workflow

### Standard Commands (use these exclusively)

```bash
make dev      # Install dependencies and setup environment
make test     # Run all tests with pytest
make lint     # Run ruff linting
make format   # Auto-format code with ruff
make typecheck # Run static type checking with ty
make quality  # Run all quality checks (test + lint + typecheck)
make clean    # Remove build artifacts and cache
```

### Individual Tools (if needed)

```bash
uv sync                    # Install dependencies from uv.lock
uv add <package>          # Add new dependencies
uv remove <package>       # Remove dependencies
uv run python main.py     # Run demo
```

## Core Library: `subset.py`

### ValidatedSubsetMeta Metaclass

Automatically validates subset columns against superset models at class definition time:

```python
from subset import ValidatedSubset

# Define superset model
class FullUserDataModel(ValidatedSubset):
    user_id: int = pa.Field(ge=1)
    name: str
    email: str
    age: int
    salary: float
    department: str
    created_at: str

# Define subset - automatically validated at class definition
class ContactDataModel(ValidatedSubset, superset=FullUserDataModel):
    user_id: int = pa.Field(ge=1)
    name: str
    email: str
    # Missing columns will raise ValidationError immediately
```

### Key Features

- **Automatic validation**: Subset columns validated against superset at import time
- **Immediate feedback**: Invalid subsets fail fast during class definition
- **Helper methods**: Auto-generated `get_subset_columns()` and `get_superset_model()`
- **Full Pandera compatibility**: Works with all Pandera validation features
- **Clean syntax**: Simple inheritance pattern with `superset=` parameter

## Testing Architecture

**Location**: `tests/` directory with 12 comprehensive test cases

**Test Coverage**:

- Metaclass validation behavior
- Superset/subset column validation
- Error handling for invalid subsets
- Helper method functionality
- Data validation integration
- Example schema patterns

**Run Tests**: `make test` (uses pytest via uv)

## Code Quality Standards

- **Type hints**: Required for all new code (enforced by ty)
- **Code style**: Enforced by ruff (auto-formatting available)
- **Test coverage**: All features must have corresponding tests
- **Documentation**: Docstrings for public APIs

## Development Conventions

- **Main library**: Keep `subset.py` minimal and focused on core functionality
- **Examples**: Use `main.py` for demonstrations and usage examples
- **Tests**: Add to `tests/` directory with descriptive test names
- **Dependencies**: Always use `uv add` and commit `uv.lock` changes
- **Quality**: Run `make quality` before committing changes

## Common Development Tasks

- **Add new feature**: Implement in `subset.py`, add tests in `tests/`, run `make quality`
- **Add example**: Extend `main.py` or `tests/schemas.py` with new model examples
- **Debug validation**: Check `tests/test_subset_validation.py` for validation patterns
- **Performance testing**: Use Polars DataFrames for large dataset validation

## Important Notes

- **Never use pip** - this project uses uv exclusively
- **Always run quality checks** - `make quality` before any commits
- **Type checking**: Some dynamic attributes use `# type: ignore` comments (expected)
- **Polars backend**: Automatic via pandera[polars] dependency for performance
