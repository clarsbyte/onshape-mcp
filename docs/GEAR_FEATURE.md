# Gear Feature Guide

The `create_gear` tool allows you to create spur gears with customizable parameters including number of teeth, module (tooth size), pressure angle, and more.

## Basic Usage

```python
await create_gear(
    documentId="your_doc_id",
    workspaceId="your_workspace_id",
    elementId="your_element_id",
    name="Drive Gear",
    numTeeth=24,
    module=2.0,
    thickness=0.5
)
```

## Parameters Explained

### Required Parameters

- **numTeeth**: Number of teeth on the gear (integer)
- **module**: Tooth size in millimeters (float)
  - Common values: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0
  - Larger module = bigger teeth
- **thickness**: Gear thickness in inches (float)

### Optional Parameters

- **pressureAngle**: Pressure angle in degrees (default: 20.0)
  - Standard options: 14.5°, 20°, 25°
  - 20° is the most common standard
- **boreDiameter**: Center hole diameter in inches (default: 0.0)
  - Set to 0 for no bore
  - Common: 0.25" (1/4"), 0.375" (3/8"), 0.5" (1/2")
- **centerX, centerY**: Gear center position in inches (default: 0, 0)
- **plane**: Sketch plane (default: "Front")
  - Options: "Front", "Top", "Right"

## Gear Calculations

### Pitch Diameter

The pitch diameter is calculated as:
```
pitch_diameter (mm) = module × numTeeth
pitch_diameter (inches) = (module × numTeeth) / 25.4
```

**Example:**
- 20-tooth gear with module 2.0
- Pitch diameter = 2.0 × 20 = 40mm = 1.575 inches

### Gear Ratios

When two gears mesh, the gear ratio is:
```
gear_ratio = teeth_on_driven_gear / teeth_on_driving_gear
```

**Example:**
- Driver: 12 teeth
- Driven: 48 teeth
- Ratio: 48 / 12 = 4:1 (driven gear turns 1/4 the speed, 4× the torque)

### Center Distance

For two meshing gears:
```
center_distance = (pitch_diameter_1 + pitch_diameter_2) / 2
```

**Example:**
- Gear 1: 20 teeth, module 2.0 → PD = 40mm
- Gear 2: 30 teeth, module 2.0 → PD = 60mm
- Center distance = (40 + 60) / 2 = 50mm = 1.968 inches

## Examples

### Example 1: Simple Gear Pair (2:1 Ratio)

```python
# Driver gear - 20 teeth
await create_gear(
    documentId=doc_id,
    workspaceId=ws_id,
    elementId=elem_id,
    name="Driver Gear",
    numTeeth=20,
    module=2.0,
    thickness=0.5,
    pressureAngle=20.0,
    boreDiameter=0.25,
    centerX=0.0,
    centerY=0.0
)

# Driven gear - 40 teeth (2:1 ratio)
# Center distance = (20*2 + 40*2) / 2 = 60mm = 2.362 inches
await create_gear(
    documentId=doc_id,
    workspaceId=ws_id,
    elementId=elem_id,
    name="Driven Gear",
    numTeeth=40,
    module=2.0,
    thickness=0.5,
    pressureAngle=20.0,
    boreDiameter=0.375,
    centerX=2.362,  # Pitch diameter sum / 2
    centerY=0.0
)
```

### Example 2: Gear Train (6:1 Reduction)

```python
# Stage 1: Driver (12T) to Intermediate (24T) = 2:1
await create_gear(
    documentId=doc_id,
    workspaceId=ws_id,
    elementId=elem_id,
    name="Input Gear",
    numTeeth=12,
    module=1.5,
    thickness=0.375,
    boreDiameter=0.25,
    centerX=0.0,
    centerY=0.0
)

await create_gear(
    documentId=doc_id,
    workspaceId=ws_id,
    elementId=elem_id,
    name="Intermediate Gear",
    numTeeth=24,
    module=1.5,
    thickness=0.375,
    boreDiameter=0.25,
    centerX=1.417,  # (12+24)*1.5/2 / 25.4
    centerY=0.0
)

# Stage 2: Intermediate (on same shaft, 12T) to Output (36T) = 3:1
# Total ratio: 2:1 × 3:1 = 6:1
await create_gear(
    documentId=doc_id,
    workspaceId=ws_id,
    elementId=elem_id,
    name="Output Gear",
    numTeeth=36,
    module=1.5,
    thickness=0.375,
    boreDiameter=0.375,
    centerX=2.834,  # Calculate from intermediate
    centerY=0.0
)
```

### Example 3: Gears with Different Modules (Don't mesh!)

```python
# This creates two gears that WON'T mesh together
# (different modules - for demonstration only)

await create_gear(
    documentId=doc_id,
    workspaceId=ws_id,
    elementId=elem_id,
    name="Large Module Gear",
    numTeeth=20,
    module=3.0,  # Large teeth
    thickness=0.5,
    centerX=0.0,
    centerY=0.0
)

await create_gear(
    documentId=doc_id,
    workspaceId=ws_id,
    elementId=elem_id,
    name="Small Module Gear",
    numTeeth=20,
    module=1.0,  # Small teeth
    thickness=0.5,
    centerX=3.0,
    centerY=0.0
)
```

## Important Notes

### Module Matching
**For gears to mesh, they MUST have the same module!**

✅ Correct: Gear1 (20T, 2.0 module) + Gear2 (30T, 2.0 module)
❌ Wrong: Gear1 (20T, 2.0 module) + Gear2 (30T, 1.5 module)

### Pressure Angle Matching
Gears should also have the same pressure angle to mesh properly.

### Simplified Profile
The current implementation creates a simplified circular gear profile. For production gears with proper involute tooth profiles:

1. Use this tool to generate the basic gear blank
2. Add involute tooth cuts using Onshape's Gear FeatureScript from the Feature Library
3. Or import a standard gear library

### Standard Modules (Metric)

Common metric module values (mm):
- 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0

### Diametral Pitch (Imperial)

If working in imperial units with diametral pitch (DP):
```
module (mm) ≈ 25.4 / DP
```

Common conversions:
- 20 DP ≈ 1.27 module
- 24 DP ≈ 1.06 module
- 32 DP ≈ 0.79 module
- 48 DP ≈ 0.53 module

## Gear Terminology

- **Module (m)**: Tooth size in millimeters (mm)
- **Pitch Diameter (PD)**: Diameter at which gears mesh (module × teeth)
- **Pressure Angle (PA)**: Angle of the tooth profile (typically 20°)
- **Addendum**: Height of tooth above pitch circle (usually = module)
- **Dedendum**: Depth of tooth below pitch circle (usually ≈ 1.25 × module)
- **Gear Ratio**: Speed/torque multiplication (driven_teeth / driver_teeth)

## Resources

- [Onshape Gear Feature Library](https://cad.onshape.com/documents/FeatureScripts) - For production involute gears
- [Gear Design Basics](https://khkgears.net/new/gear_knowledge/gear_technical_reference/)
- [Module vs Diametral Pitch](https://www.sdp-si.com/resources/elements-of-metric-gear-technology/)
