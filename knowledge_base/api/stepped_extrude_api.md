# Stepped Extrude API - Counterbore Holes

## Overview

The `create_stepped_extrude` MCP tool creates counterbore holes (stepped holes with multiple diameters) in Onshape Part Studios. It automates the creation of multiple circular sketches and extrude-remove operations to produce professional counterbore features.

## What It Creates

A counterbore hole consists of multiple concentric circles, each extruded to different depths:
- **Largest diameter** at the top (shallowest depth) - typically for bolt heads
- **Medium diameter(s)** in the middle - typically for clearance
- **Smallest diameter** at the bottom (deepest depth) - typically for threads or through-hole

## API Signature

```python
create_stepped_extrude(
    documentId: str,
    workspaceId: str,
    elementId: str,
    center: [float, float],
    radii: [float, ...],
    depths: [float, ...],
    plane: str = "Top",
    namePrefix: str = "Counterbore"
)
```

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `documentId` | string | Onshape document ID (28 hex characters) |
| `workspaceId` | string | Workspace ID (24 hex characters) |
| `elementId` | string | Part Studio element ID (24 hex characters) |
| `center` | array | [x, y] position in inches from origin |
| `radii` | array | Radii in inches, largest to smallest |
| `depths` | array | Cumulative depths in inches from top surface |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `plane` | string | `"Top"` | Sketch plane: "Top", "Front", or "Right" |
| `namePrefix` | string | `"Counterbore"` | Prefix for feature names |

## How It Works

### Internal Process

1. **Validate inputs**:
   - Check that radii and depths arrays have same length
   - Require at least 2 steps (minimum for counterbore)

2. **Sort steps**:
   - Sort by radius in descending order (largest first)
   - This ensures proper counterbore geometry

3. **Create features sequentially**:
   - For each (radius, depth) pair:
     - Create circular sketch on specified plane
     - Create extrude REMOVE operation to specified depth
   - Replace sketch ID placeholders with actual IDs

4. **Return results**:
   - List of all feature IDs created

### Example Feature Sequence

For a 3-level counterbore:
```python
create_stepped_extrude(
    center=[2, 2],
    radii=[0.75, 0.5, 0.375],
    depths=[0.5, 1.0, 1.5]
)
```

Creates:
1. Sketch with Ø1.5" circle at [2, 2]
2. Extrude REMOVE to 0.5" depth
3. Sketch with Ø1.0" circle at [2, 2]
4. Extrude REMOVE to 1.0" depth
5. Sketch with Ø0.75" circle at [2, 2]
6. Extrude REMOVE to 1.5" depth

Result: Counterbore with steps at 0.5", 1.0", and 1.5" depths.

## Usage Examples

### Example 1: Simple M6 Counterbore

```python
# M6 socket head cap screw counterbore
# Counterbore: 11mm diameter, 6.5mm deep
# Clearance: 6.6mm through-hole

create_stepped_extrude(
    documentId="3a37bea3a36351a5f3da417c",
    workspaceId="d22866472a0949b1a8061821",
    elementId="a3fc5500d9cfa40ca42957f1",
    center=[1.0, 1.0],
    radii=[0.433, 0.130],  # 11mm, 6.6mm in inches
    depths=[0.256, 0.787],  # 6.5mm, 20mm in inches
    plane="Top",
    namePrefix="M6_Counterbore"
)
```

### Example 2: 3-Level Bearing Seat

```python
# Bearing housing with snap ring groove
# Level 1: 55mm snap ring groove, 3mm deep
# Level 2: 47mm bearing seat, 15mm deep
# Level 3: 42mm through-hole, 25mm deep

create_stepped_extrude(
    documentId="3a37bea3a36351a5f3da417c",
    workspaceId="d22866472a0949b1a8061821",
    elementId="a3fc5500d9cfa40ca42957f1",
    center=[3.0, 2.0],
    radii=[1.083, 0.925, 0.827],  # 55mm, 47mm, 42mm
    depths=[0.118, 0.591, 0.984],  # 3mm, 15mm, 25mm
    plane="Front",
    namePrefix="Bearing_6204"
)
```

