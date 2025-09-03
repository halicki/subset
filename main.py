"""
Clean subset validation using base class pattern.
Automatic validation of DataFrameModel subsets against superset schemas.
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


# ===========================================
# VALIDATED SUBSET BASE CLASS
# ===========================================


class ValidatedSubset(DataFrameModel, metaclass=ValidatedSubsetMeta):
    """
    Base class for all subset models with automatic validation.
    Inherit from this and specify superset in class definition.
    """

    class Config:
        strict = "filter"


# ===========================================
# CENTRAL SUPERSET SCHEMAS
# ===========================================


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


class FullProductDataModel(DataFrameModel):
    product_id: int = pa.Field(ge=1)
    name: str
    price: float = pa.Field(ge=0)
    category: str
    in_stock: bool
    created_at: str

    class Config:
        strict = "filter"


# ===========================================
# SUBSET MODEL DEFINITIONS
# ===========================================


class ContactDataModel(ValidatedSubset, superset=FullUserDataModel):
    """Contact information subset - just the essentials for communication."""

    user_id: int = pa.Field(ge=1)
    name: str
    email: str


class FinanceDataModel(ValidatedSubset, superset=FullUserDataModel):
    """Financial information subset - salary and department data."""

    user_id: int = pa.Field(ge=1)
    salary: float = pa.Field(ge=0)
    department: str


class UserBasicsModel(ValidatedSubset, superset=FullUserDataModel):
    """Basic user information subset - core demographic data."""

    user_id: int = pa.Field(ge=1)
    name: str
    age: int = pa.Field(ge=0, le=120)


class ProductSummaryModel(ValidatedSubset, superset=FullProductDataModel):
    """Product summary subset - key product information."""

    product_id: int = pa.Field(ge=1)
    name: str
    price: float = pa.Field(ge=0)


class ProductInventoryModel(ValidatedSubset, superset=FullProductDataModel):
    """Product inventory subset - stock tracking information."""

    product_id: int = pa.Field(ge=1)
    name: str
    in_stock: bool


def main():
    """Demonstrate the ValidatedSubset pattern with real data validation."""
    print("=== ValidatedSubset Pattern Demonstration ===")
    print()
    print(
        "✅ All subset models validated against superset schemas at class definition time!"
    )
    print()

    # Create sample data that includes extra columns
    sample_user_data = {
        "user_id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com"],
        "age": [25, 30, 35],
        "salary": [50000.0, 60000.0, 70000.0],
        "department": ["Engineering", "Marketing", "Sales"],
        "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "extra_column": ["will", "be", "filtered"],
    }

    sample_product_data = {
        "product_id": [101, 102, 103],
        "name": ["Widget A", "Gadget B", "Tool C"],
        "price": [19.99, 29.99, 39.99],
        "category": ["Tools", "Electronics", "Hardware"],
        "in_stock": [True, False, True],
        "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "extra_product_column": ["will", "be", "filtered"],
    }

    user_df = pl.DataFrame(sample_user_data)
    product_df = pl.DataFrame(sample_product_data)

    print(f"Original user data: {user_df.columns} (shape: {user_df.shape})")
    print(f"Original product data: {product_df.columns} (shape: {product_df.shape})")
    print()

    # Test user subset models
    print("=== User Data Subsets ===")
    contact_result = ContactDataModel.validate(user_df)
    print(f"ContactDataModel: {contact_result.columns}")

    finance_result = FinanceDataModel.validate(user_df)
    print(f"FinanceDataModel: {finance_result.columns}")

    basics_result = UserBasicsModel.validate(user_df)
    print(f"UserBasicsModel: {basics_result.columns}")
    print()

    # Test product subset models
    print("=== Product Data Subsets ===")
    summary_result = ProductSummaryModel.validate(product_df)
    print(f"ProductSummaryModel: {summary_result.columns}")

    inventory_result = ProductInventoryModel.validate(product_df)
    print(f"ProductInventoryModel: {inventory_result.columns}")
    print()

    print("=== Pattern Benefits ===")
    print("✅ Succinct syntax: class MyModel(ValidatedSubset, superset=ParentModel)")
    print("✅ Automatic validation at class definition time")
    print("✅ Clear inheritance relationship")
    print("✅ IDE autocompletion and type checking support")
    print("✅ Built-in helper methods for introspection")
    print()

    # Demonstrate helper methods
    print("=== Built-in Helper Methods ===")
    print(
        f"ContactDataModel.get_subset_columns(): {ContactDataModel.get_subset_columns()}"
    )  # type: ignore
    print(
        f"ContactDataModel.get_superset_model(): {ContactDataModel.get_superset_model().__name__}"
    )  # type: ignore
    print(
        f"ProductSummaryModel.get_subset_columns(): {ProductSummaryModel.get_subset_columns()}"
    )  # type: ignore


if __name__ == "__main__":
    main()
