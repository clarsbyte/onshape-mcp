"""Fillet feature builder for Onshape."""

from typing import Any, Dict, List, Optional
from enum import Enum


class FilletType(Enum):
    """Fillet operation type."""

    EDGE = "EDGE"  # Standard edge fillet
    FACE = "FACE"  # Face fillet
    FULL_ROUND = "FULL_ROUND"  # Full round fillet


class FilletBuilder:
    """Builder for creating Onshape fillet features."""

    def __init__(
        self,
        name: str = "Fillet",
        radius: float = 0.1,
        fillet_type: FilletType = FilletType.EDGE,
    ):
        """Initialize fillet builder.

        Args:
            name: Name of the fillet feature
            radius: Fillet radius in inches
            fillet_type: Type of fillet operation
        """
        self.name = name
        self.radius = radius
        self.fillet_type = fillet_type
        self.radius_variable: Optional[str] = None
        self.edge_ids: List[str] = []

    def set_radius(self, radius: float, variable_name: Optional[str] = None) -> "FilletBuilder":
        """Set fillet radius.

        Args:
            radius: Radius in inches
            variable_name: Optional variable name to reference

        Returns:
            Self for chaining
        """
        self.radius = radius
        self.radius_variable = variable_name
        return self

    def add_edge(self, edge_id: str) -> "FilletBuilder":
        """Add an edge to fillet.

        Args:
            edge_id: Deterministic ID of the edge to fillet

        Returns:
            Self for chaining
        """
        self.edge_ids.append(edge_id)
        return self

    def set_edges(self, edge_ids: List[str]) -> "FilletBuilder":
        """Set all edges to fillet.

        Args:
            edge_ids: List of deterministic edge IDs

        Returns:
            Self for chaining
        """
        self.edge_ids = edge_ids
        return self

    def build(self) -> Dict[str, Any]:
        """Build the fillet feature JSON.

        Returns:
            Feature definition for Onshape API
        """
        if not self.edge_ids:
            raise ValueError("At least one edge ID must be set before building fillet")

        radius_expression = f"#{self.radius_variable}" if self.radius_variable else f"{self.radius} in"

        return {
            "btType": "BTFeatureDefinitionCall-1406",
            "feature": {
                "btType": "BTMFeature-134",
                "featureType": "fillet",
                "name": self.name,
                "suppressed": False,
                "namespace": "",
                "parameters": [
                    {
                        "btType": "BTMParameterQueryList-148",
                        "queries": [
                            {
                                "btType": "BTMIndividualQuery-138",
                                "deterministicIds": self.edge_ids,
                            }
                        ],
                        "parameterId": "entities",
                        "parameterName": "",
                        "libraryRelationType": "NONE",
                    },
                    {
                        "btType": "BTMParameterQuantity-147",
                        "isInteger": False,
                        "value": self.radius,
                        "units": "",
                        "expression": radius_expression,
                        "parameterId": "radius",
                        "parameterName": "",
                        "libraryRelationType": "NONE",
                    },
                    {
                        "btType": "BTMParameterEnum-145",
                        "namespace": "",
                        "enumName": "FilletType",
                        "value": self.fillet_type.value,
                        "parameterId": "filletType",
                        "parameterName": "",
                        "libraryRelationType": "NONE",
                    },
                ],
            },
        }
