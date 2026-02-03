# Snapshot Testing Guide

This directory contains tools for generating and validating JSON snapshots from Unity `.hhh` files for cross-platform .NET porting validation.

## Quick Start

### 1. Generate Snapshots from `.hhh` Files

```bash
python3 generate_snapshots.py <input_dir_or_file> <output_dir>
```

**Example:**
```bash
python3 generate_snapshots.py SampleMods/ snapshots/
```

This generates:
- `manifest.json` - File metadata (Unity version, platform, object count)
- `summary.json` - Type overview and object listing
- `objects/` - Individual JSON file for each object

### 2. Compare Your .NET Output Against Baseline

```bash
python3 compare_snapshots.py <baseline_snapshots> <dotnet_output>
```

**Example:**
```bash
# First: generate Python baseline
python3 generate_snapshots.py SampleMods/BambooCopter_head.hhh snapshots/python/

# Then: generate .NET output in same format
# (your .NET app should output JSON to: snapshots/dotnet/)

# Finally: compare
python3 compare_snapshots.py snapshots/python/ snapshots/dotnet/
```

## Snapshot Format

### File Structure
Each `.hhh` file generates a snapshot directory:

```
snapshots/
└── BambooCopter_head/
    ├── manifest.json              # File metadata
    ├── summary.json               # Type summary
    └── objects/
        ├── 000_GameObject_xxx.json
        ├── 001_Transform_xxx.json
        ├── 002_Mesh_xxx.json
        └── ... (one file per object)
```

### Object Snapshot Format

Each object snapshot contains:

```json
{
  "metadata": {
    "path_id": -8369783043922299965,
    "class_id": 4,
    "type": "Transform",
    "byte_start": 98736,
    "byte_size": 68
  },
  "data": {
    "m_Name": "object_name",
    "m_Property1": "value1",
    "m_Property2": ["array", "of", "values"],
    "nested_object": {
      "inner_property": "value"
    },
    "binary_data_field": {
      "_binary": true,
      "_format": "base64",
      "size": 262144,
      "data": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  }
}
```

### Binary Data Handling

Binary data (images, raw bytes) is stored as base64:

```json
{
  "_binary": true,
  "_format": "base64",
  "size": <bytes>,
  "data": "<base64 string>"
}
```

This allows:
- JSON compatibility (all data in text format)
- Exact byte-for-byte reproduction
- Size verification
- Rendering (three.js can parse base64 images directly)

## Understanding the `.resS` Files

Some texture data is stored in `.resS` ("resource serialized") files within the bundle:

```json
"m_StreamData": {
  "offset": 1276448,
  "size": 1398128,
  "path": "archive:/CAB-xxx/CAB-xxx.resS"
}
```

**This tells you:**
- Texture image data starts at offset 1276448 in the `.resS` file
- It's 1398128 bytes in size
- UnityPy handles extraction automatically

## Mesh Data Note

In these sample files, mesh data (vertices, triangles, normals) appears as empty arrays in the parsed output. This may be:
1. Runtime optimization in the export
2. Data stored differently in the `.resS` file
3. Expected behavior for certain asset bundles

The **material and texture data** is complete and renderable, which is critical for three.js validation.

## Validation Workflow

### Option 1: Three.js Visual Verification

Open `verify_snapshots_threejs.html` (if available) to:
- View 3D meshes with materials and textures
- Compare Python vs .NET output side-by-side
- Spot-check rendering accuracy

### Option 2: Automated Comparison

Run the comparison script to:
- Verify topology matches exactly (vertex/triangle counts)
- Apply floating-point tolerances for geometry
- Check material property values
- Report detailed diffs

### Expected Test Results

✅ **PASS if:**
- All objects present in both versions
- Topology matches exactly (same vertex/triangle counts)
- Material colors and properties match within tolerance
- Texture references resolve correctly
- GameObject hierarchies match

❌ **FAIL if:**
- Missing objects in .NET output
- Vertex counts differ
- Material properties don't match
- Texture metadata differs (size, format)

## For Your .NET Implementation

Your .NET parser should output JSON in the exact same format:

1. **File-level:** Create `<filename>/manifest.json`
2. **Summary:** Create `<filename>/summary.json`
3. **Objects:** For each object, create `<filename>/objects/<index>_<type>_<pathid>.json`

The structure must match the Python snapshots exactly for comparison to work.

## Questions?

Check the `SNAPSHOT_TESTING_PLAN.md` for detailed planning and architecture notes.
