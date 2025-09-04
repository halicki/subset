"""
Clean subset validation using base class pattern.
Automatic validation of DataFrameModel subsets against superset schemas.
"""

from pandera.polars import DataFrameModel
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

        return new_class

    @staticmethod
    def _validate_against_superset(
        subset_class: Type, superset_model: Type[DataFrameModel], subset_name: str
    ):
        """Validate that subset columns exist in superset with compatible types."""
        subset_annotations = getattr(subset_class, "__annotations__", {})
        superset_annotations = getattr(superset_model, "__annotations__", {})

        if not subset_annotations:
            return  # No columns to validate

        subset_columns = set(subset_annotations.keys())
        superset_columns = set(superset_annotations.keys())

        # Check for missing columns
        missing_columns = subset_columns - superset_columns
        if missing_columns:
            raise ValueError(
                f"❌ Subset model '{subset_name}' declares columns not in superset '{superset_model.__name__}':\n"
                f"   Missing columns: {sorted(missing_columns)}\n"
                f"   Available superset columns: {sorted(superset_columns)}"
            )

        # Check for type compatibility
        type_mismatches = []
        for column_name in subset_columns:
            subset_type = subset_annotations[column_name]
            superset_type = superset_annotations[column_name]

            if subset_type != superset_type:
                subset_type_name = getattr(subset_type, "__name__", str(subset_type))
                superset_type_name = getattr(
                    superset_type, "__name__", str(superset_type)
                )
                type_mismatches.append(
                    f"   • {column_name}: subset has {subset_type_name}, superset has {superset_type_name}"
                )

        if type_mismatches:
            raise TypeError(
                f"❌ Subset model '{subset_name}' has type mismatches with superset '{superset_model.__name__}':\n"
                + "\n".join(type_mismatches)
            )


class ValidatedSubset(DataFrameModel, metaclass=ValidatedSubsetMeta):
    """
    Base class for all subset models with automatic validation.
    Inherit from this and specify superset in class definition.
    """

    class Config:
        strict = "filter"
