# Counterbore Holes in Onshape

## Overview

A counterbore hole (also called a stepped hole) is a hole with multiple diameters that decrease as the hole goes deeper into the part. These are commonly used for:
- Recessing bolt heads or screw heads below the surface
- Creating bearing seats
- Installing inserts or bushings
- Socket head cap screws (SHCS) clearance

![Example of counterbore holes](../images/counterbore_example.png)

## Anatomy of a Counterbore Hole

A typical counterbore hole has:
1. **Counterbore diameter** (largest) - Top level, shallow depth
2. **Clearance diameter** (medium) - Middle level, moderate depth
3. **Thread diameter** (smallest) - Bottom level, deepest

Example for M6 socket head cap screw:
- Counterbore: Ø12mm × 6mm deep (head clearance)
- Clearance: Ø6.6mm × 15mm deep (shaft clearance)
- Thread: Ø5mm × 20mm deep (tap drill)

## Creating Counterbore Holes in Onshape

### Method 1: Stepped Extrude (Recommended for Multiple Steps)

The `create_stepped_extrude` tool creates counterbore holes automatically by:
1. Creating circular sketches for each diameter
2. Extruding each as a REMOVE operation to the specified depth
3. Properly ordering from largest to smallest diameter

**Parameters:**
- `center`: [x, y] position in inches
- `radii`: List of radii from largest to smallest (in inches)
- `depths`: List of cumulative depths (in inches)
- `plane`: Sketch plane (default: "Top")

**Example - 3-Level Counterbore:**
```python
create_stepped_extrude(
    documentId="...",
    workspaceId="...",
    elementId="...",
    center=[2, 2],
    radii=[0.75, 0.5, 0.375],  # Largest to smallest
    depths=[0.7874, 1.5748, 2.362],  # 2cm, 4cm, 6cm cumulative
    plane="Top",
    namePrefix="Counterbore"
)
```

This creates:
- Step 1: Ø1.5" circle, REMOVE to 0.7874" depth
- Step 2: Ø1.0" circle, REMOVE to 1.5748" depth
- Step 3: Ø0.75" circle, REMOVE to 2.362" depth

### Method 2: Manual Sketch + Multiple Extrudes

For more control or complex geometries:

1. **Create base solid** (if not exists)
2. **For each step:**
   - Create circle sketch on appropriate plane
   - Extrude REMOVE to specific depth

**Example:**
```python
# Step 1: Largest diameter (counterbore)
sketch1 = create_sketch_circle(
    center=[2, 2],
    radius=0.236,  # 6mm counterbore
    plane="Top"
)
create_hole(
    sketchFeatureId=sketch1.id,
    depth=0.236  # 6mm deep
)

# Step 2: Medium diameter (clearance)
sketch2 = create_sketch_circle(
    center=[2, 2],
    radius=0.130,  # 3.3mm clearance
    plane="Top"
)
create_hole(
    sketchFeatureId=sketch2.id,
    depth=0.591  # 15mm deep
)

# Step 3: Smallest diameter (thread)
sketch3 = create_sketch_circle(
    center=[2, 2],
    radius=0.098,  # 2.5mm tap drill
    plane="Top"
)
create_hole(
    sketchFeatureId=sketch3.id,
    depth=0.787  # 20mm deep
)
```

## Best Practices

### 1. Design for Manufacturing

**Standard Counterbore Dimensions:**
- Follow ISO 7379 or ASME B18.3 for standard counterbores
- Use standard drill sizes when possible
- Allow adequate wall thickness around holes (typically 1.5× hole diameter minimum)

**Material Considerations:**
- Metals: Can use sharp transitions between diameters
- Plastics: Add small radius (0.5-1mm) at diameter transitions to reduce stress
- 3D Printed: Increase clearances by 0.2-0.3mm for dimensional accuracy

### 2. Ordering and Depth

**Depths should be cumulative, not incremental:**
- ✅ Correct: [0.5, 1.0, 1.5] - each depth from top surface
- ❌ Wrong: [0.5, 0.5, 0.5] - would create all at same depth

**Radii should be in descending order:**
- ✅ Correct: [0.75, 0.5, 0.375] - largest to smallest
- ❌ Wrong: [0.375, 0.5, 0.75] - would create inverted counterbore

### 3. Nomenclature

Name counterbore features clearly:
- "M6 Counterbore" - includes fastener size
- "Bearing Seat 6204" - includes bearing part number
- "Insert M8x1.25" - includes insert specifications

### 4. Variables and Parametric Design

Use variables for counterbores that may change:

```python
# Define fastener variables
set_variable(name="boltDiameter", expression="0.25 in")
set_variable(name="headDiameter", expression="#boltDiameter * 1.5")
set_variable(name="headHeight", expression="#boltDiameter * 0.7")
set_variable(name="boreDepth", expression="#headHeight + 0.03 in")  # +0.03" clearance

# Use in counterbore
create_stepped_extrude(
    radii=["#headDiameter / 2", "#boltDiameter / 2"],
    depths=["#boreDepth", "#boreDepth + 0.5 in"]
)
```

## Common Mistakes to Avoid

### ❌ Insufficient Clearance
```python
# Too tight - bolt head won't fit
radii=[0.236, 0.130]  # Exactly M6 head diameter
depths=[0.236, 1.0]   # Exactly M6 head height
```

### ✅ Proper Clearance
```python
# Add 0.5mm (0.02") clearance
radii=[0.256, 0.138]  # M6 + clearance
depths=[0.256, 1.0]   # M6 + clearance
```