### Example 3: Multiple Counterbores (Bolt Pattern)

```python
# Create 4 M8 counterbores in corners of a plate
hole_positions = [
    [1.0, 1.0],
    [7.0, 1.0],
    [1.0, 5.0],
    [7.0, 5.0]
]

for i, pos in enumerate(hole_positions):
    create_stepped_extrude(
        documentId="3a37bea3a36351a5f3da417c",
        workspaceId="d22866472a0949b1a8061821",
        elementId="a3fc5500d9cfa40ca42957f1",
        center=pos,
        radii=[0.571, 0.177],  # 14.5mm counterbore, 9mm clearance
        depths=[0.335, 0.787],  # 8.5mm bore, 20mm through
        namePrefix=f"M8_Hole_{i+1}"
    )
```

## Common Use Cases

### 1. Fastener Counterbores

For recessing bolt/screw heads:
- Radii: [head_diameter/2, clearance_diameter/2]
- Depths: [head_height + clearance, total_depth]

### 2. Bearing Seats

For mounting bearings with retaining features:
- Radii: [retainer_diameter/2, bearing_OD/2, bearing_ID/2]
- Depths: [retainer_depth, bearing_depth, through_depth]

### 3. Insert Holes

For threaded inserts or press-fit inserts:
- Radii: [tool_access_diameter/2, insert_diameter/2]
- Depths: [tool_depth, insert_depth]

### 4. PCB Standoffs

For mounting circuit boards:
- Radii: [hex_tool_clearance/2, screw_clearance/2]
- Depths: [socket_depth, through_depth]

## Unit Conversions

All measurements are in **inches**. Convert from metric:

```python
# Metric to inches conversion
mm_to_inches = lambda mm: mm / 25.4

# Example: M6 counterbore in metric
counterbore_mm = 11.0  # mm
clearance_mm = 6.6     # mm
depth1_mm = 6.5        # mm
depth2_mm = 20.0       # mm

# Convert for API
radii = [mm_to_inches(counterbore_mm/2), mm_to_inches(clearance_mm/2)]
depths = [mm_to_inches(depth1_mm), mm_to_inches(depth2_mm)]

create_stepped_extrude(
    center=[1.0, 1.0],
    radii=radii,
    depths=depths
)
```

## Error Handling

### Common Errors

**Array Length Mismatch:**
```python
# ❌ Error: Different array lengths
radii=[0.5, 0.25]       # 2 radii
depths=[0.5, 1.0, 1.5]  # 3 depths
```

```python
# ✅ Correct: Same length
radii=[0.5, 0.375, 0.25]
depths=[0.5, 1.0, 1.5]
```

**Insufficient Steps:**
```python
# ❌ Error: Only 1 step
radii=[0.5]
depths=[1.0]
```

```python
# ✅ Correct: At least 2 steps
radii=[0.5, 0.25]
depths=[0.5, 1.0]
```

**Invalid Plane:**
```python
# ❌ Error: Invalid plane name
plane="XY"
```

```python
# ✅ Correct: Use standard plane names
plane="Top"  # or "Front" or "Right"
```

**Inverted Depths:**
Not an error, but creates unexpected geometry:
```python
# ⚠️ Warning: Depths should be ascending
depths=[2.0, 1.0, 0.5]  # Deepest first - unusual
```

```python
# ✅ Typical: Cumulative depths from surface
depths=[0.5, 1.0, 2.0]  # Increasing depth
```

## Design Considerations

### 1. Radii Order

Radii should typically be in **descending order** (largest first):
- Largest diameter at shallowest depth (counterbore/seat)
- Smallest diameter at deepest depth (through-hole/thread)

The tool automatically sorts by radius descending, but providing them in correct order improves readability.

### 2. Depth Values

Depths are **cumulative** from the sketch plane:
- First depth: distance from surface to first step
- Second depth: distance from surface to second step
- Third depth: distance from surface to third step

Not incremental between steps!

### 3. Clearances

