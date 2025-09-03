"""
Test schemas for subset validation examples.
Central superset schemas and example subset models.
"""

import pandera as pa
from pandera.polars import DataFrameModel
from subset import ValidatedSubset


# ===========================================
# CENTRAL SUPERSET SCHEMAS
# ===========================================


class FullUserDataModel(DataFrameModel):
    """Complete user data model with all available fields."""

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
    """Complete product data model with all available fields."""

    product_id: int = pa.Field(ge=1)
    name: str
    price: float = pa.Field(ge=0)
    category: str
    in_stock: bool
    created_at: str

    class Config:
        strict = "filter"


# ===========================================
# EXAMPLE SUBSET MODEL DEFINITIONS
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