### ❌ Inverted Depths
```python
# Wrong - deepest first
depths=[2.0, 1.0, 0.5]
```

### ✅ Correct Depths
```python
# Correct - cumulative from surface
depths=[0.5, 1.0, 2.0]
```

### ❌ Inconsistent Array Lengths
```python
# Error - mismatched arrays
radii=[0.5, 0.375]
depths=[0.5, 1.0, 1.5]  # 3 depths, only 2 radii!
```

### ✅ Matched Arrays
```python
# Correct - same length
radii=[0.5, 0.375, 0.25]
depths=[0.5, 1.0, 1.5]
```

## Standard Fastener Counterbores

### Metric Socket Head Cap Screws (ISO 4762)

| Screw Size | Clearance Ø | Counterbore Ø | Counterbore Depth |
|------------|-------------|---------------|-------------------|
| M3         | 3.4mm       | 6.5mm         | 3.5mm             |
| M4         | 4.5mm       | 8.0mm         | 4.5mm             |
| M5         | 5.5mm       | 9.5mm         | 5.5mm             |
| M6         | 6.6mm       | 11.0mm        | 6.5mm             |
| M8         | 9.0mm       | 14.5mm        | 8.5mm             |
| M10        | 11.0mm      | 17.5mm        | 10.5mm            |

### Imperial Socket Head Cap Screws (ASME B18.3)

| Screw Size | Clearance Ø | Counterbore Ø | Counterbore Depth |
|------------|-------------|---------------|-------------------|
| #6-32      | 0.149"      | 0.281"        | 0.138"            |
| #8-32      | 0.177"      | 0.344"        | 0.164"            |
| 1/4-20     | 0.266"      | 0.469"        | 0.250"            |
| 5/16-18    | 0.328"      | 0.562"        | 0.312"            |
| 3/8-16     | 0.391"      | 0.656"        | 0.375"            |
| 1/2-13     | 0.516"      | 0.875"        | 0.500"            |

## Real-World Examples

### Example 1: Mounting Plate with M6 Counterbores

```python
# Base plate 200mm × 100mm × 10mm
base_sketch = create_sketch_rectangle(
    corner1=[0, 0],
    corner2=[7.874, 3.937],  # 200mm × 100mm
    plane="Top"
)
create_extrude(
    sketchFeatureId=base_sketch.id,
    depth=0.394,  # 10mm
    operationType="NEW"
)

# M6 counterbore pattern (4 corners)
hole_positions = [
    [0.787, 0.787],    # 20mm from edges
    [7.087, 0.787],
    [0.787, 3.150],
    [7.087, 3.150]
]

for pos in hole_positions:
    create_stepped_extrude(
        center=pos,
        radii=[0.433, 0.130],  # 11mm counterbore, 6.6mm clearance
        depths=[0.256, 0.394],  # 6.5mm bore, through 10mm plate
        namePrefix=f"M6_Counterbore_{pos[0]}_{pos[1]}"
    )
```

### Example 2: Bearing Housing with Stepped Bore

```python
# Bearing 6204 (20mm ID, 47mm OD, 14mm width)
# Housing bore: 47.1mm fit, 52mm counterbore for snap ring

create_stepped_extrude(
    center=[2.0, 2.0],
    radii=[1.024, 0.925],  # 52mm counterbore, 47mm bearing seat
    depths=[0.118, 0.669],  # 3mm snap ring groove, 17mm total depth
    plane="Top",
    namePrefix="Bearing_6204_Seat"
)
```

### Example 3: PCB Standoff Counterbore (M3)

```python
# Counterbore for M3 standoff with hex socket access
create_stepped_extrude(
    center=[0.5, 0.5],
    radii=[0.236, 0.067],  # 6mm hex socket clearance, 3.4mm screw clearance
    depths=[0.197, 0.394],  # 5mm counterbore, through 10mm base
    plane="Top",
    namePrefix="M3_Standoff_Counterbore"
)
```

## Testing and Validation

### Clearance Check

After creating counterbores:
1. Measure actual fastener dimensions
2. Verify clearances in model (Measure tool)
3. Check wall thickness around holes
4. Verify depth allows full thread engagement

### Print Test Piece

For 3D printing or machined parts:
1. Create test piece with all counterbore sizes
2. Verify fit with actual hardware
3. Adjust tolerances if needed
4. Document working clearances

## Resources

### Standards
- ISO 4762: Socket head cap screws
- ISO 7379: Counterbored holes
- ASME B18.3: Socket cap screws
- ASME B18.2.1: Clearance holes

### Tools
- [Fastener clearance calculator](https://www.gewinde-normen.de/en/)
- [Drill size charts](https://www.machiningdoctor.com/charts/drill-size-chart/)
- [Bearing specifications](https://www.skf.com/)

### Further Reading
- Onshape Learning Center: Hole Features
- Machinery's Handbook: Section on holes and counterbores
- GD&T standards for hole positioning tolerance

## Key Takeaways

✅ **DO:**
- Use cumulative depths from top surface
- Order radii from largest to smallest
- Add appropriate clearances (0.5-1mm typical)
- Name features with fastener/component specifications
- Consider manufacturing method and material
- Verify fit with actual hardware when possible

❌ **DON'T:**
- Use incremental depths (each depth is from origin)
- Reverse radius order (always largest first)
- Use exact fastener dimensions (always add clearance)
- Create holes without checking wall thickness
- Forget to account for manufacturing tolerances

The `create_stepped_extrude` tool makes creating professional counterbore holes fast and consistent!
