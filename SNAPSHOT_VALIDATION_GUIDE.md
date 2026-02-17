# UnityPy Snapshot Validation Guide

This guide explains how to validate the UnityPy asset extraction logic using the comprehensive snapshot validation tests.

## Overview

The snapshot validation system ensures that UnityPy correctly extracts Unity asset bundles (.hhh files) and generates accurate JSON snapshots. It validates:

- Object counts per bundle
- Mesh vertex/index/UV counts
- Material property values (colors, floats, textures)
- Texture extraction results
- Path ID serialization as strings (for JavaScript 64-bit precision)
- Material TexEnv tuple format
- All 10 reference bundles

## Prerequisites

```bash
# Install UnityPy with dependencies
pip install -e .

# Install test dependencies
pip install pytest numpy
```

## Running Tests

### Run All Validation Tests

```bash
pytest tests/test_snapshot_validation.py -v
```

This runs 13 tests:
- 10 bundle validation tests (one per reference bundle)
- PathID string serialization test
- Material TexEnv format test
- Bundle presence test

### Run Specific Bundle Test

```bash
# Test a specific bundle
pytest "tests/test_snapshot_validation.py::test_bundle_snapshot_validation[ClownNose_head-10-0]" -v

# Test the large animated bundle
pytest "tests/test_snapshot_validation.py::test_bundle_snapshot_validation[Aku Aku_world-228-1]" -v
```

### Run PathID Validation Only

```bash
pytest tests/test_snapshot_validation.py::test_pathid_string_serialization -v
```

### Run Material Validation Only

```bash
pytest tests/test_snapshot_validation.py::test_material_texenv_format -v
```

## Test Structure

### Bundle Validation Tests

Each bundle test validates:

1. **Metadata**: Object count, Unity version, platform, endianness
2. **Summary**: Total objects, object type counts
3. **Textures**: Texture count and extraction
4. **PathID Format**: All PathIDs stored as strings
5. **Individual Objects**: Sample validation of first, middle, and last objects
6. **Mesh Geometry**: Vertex/index/UV counts match
7. **Material Properties**: Colors, floats, and texture references match

### PathID String Serialization Test

Validates that all PathID fields are serialized as strings to preserve 64-bit precision in JavaScript:
- Checks manifest.json
- Checks summary.json
- Checks object files
- Validates both positive and negative 64-bit integers

### Material TexEnv Format Test

Validates that Material TexEnvs are properly formatted as tuples (lists in JSON):
- Each TexEnv is a 2-element list: `[name, data]`
- Example: `["_MainTex", {"m_Texture": {"m_PathID": "12345"}, ...}]`

## Reference Bundles

The validation system tests against 10 reference bundles:

| Bundle | Objects | Textures | Notes |
|--------|---------|----------|-------|
| SamusPlushie_body | 25 | 2 | Static body model |
| BambooCopter_head | 13 | 0 | Static head model |
| ClownNose_head | 10 | 0 | Static head model |
| FoxMask_head | 11 | 1 | Static head model |
| FrogHatSmile_head | 11 | 1 | Static head model |
| AmyBackpack_body | 13 | 1 | Static body model |
| Aku Aku_world | 228 | 1 | Animated (SkinnedMeshRenderer) |
| Cigar_neck | 17 | 0 | Particle system |
| Odradek_neck | 55 | 0 | Static neck model |
| Volleyball_world | 22 | 0 | Static world object |

## Snapshot Directory Structure

```
snapshots/{bundle_name}/
  ├── manifest.json          # Bundle metadata
  ├── summary.json           # Object type counts
  ├── textures_index.json    # (if textures present)
  ├── objects/
  │   ├── 000_Type_PathID.json
  │   ├── 001_Type_PathID.json
  │   └── ...
  └── textures/              # (if textures present)
      ├── tex_PathID.png
      └── ...
```

## Generating New Snapshots

To regenerate snapshots for all bundles:

```bash
python generate_snapshots.py SampleMods/ snapshots/
```

To generate a snapshot for a single bundle:

```bash
python generate_snapshots.py SampleMods/ClownNose_head.hhh snapshots/
```

## What the Tests Validate

### 1. Object Counts
✅ Total object count matches expected count  
✅ Object type counts match (GameObjects, Transforms, Meshes, etc.)

### 2. Mesh Geometry
✅ Vertex count matches  
✅ Index count matches  
✅ UV coordinate arrays match in length  
✅ Geometry info metadata present

### 3. Material Properties
✅ Color values match (within float tolerance)  
✅ Float property values match (within float tolerance)  
✅ Texture references match  
✅ Texture PathIDs are strings  
✅ TexEnvs are tuples (2-element lists)

### 4. Texture Extraction
✅ Texture count matches expected  
✅ Textures extracted as PNG files  
✅ Texture index file present when textures exist

### 5. PathID Serialization
✅ All PathID fields stored as strings  
✅ Handles 64-bit negative integers correctly  
✅ Preserves precision for JavaScript compatibility

## Edge Cases Handled

The validation tests ensure proper handling of:

1. **Large PathIDs**: Negative 64-bit integers (e.g., `-8911878726397676121`)
2. **Missing Textures**: Some bundles have no textures
3. **SkinnedMeshRenderers**: Animated models with bones (Aku Aku_world)
4. **ParticleSystems**: Different structure from MeshRenderers (Cigar_neck)
5. **Empty Texture References**: Materials without textures
6. **Float Precision**: Colors and floats compared with tolerance

## Success Criteria

All tests pass means:

✅ Generated snapshots match reference snapshots for all 10 bundles  
✅ Object counts match exactly  
✅ Mesh geometry is identical  
✅ All property values match (within tolerance)  
✅ Texture PNGs extracted successfully  
✅ PathIDs preserved for JavaScript compatibility

## Troubleshooting

### Test Fails with "No module named 'numpy'"

```bash
pip install numpy
```

### Test Fails with PathID Mismatch

Check that PathIDs are being serialized as strings in `generate_snapshots.py`:
- The `convert_pathids_to_strings()` function should be called
- The `serialize_value()` function should handle PathID keys

### Test Fails with Geometry Mismatch

Ensure MeshHandler is correctly extracting geometry:
- Check `extract_mesh_geometry()` function
- Verify vertex/index buffer extraction
- Check UV coordinate handling

### Texture Extraction Fails

Ensure texture dependencies are installed:
```bash
pip install Pillow texture2ddecoder etcpak astc-encoder-py
```

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Run Snapshot Validation Tests
  run: |
    pip install -e .
    pip install pytest numpy
    pytest tests/test_snapshot_validation.py -v
```

## Further Reading

- [SNAPSHOT_TESTING_PLAN.md](SNAPSHOT_TESTING_PLAN.md) - Complete architecture
- [SNAPSHOT_QUICK_REFERENCE.md](SNAPSHOT_QUICK_REFERENCE.md) - Quick start guide
- [SNAPSHOT_TESTING_README.md](SNAPSHOT_TESTING_README.md) - Format specification
- [MESH_DATA_INVESTIGATION.md](MESH_DATA_INVESTIGATION.md) - Mesh data deep dive
