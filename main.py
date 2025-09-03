"""
Metaclass implementation for automatic subset validation against superset.
No more manual validate_subset_columns calls!
"""

import polars as pl
from pandera.polars import DataFrameModel
import pandera as pa
from typing import Type, Any, Dict


from pandera.api.base.model import MetaModel


class ValidatedSubsetMeta(MetaModel):
    """
    Metaclass that automatically validates subset models against a superset at class definition time.
    Inherits from Pandera's MetaModel to be compatible with DataFrameModel.
    """

    def __new__(cls, name: str, bases: tuple, attrs: Dict[str, Any], **kwargs):
        # Get the superset model if specified
        superset_model = kwargs.get("superset", None)

        # Create the class first
        new_class = super().__new__(cls, name, bases, attrs)

        # If this is a subset model (has superset specified), validate it
        if superset_model is not None:
            cls._validate_against_superset(new_class, superset_model, name)

            # Store the superset reference for later use
            new_class.__superset_model__ = superset_model

            # Add a helpful method to check what columns this subset uses
            new_class.get_subset_columns = classmethod(
                lambda cls: list(cls.__annotations__.keys())
            )
            new_class.get_superset_model = classmethod(
                lambda cls: cls.__superset_model__
            )

        return new_class

    @staticmethod
    def _validate_against_superset(
        subset_class: Type, superset_model: Type[DataFrameModel], subset_name: str
    ):
        """Validate that subset columns exist in superset."""
        if not hasattr(subset_class, "__annotations__"):
            return  # No annotations to validate

        subset_columns = set(subset_class.__annotations__.keys())
        superset_columns = set(superset_model.__annotations__.keys())

        missing = subset_columns - superset_columns
        if missing:
            raise ValueError(
                f"❌ Subset model '{subset_name}' declares columns not in superset '{superset_model.__name__}': {missing}\n"
                f"   Available superset columns: {sorted(superset_columns)}\n"
                f"   Subset tried to use: {sorted(subset_columns)}"
            )

        print(
            f"✅ Subset model '{subset_name}' validated against superset '{superset_model.__name__}'"
        )


# Central repository - SUPERSET schema (source of truth)
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


# Subset models using metaclass - automatic validation!
class ContactDataModel(
    DataFrameModel, metaclass=ValidatedSubsetMeta, superset=FullUserDataModel
):
    user_id: int = pa.Field(ge=1)
    name: str
    email: str

    class Config:
        strict = "filter"


class FinanceDataModel(
    DataFrameModel, metaclass=ValidatedSubsetMeta, superset=FullUserDataModel
):
    user_id: int = pa.Field(ge=1)
    salary: float = pa.Field(ge=0)
    department: str

    class Config:
        strict = "filter"


# For comparison - the old manual approach (no longer needed!)
def validate_subset_columns(
    subset_model: type[DataFrameModel], superset_model: type[DataFrameModel]
) -> bool:
    """Manual validation (replaced by metaclass approach)."""
    subset_columns = set(subset_model.__annotations__.keys())
    superset_columns = set(superset_model.__annotations__.keys())

    missing = subset_columns - superset_columns
    if missing:
        raise ValueError(
            f"Subset {subset_model.__name__} declares columns not in superset {superset_model.__name__}: {missing}"
        )

    print(
        f"✅ {subset_model.__name__} subset is valid against {superset_model.__name__}"
    )
    return True


def main():
    print("=== Metaclass-Based Automatic Validation Demo ===")
    print()

    # Show superset columns
    superset_columns = list(FullUserDataModel.__annotations__.keys())
    print(f"Superset columns: {superset_columns}")
    print()

    print("=== Models Already Validated at Class Definition Time ===")
    print("(You saw the validation messages when the classes were defined)")
    print()

    # Show that models are already validated
    contact_columns = list(ContactDataModel.__annotations__.keys())
    finance_columns = list(FinanceDataModel.__annotations__.keys())

    print(f"ContactDataModel columns: {contact_columns}")
    print(f"FinanceDataModel columns: {finance_columns}")
    print()

    # Demonstrate new helper methods added by metaclass
    print("=== Helper Methods Added by Metaclass ===")
    print(
        f"ContactDataModel.get_subset_columns(): {getattr(ContactDataModel, 'get_subset_columns')()}"
    )
    print(
        f"ContactDataModel.get_superset_model(): {getattr(ContactDataModel, 'get_superset_model')().__name__}"
    )
    print(
        f"FinanceDataModel.get_subset_columns(): {getattr(FinanceDataModel, 'get_subset_columns')()}"
    )
    print(
        f"FinanceDataModel.get_superset_model(): {getattr(FinanceDataModel, 'get_superset_model')().__name__}"
    )
    print()

    # Test with actual data
    print("=== Testing with Real Data ===")
    sample_data = {
        "user_id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com"],
        "age": [25, 30, 35],
        "salary": [50000.0, 60000.0, 70000.0],
        "department": ["Engineering", "Marketing", "Sales"],
        "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "extra_column": ["will", "be", "filtered"],
    }

    df = pl.DataFrame(sample_data)
    print(f"Original data columns: {df.columns}")
    print(f"Original shape: {df.shape}")
    print()

    # Test subset models
    contact_result = ContactDataModel.validate(df)
    print(f"Contact subset result: {contact_result.columns}")
    print(f"Contact shape: {contact_result.shape}")
    print(contact_result)
    print()

    finance_result = FinanceDataModel.validate(df)
    print(f"Finance subset result: {finance_result.columns}")
    print(f"Finance shape: {finance_result.shape}")
    print(finance_result)
    print()

    # Demonstrate runtime error for invalid subset
    print("=== Attempting to Create Invalid Subset Model ===")
    print("This will fail at class definition time...")

    try:
        # This will fail immediately when the class is defined!
        class InvalidSubsetModel(
            DataFrameModel, metaclass=ValidatedSubsetMeta, superset=FullUserDataModel
        ):
            user_id: int = pa.Field(ge=1)
            name: str
            email: str
            non_existent_column: str  # ⚠️ This doesn't exist in superset!

            class Config:
                strict = "filter"

        print("❌ This line should never be reached!")

    except ValueError as e:
        print("Caught validation error at class definition time:")
        print(f"{e}")


if __name__ == "__main__":
    main()
