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


class ValidatedSubset(DataFrameModel, metaclass=ValidatedSubsetMeta):
    """
    Base class for all subset models with automatic validation.
    Inherit from this and specify superset in class definition.
    """

    class Config:
        strict = "filter"