Always add clearance to nominal dimensions:
- Fasteners: +0.5-1.0mm (0.02-0.04")
- Bearings: +0.05-0.1mm (0.002-0.004") for slip fit
- Press fits: -0.01-0.05mm (interference fit)
- 3D printing: +0.2-0.3mm (0.008-0.012") for dimensional accuracy

### 4. Wall Thickness

Ensure adequate material around holes:
- Minimum wall thickness: 1.5× largest hole diameter
- For structural loads: 2-3× hole diameter
- Check stress concentrations at diameter transitions

## Underlying Onshape API

The tool generates standard Onshape feature JSON:

### Sketch Feature
```json
{
  "btType": "BTFeatureDefinitionCall-1406",
  "feature": {
    "featureType": "sketch",
    "name": "Counterbore Sketch 1",
    "parameters": [
      {
        "btType": "BTMParameterQueryList-148",
        "parameterId": "sketchPlane",
        "queries": [/* plane reference */]
      }
      /* sketch entities */
    ]
  }
}
```

### Extrude Remove Feature
```json
{
  "btType": "BTFeatureDefinitionCall-1406",
  "feature": {
    "featureType": "extrude",
    "name": "Counterbore 1",
    "parameters": [
      {
        "parameterId": "entities",
        "queries": [/* sketch region reference */]
      },
      {
        "parameterId": "operationType",
        "value": "REMOVE"
      },
      {
        "parameterId": "depth",
        "expression": "0.5 in"
      }
    ]
  }
}
```

## Best Practices

### DO ✅

- Provide radii in descending order for clarity
- Use cumulative depths from surface
- Add appropriate clearances to nominal dimensions
- Name features with component specifications
- Verify wall thickness around holes
- Use variables for dimensions that may change
- Test fit with actual hardware when possible

### DON'T ❌

- Mix up radii and diameter (API uses radii)
- Use incremental depths between steps
- Forget to convert from metric to inches
- Create counterbores without adequate clearance
- Exceed material thickness with depth values
- Use exact nominal dimensions without tolerance

## Comparison with Manual Method

### Manual Approach (6+ API calls):
1. Create plane reference
2. Create sketch 1
3. Add circle 1
4. Create extrude 1 (REMOVE)
5. Create sketch 2
6. Add circle 2
7. Create extrude 2 (REMOVE)
8. ...repeat for each step

### Stepped Extrude (1 API call):
1. Call `create_stepped_extrude` with all parameters

Benefits:
- ✅ Fewer API calls (faster)
- ✅ Automatic feature naming
- ✅ Consistent positioning (all circles share center)
- ✅ Built-in validation
- ✅ Cleaner code

## Related Tools

- `create_hole` - Simple through-hole (single diameter)
- `create_sketch_circle` - Manual circle creation
- `create_extrude` - Manual extrude features
- `create_fillet` - Round sharp edges between steps
- `set_variable` - Create parametric counterbores

## References

- [Onshape Part Studio API](https://onshape-public.github.io/docs/api-intro/partstudios)
- [Extrude Feature Documentation](https://onshape-public.github.io/docs/api-intro/features)
- [ISO 4762 - Socket Head Cap Screws](https://www.iso.org/standard/34878.html)
- [ASME B18.3 - Socket Cap Screws](https://www.asme.org/codes-standards/find-codes-standards/b18-3-socket-cap-shoulder-set-screws-hex-metric-socket-head-cap-screws)

## Version History

- **v1.0** (2026-01-30): Initial release
  - Support for multiple diameter steps
  - Automatic sketch and extrude generation
  - Standard plane support (Top, Front, Right)
  - Parametric center positioning
  - Automatic feature naming

## Future Enhancements

Potential improvements:
- Variable support for parametric dimensions
- Automatic clearance calculation from fastener size
- Built-in fastener library (M3, M6, 1/4-20, etc.)
- Support for custom planes (not just Top/Front/Right)
- Chamfer/fillet options for diameter transitions
- Threaded hole representation
- Bolt pattern generation (circular, linear, grid)

---

**Need Help?**
- See: `knowledge_base/cad/counterbore_holes.md` for design guidance
- See: `knowledge_base/cad/cad_best_practices.md` for general CAD best practices
- Onshape forum: https://forum.onshape.com/
