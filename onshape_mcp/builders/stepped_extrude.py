"""Stepped extrude feature builder for Onshape - creates counterbore holes."""

from typing import Any, Dict, List, Optional, Tuple
from .extrude import ExtrudeType


class SteppedExtrudeBuilder:
    """Builder for creating stepped holes (counterbore holes) with multiple diameters."""

    def __init__(
        self,
        name_prefix: str = "Step",
        center: Tuple[float, float] = (0, 0),
        radii: Optional[List[float]] = None,
        depths: Optional[List[float]] = None,
        plane: str = "Top",
    ):
        """Initialize stepped extrude builder for counterbore holes.

        Args:
            name_prefix: Prefix for the feature names (will add step numbers)
            center: Center point [x, y] in inches for all circles
            radii: List of radii in inches, in descending order (largest to smallest)
            depths: List of cumulative depths in inches (e.g., [0.5, 1.0, 1.5] for steps at 0.5", 1.0", 1.5")
            plane: Sketch plane ("Top", "Front", or "Right")
        """
        self.name_prefix = name_prefix
        self.center = center
        self.radii = radii or []
        self.depths = depths or []
        self.plane = plane

    def add_step(
        self, radius: float, depth: float
    ) -> "SteppedExtrudeBuilder":
        """Add a step to the counterbore hole.

        Args:
            radius: Radius in inches for this step
            depth: Cumulative depth in inches for this step

        Returns:
            Self for chaining
        """
        self.radii.append(radius)
        self.depths.append(depth)
        return self

    def build_all_features(self) -> List[Dict[str, Any]]:
        """Build all features (sketches + extrudes) for the counterbore hole.

        Returns:
            List of feature definitions for Onshape API (alternating sketch, extrude, sketch, extrude...)
        """
        if len(self.radii) != len(self.depths):
            raise ValueError("Number of radii must match number of depths")

        if len(self.radii) < 2:
            raise ValueError("At least 2 steps required for counterbore hole")

        from .sketch import SketchBuilder

        features = []

        # Sort by radius (largest first) to create proper counterbore
        # Largest radius should have shallowest depth
        steps = list(zip(self.radii, self.depths))
        steps.sort(key=lambda x: -x[0])  # Sort by radius descending

        for i, (radius, depth) in enumerate(steps):
            # Create a sketch with a single circle
            sketch = SketchBuilder(
                name=f"{self.name_prefix} Sketch {i + 1}",
                plane=self.plane
            )
            sketch.add_circle(
                center=self.center,
                radius=radius,
                is_construction=False
            )

            # Add sketch feature
            sketch_feature = sketch.build()
            features.append(sketch_feature)

            # Create placeholder for sketch ID - will be filled in after sketch is created
            sketch_id_placeholder = f"{{SKETCH_{i}}}"

            # Create extrude REMOVE feature
            extrude_feature = {
                "btType": "BTFeatureDefinitionCall-1406",
                "feature": {
                    "btType": "BTMFeature-134",
                    "featureType": "extrude",
                    "name": f"{self.name_prefix} {i + 1}",
                    "suppressed": False,
                    "namespace": "",
                    "parameters": [
                        {
                            "btType": "BTMParameterQueryList-148",
                            "queries": [
                                {
                                    "btType": "BTMIndividualSketchRegionQuery-140",
                                    "queryStatement": None,
                                    "filterInnerLoops": True,
                                    "queryString": f'query = qSketchRegion(id + "{sketch_id_placeholder}", true);',
                                    "featureId": sketch_id_placeholder,
                                    "deterministicIds": [],
                                }
                            ],
                            "parameterId": "entities",
                            "parameterName": "",
                            "libraryRelationType": "NONE",
                        },
                        {
                            "btType": "BTMParameterEnum-145",
                            "namespace": "",
                            "enumName": "NewBodyOperationType",
                            "value": ExtrudeType.REMOVE.value,
                            "parameterId": "operationType",
                            "parameterName": "",
                            "libraryRelationType": "NONE",
                        },
                        {
                            "btType": "BTMParameterQuantity-147",
                            "isInteger": False,
                            "value": depth,
                            "units": "",
                            "expression": f"{depth} in",
                            "parameterId": "depth",
                            "parameterName": "",
                            "libraryRelationType": "NONE",
                        },
                        {
                            "btType": "BTMParameterBoolean-144",
                            "value": False,
                            "parameterId": "oppositeDirection",
                            "parameterName": "",
                            "libraryRelationType": "NONE",
                        },
                    ],
                },
            }
            features.append(extrude_feature)

        return features
