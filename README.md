# Subset Validation Library

A clean Python library for automatic validation of DataFrameModel subsets against superset schemas using Pandera and Polars.

## Features

- ✅ **Automatic validation** - Subset columns validated against superset at class definition time
- ✅ **Succinct syntax** - Simple inheritance with `superset=` parameter
- ✅ **Type-safe** - Full static type checking and IDE autocompletion
- ✅ **High performance** - Built on Polars backend for fast data processing
- ✅ **Zero boilerplate** - No manual validation calls or column selection needed

## Quick Start

### Installation

```bash
# Clone and install
git clone <repository-url>
cd subset
uv sync --dev
```

### Basic Usage

```python
from subset import ValidatedSubset
import pandera as pa
from pandera.polars import DataFrameModel

# Define your superset schema
class FullUserDataModel(DataFrameModel):
    user_id: int = pa.Field(ge=1)
    name: str
    email: str
    age: int = pa.Field(ge=0, le=120)
    salary: float = pa.Field(ge=0)
    department: str
    created_at: str

    class Config:
        strict = "filter"

# Create subset models with automatic validation
class ContactDataModel(ValidatedSubset, superset=FullUserDataModel):
    """Contact information subset - just the essentials."""
    user_id: int = pa.Field(ge=1)
    name: str
    email: str

class FinanceDataModel(ValidatedSubset, superset=FullUserDataModel):
    """Financial information subset."""
    user_id: int = pa.Field(ge=1)
    salary: float = pa.Field(ge=0)
    department: str
```

### Data Validation

```python
import polars as pl

# Your data with extra columns
data = {
    "user_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "email": ["alice@example.com", "bob@example.com", "charlie@example.com"],
    "age": [25, 30, 35],
    "salary": [50000.0, 60000.0, 70000.0],
    "department": ["Engineering", "Marketing", "Sales"],
    "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "extra_column": ["will", "be", "filtered"],
}

df = pl.DataFrame(data)

# Validate and filter to subset columns automatically
contact_df = ContactDataModel.validate(df)
# Result: Only user_id, name, email columns

finance_df = FinanceDataModel.validate(df)
# Result: Only user_id, salary, department columns
```

## How It Works

The `ValidatedSubset` pattern uses a metaclass to automatically validate subset models at class definition time:

1. **Define superset** - Create your complete data model
2. **Create subsets** - Inherit from `ValidatedSubset` with `superset=` parameter
3. **Automatic validation** - Metaclass validates that all subset columns exist in superset
4. **Runtime filtering** - Pandera filters data to include only subset columns

### Key Benefits

- **Compile-time safety** - Catch column mismatches when defining models, not at runtime
- **Zero boilerplate** - No manual column selection or validation calls needed
- **Scalable architecture** - Clean pattern for managing 10+ related models
- **Full Pandera integration** - Leverages existing validation and filtering capabilities
- **Developer experience** - IDE autocompletion and static type checking support

## Development

### Prerequisites

- Python 3.13+
- UV package manager

### Development Commands

#### Setup and Environment

```bash
# Initial setup - install dependencies and prepare environment
make dev

# Show all available commands
make help
```

#### Code Quality and Testing

```bash
# Run all quality checks (recommended before commits)
make quality          # Complete check: tests + linting + type checking

# Individual quality checks
make test            # Run all tests with pytest
make lint            # Run ruff linting
make typecheck       # Run static type checking with ty
make format          # Auto-format code with ruff
```

#### Maintenance

```bash
# Clean up cache files and build artifacts
make clean
```

### Project Structure

```
subset/
├── subset.py          # Main library code
├── pyproject.toml     # Package configuration
├── Makefile          # Development commands
├── tests/            # Test suite
│   ├── __init__.py
│   ├── schemas.py    # Example schemas
│   └── test_subset_validation.py
└── README.md
```

## Requirements

- Python >= 3.13
- pandera[polars] >= 0.26.1

## License

MIT License - see [LICENSE](LICENSE) file for details.
