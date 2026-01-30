"""Edge query utilities for Onshape."""

from typing import Any, Dict, List, Optional
from .client import OnshapeClient


class EdgeQuery:
    """Helper class for querying and filtering edges in Onshape parts."""

    def __init__(self, client: OnshapeClient):
        """Initialize the edge query helper.

        Args:
            client: Onshape API client
        """
        self.client = client

    async def get_edges(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
    ) -> Dict[str, Any]:
        """Get all edges from a Part Studio using FeatureScript.

        Args:
            document_id: Document ID
            workspace_id: Workspace ID
            element_id: Part Studio element ID

        Returns:
            Dictionary containing edge information
        """
        # FeatureScript to query all edges
        script = """
        function(context is Context, queries) {
            const allEdges = qEverything(EntityType.EDGE);
            const edgeData = [];

            for (var edge in evaluateQuery(context, allEdges)) {
                const edgeInfo = {
                    "transientId": transientQueriesToStrings(context, edge)[0],
                    "deterministicId": undefined
                };

                // Try to get deterministic ID
                try {
                    edgeInfo.deterministicId = toString(qDeterministicIdQuery(edge));
                } catch {}

                // Get edge geometry type
                const geom = evEdgeTangentLine(context, {
                    "edge": edge,
                    "parameter": 0.5
                });

                edgeInfo.geometryType = toString(geom.geometryType);

                // Try to get curvature info for circular edges
                try {
                    const curvature = evEdgeCurvature(context, {
                        "edge": edge,
                        "parameter": 0.5
                    });
                    if (curvature.radius != undefined) {
                        edgeInfo.radius = curvature.radius * meter;
                    }
                } catch {}

                edgeData = append(edgeData, edgeInfo);
            }

            return edgeData;
        }
        """

        path = (
            f"/api/v6/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}"
            "/featurescript"
        )
        data = {"script": script}
        return await self.client.post(path, data=data)

    async def find_circular_edges(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        radius: Optional[float] = None,
        tolerance: float = 0.001,
    ) -> List[str]:
        """Find circular edges, optionally filtered by radius.

        Args:
            document_id: Document ID
            workspace_id: Workspace ID
            element_id: Part Studio element ID
            radius: Optional radius to filter by (in inches)
            tolerance: Radius match tolerance (in inches)

        Returns:
            List of deterministic edge IDs
        """
        all_edges = await self.get_edges(document_id, workspace_id, element_id)

        circular_edges = []
        result = all_edges.get("result", {})

        if not isinstance(result, dict) or "value" not in result:
            return circular_edges

        edges = result["value"]

        for edge in edges:
            # Check if edge has radius (circular)
            if "radius" not in edge:
                continue

            edge_radius = edge["radius"]

            # If no radius filter specified, include all circular edges
            if radius is None:
                if "deterministicId" in edge and edge["deterministicId"]:
                    circular_edges.append(edge["deterministicId"])
            # Otherwise, check if radius matches
            elif abs(edge_radius - radius) <= tolerance:
                if "deterministicId" in edge and edge["deterministicId"]:
                    circular_edges.append(edge["deterministicId"])

        return circular_edges

    async def find_edges_by_feature(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        feature_id: str,
    ) -> List[str]:
        """Find edges created by a specific feature.

        Args:
            document_id: Document ID
            workspace_id: Workspace ID
            element_id: Part Studio element ID
            feature_id: Feature ID to query

        Returns:
            List of deterministic edge IDs
        """
        script = f"""
        function(context is Context, queries) {{
            const feature = qCreatedBy(makeId("{feature_id}"), EntityType.EDGE);
            const edges = evaluateQuery(context, feature);

            const edgeIds = [];
            for (var edge in edges) {{
                try {{
                    const detId = toString(qDeterministicIdQuery(edge));
                    edgeIds = append(edgeIds, detId);
                }} catch {{}}
            }}

            return edgeIds;
        }}
        """

        path = (
            f"/api/v6/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}"
            "/featurescript"
        )
        data = {"script": script}
        result = await self.client.post(path, data=data)

        edge_ids = []
        if isinstance(result, dict) and "result" in result:
            result_value = result["result"].get("value", [])
            if isinstance(result_value, list):
                edge_ids = result_value

        return edge_ids
