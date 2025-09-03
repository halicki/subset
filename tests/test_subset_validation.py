"""
Test the ValidatedSubset pattern with pytest.
Comprehensive tests for subset validation functionality.
"""

import pytest
import polars as pl
from subset import ValidatedSubset
import pandera as pa
from tests.schemas import (
    FullUserDataModel,
    FullProductDataModel,
    ContactDataModel,
    FinanceDataModel,
    UserBasicsModel,
    ProductSummaryModel,
    ProductInventoryModel,
)


class TestValidatedSubsetMeta:
    """Test the metaclass validation functionality."""

    def test_valid_subset_creation(self):
        """Test that valid subset models are created successfully."""

        # This should work without raising an exception
        class ValidTestModel(ValidatedSubset, superset=FullUserDataModel):
            user_id: int = pa.Field(ge=1)
            name: str

        assert hasattr(ValidTestModel, "__superset_model__")
        assert ValidTestModel.__superset_model__ == FullUserDataModel  # type: ignore

    def test_invalid_subset_creation_raises_error(self):
        """Test that invalid subset models raise ValueError."""
        with pytest.raises(ValueError, match="declares columns not in superset"):

            class InvalidTestModel(ValidatedSubset, superset=FullUserDataModel):
                user_id: int = pa.Field(ge=1)
                invalid_column: str  # This column doesn't exist in superset

    def test_subset_without_superset_works(self):
        """Test that models without superset specified work normally."""

        class RegularModel(ValidatedSubset):
            some_field: str

        # Should not have superset reference
        assert not hasattr(RegularModel, "__superset_model__")


class TestSubsetValidation:
    """Test actual data validation with subset models."""

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data with extra columns that should be filtered."""
        return {
            "user_id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "email": ["alice@example.com", "bob@example.com", "charlie@example.com"],
            "age": [25, 30, 35],
            "salary": [50000.0, 60000.0, 70000.0],
            "department": ["Engineering", "Marketing", "Sales"],
            "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "extra_column": ["will", "be", "filtered"],
        }

    @pytest.fixture
    def sample_product_data(self):
        """Sample product data with extra columns that should be filtered."""
        return {
            "product_id": [101, 102, 103],
            "name": ["Widget A", "Gadget B", "Tool C"],
            "price": [19.99, 29.99, 39.99],
            "category": ["Tools", "Electronics", "Hardware"],
            "in_stock": [True, False, True],
            "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "extra_product_column": ["will", "be", "filtered"],
        }

    def test_contact_data_model_validation(self, sample_user_data):
        """Test ContactDataModel validation and filtering."""
        df = pl.DataFrame(sample_user_data)
        result = ContactDataModel.validate(df)

        expected_columns = ["user_id", "name", "email"]
        assert result.columns == expected_columns
        assert result.shape == (3, 3)

    def test_finance_data_model_validation(self, sample_user_data):
        """Test FinanceDataModel validation and filtering."""
        df = pl.DataFrame(sample_user_data)
        result = FinanceDataModel.validate(df)

        expected_columns = ["user_id", "salary", "department"]
        assert result.columns == expected_columns
        assert result.shape == (3, 3)

    def test_user_basics_model_validation(self, sample_user_data):
        """Test UserBasicsModel validation and filtering."""
        df = pl.DataFrame(sample_user_data)
        result = UserBasicsModel.validate(df)

        expected_columns = ["user_id", "name", "age"]
        assert result.columns == expected_columns
        assert result.shape == (3, 3)

    def test_product_summary_model_validation(self, sample_product_data):
        """Test ProductSummaryModel validation and filtering."""
        df = pl.DataFrame(sample_product_data)
        result = ProductSummaryModel.validate(df)

        expected_columns = ["product_id", "name", "price"]
        assert result.columns == expected_columns
        assert result.shape == (3, 3)

    def test_product_inventory_model_validation(self, sample_product_data):
        """Test ProductInventoryModel validation and filtering."""
        df = pl.DataFrame(sample_product_data)
        result = ProductInventoryModel.validate(df)

        expected_columns = ["product_id", "name", "in_stock"]
        assert result.columns == expected_columns
        assert result.shape == (3, 3)

    def test_validation_with_missing_columns_fails(self, sample_user_data):
        """Test that validation fails when required columns are missing."""
        # Remove a required column
        incomplete_data = {k: v for k, v in sample_user_data.items() if k != "email"}
        df = pl.DataFrame(incomplete_data)

        # Should raise an error because email column is missing
        with pytest.raises(Exception):  # Pandera will raise its own validation error
            ContactDataModel.validate(df)


class TestPatternBehavior:
    """Test the overall behavior of the ValidatedSubset pattern."""

    def test_multiple_models_from_same_superset(self):
        """Test that multiple subset models can be created from the same superset."""
        # All these models should be created successfully
        assert ContactDataModel.__superset_model__ == FullUserDataModel  # type: ignore
        assert FinanceDataModel.__superset_model__ == FullUserDataModel  # type: ignore
        assert UserBasicsModel.__superset_model__ == FullUserDataModel  # type: ignore

    def test_different_supersets(self):
        """Test that models can use different superset schemas."""
        assert ContactDataModel.__superset_model__ == FullUserDataModel  # type: ignore
        assert ProductSummaryModel.__superset_model__ == FullProductDataModel  # type: ignore

        # They should be different
        contact_superset = ContactDataModel.__superset_model__  # type: ignore
        product_superset = ProductSummaryModel.__superset_model__  # type: ignore
        assert contact_superset != product_superset

    def test_config_inheritance(self):
        """Test that Config is properly inherited."""
        # All models should have strict="filter" configuration
        assert ContactDataModel.Config.strict == "filter"
        assert ProductSummaryModel.Config.strict == "filter"
