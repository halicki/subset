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

    def test_type_mismatch_raises_error(self):
        """Test that type mismatches raise TypeError."""
        with pytest.raises(TypeError, match="has type mismatches with superset"):

            class TypeMismatchModel(ValidatedSubset, superset=FullUserDataModel):
                user_id: str  # Wrong type - should be int
                name: str

    def test_subset_without_superset_works(self):
        """Test that models without superset specified work normally."""

        class RegularModel(ValidatedSubset):
            some_field: str

        # Should not have superset reference
        assert not hasattr(RegularModel, "__superset_model__")

    def test_empty_subset_model_works(self):
        """Test that subset model with no annotations works."""

        class EmptySubsetModel(ValidatedSubset, superset=FullUserDataModel):
            pass  # No annotations

        # Should not raise an error and should have superset reference
        assert hasattr(EmptySubsetModel, "__superset_model__")
        assert EmptySubsetModel.__superset_model__ == FullUserDataModel  # type: ignore

    def test_multiple_missing_columns_error(self):
        """Test error message when multiple columns are missing."""
        with pytest.raises(ValueError) as exc_info:

            class MultipleMissingModel(ValidatedSubset, superset=FullUserDataModel):
                user_id: int = pa.Field(ge=1)
                missing_col1: str
                missing_col2: int

        error_msg = str(exc_info.value)
        assert "missing_col1" in error_msg
        assert "missing_col2" in error_msg
        assert "Missing columns:" in error_msg

    def test_multiple_type_mismatches_error(self):
        """Test error message when multiple types are mismatched."""
        with pytest.raises(TypeError) as exc_info:

            class MultipleTypeMismatchModel(
                ValidatedSubset, superset=FullUserDataModel
            ):
                user_id: str  # Should be int
                age: str  # Should be int
                name: str  # This one is correct

        error_msg = str(exc_info.value)
        assert "user_id" in error_msg
        assert "age" in error_msg
        assert "subset has str, superset has int" in error_msg

    def test_complex_type_annotations(self):
        """Test that complex type annotations are handled correctly."""
        from typing import Optional

        # This should work - same complex types
        class ComplexValidModel(ValidatedSubset, superset=FullUserDataModel):
            user_id: int = pa.Field(ge=1)
            name: str

        # This should fail - different complex types
        with pytest.raises(TypeError):

            class ComplexInvalidModel(ValidatedSubset, superset=FullUserDataModel):
                user_id: Optional[int]  # Different from superset's int
                name: str


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

    def test_field_validation_inheritance(self, sample_user_data):
        """Test that Pandera Field validations are properly inherited."""
        # Create data with invalid values
        invalid_data = sample_user_data.copy()
        invalid_data["user_id"] = [-1, 0, -5]  # Invalid: should be >= 1

        df = pl.DataFrame(invalid_data)

        # Should raise Pandera validation error for Field constraints
        with pytest.raises(Exception):  # Pandera field validation error
            ContactDataModel.validate(df)

    def test_strict_filter_behavior(self, sample_user_data):
        """Test that strict='filter' removes extra columns correctly."""
        df = pl.DataFrame(sample_user_data)
        result = ContactDataModel.validate(df)

        # Should only contain subset columns, extra columns filtered out
        assert len(result.columns) == 3
        assert "extra_column" not in result.columns
        assert "created_at" not in result.columns  # Not in ContactDataModel

        # But should contain all subset columns
        expected = {"user_id", "name", "email"}
        actual = set(result.columns)
        assert actual == expected

    def test_data_values_preserved(self, sample_user_data):
        """Test that data values are preserved during validation."""
        df = pl.DataFrame(sample_user_data)
        result = ContactDataModel.validate(df)

        # Check that actual data values are preserved
        assert result["user_id"].to_list() == [1, 2, 3]
        assert result["name"].to_list() == ["Alice", "Bob", "Charlie"]
        assert result["email"].to_list() == [
            "alice@example.com",
            "bob@example.com",
            "charlie@example.com",
        ]


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

    def test_superset_model_storage(self):
        """Test that superset model reference is stored correctly."""
        # Test that the stored superset model is the actual class, not a copy
        assert ContactDataModel.__superset_model__ is FullUserDataModel  # type: ignore
        assert ProductSummaryModel.__superset_model__ is FullProductDataModel  # type: ignore

    def test_inheritance_from_pandera_dataframe_model(self):
        """Test that subset models properly inherit from DataFrameModel."""
        # Should have all the DataFrameModel methods
        assert hasattr(ContactDataModel, "validate")
        assert hasattr(ContactDataModel, "Config")

        # Should be instance of DataFrameModel metaclass
        assert isinstance(ContactDataModel, type)

    def test_metaclass_applied_correctly(self):
        """Test that ValidatedSubsetMeta is properly applied."""
        # The metaclass should be ValidatedSubsetMeta
        from subset import ValidatedSubsetMeta

        assert type(ContactDataModel) is ValidatedSubsetMeta

        # But regular models without superset should also work
        class RegularModel(ValidatedSubset):
            some_field: str

        assert type(RegularModel) is ValidatedSubsetMeta
