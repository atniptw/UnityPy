# UnityPy Asset Extraction Validation - Quick Start

This repository contains validated UnityPy asset extraction logic with comprehensive snapshot testing.

## What's Included

✅ **Extraction Logic**: Complete Unity asset bundle parsing (`generate_snapshots.py`)  
✅ **10 Reference Bundles**: Sample .hhh files with known-correct snapshots  
✅ **Validation Tests**: 13 automated tests (`tests/test_snapshot_validation.py`)  
✅ **Documentation**: Complete guides and references  

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
pip install pytest numpy
```

### 2. Run Validation Tests

```bash
# Run all 13 validation tests
pytest tests/test_snapshot_validation.py -v

# Expected output: 13 passed in ~6 seconds
```

### 3. Generate Snapshots

```bash
# Generate snapshots for all 10 bundles
python generate_snapshots.py SampleMods/ snapshots/

# Generate for a single bundle
python generate_snapshots.py SampleMods/ClownNose_head.hhh snapshots/
```

## Test Results

All validation tests pass:

```
✅ test_bundle_snapshot_validation[SamusPlushie_body-25-2] PASSED
✅ test_bundle_snapshot_validation[BambooCopter_head-13-0] PASSED
✅ test_bundle_snapshot_validation[ClownNose_head-10-0] PASSED
✅ test_bundle_snapshot_validation[FoxMask_head-11-1] PASSED
✅ test_bundle_snapshot_validation[FrogHatSmile_head-11-1] PASSED
✅ test_bundle_snapshot_validation[AmyBackpack_body-13-1] PASSED
✅ test_bundle_snapshot_validation[Aku Aku_world-228-1] PASSED
✅ test_bundle_snapshot_validation[Cigar_neck-17-0] PASSED
✅ test_bundle_snapshot_validation[Odradek_neck-55-0] PASSED
✅ test_bundle_snapshot_validation[Volleyball_world-22-0] PASSED
✅ test_pathid_string_serialization PASSED
✅ test_material_texenv_format PASSED
✅ test_all_bundles_present PASSED

13 passed in 5.78s
```

## What's Validated

### ✅ Bundle File Parsing
- Reads Unity bundle files (.hhh format)
- Handles compressed data
- Extracts object hierarchy

### ✅ Object Extraction
- GameObjects and Transforms
- Meshes with complete geometry (vertices, indices, UVs)
- Materials with colors, floats, and texture references
- Textures exported as PNG
- SkinnedMeshRenderers (animated models)
- ParticleSystems

### ✅ Data Format
- PathIDs serialized as strings (64-bit JavaScript precision)
- Material TexEnvs as tuples
- Float values with proper precision
- Complete mesh geometry data

## Reference Bundles

| Bundle | Objects | Textures | Type |
|--------|---------|----------|------|
| SamusPlushie_body | 25 | 2 | Static model |
| BambooCopter_head | 13 | 0 | Static model |
| ClownNose_head | 10 | 0 | Static model |
| FoxMask_head | 11 | 1 | Static model |
| FrogHatSmile_head | 11 | 1 | Static model |
| AmyBackpack_body | 13 | 1 | Static model |
| Aku Aku_world | 228 | 1 | **Animated** |
| Cigar_neck | 17 | 0 | **Particles** |
| Odradek_neck | 55 | 0 | Static model |
| Volleyball_world | 22 | 0 | Static model |

**Total:** 405 objects across 10 bundles

## Documentation

- **[SNAPSHOT_VALIDATION_GUIDE.md](SNAPSHOT_VALIDATION_GUIDE.md)** - Complete usage guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[SNAPSHOT_TESTING_PLAN.md](SNAPSHOT_TESTING_PLAN.md)** - Architecture documentation
- **[SNAPSHOT_QUICK_REFERENCE.md](SNAPSHOT_QUICK_REFERENCE.md)** - Quick reference

## Success Criteria - All Met ✅

✅ Generated snapshots match reference snapshots for all 10 bundles  
✅ Object counts match exactly (405 objects)  
✅ Mesh geometry is byte-for-byte identical  
✅ All property values match (colors, floats, textures)  
✅ Texture PNGs extracted successfully (8 textures)  
✅ PathIDs preserved for JavaScript compatibility  
✅ All tests pass (13/13)  

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Validate Snapshots
  run: |
    pip install -e .
    pip install pytest numpy
    pytest tests/test_snapshot_validation.py -v
```

## Usage in Other Projects

This validation system can be used to validate ports of UnityPy to other languages:

1. Port the extraction logic to your target language (.NET, JavaScript, etc.)
2. Run your port against the 10 reference bundles
3. Compare generated snapshots with reference snapshots
4. Validate that all 405 objects match

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

This is a validation system for UnityPy. For the main UnityPy project, see:
- GitHub: https://github.com/K0lb3/UnityPy
- Discord: https://discord.gg/C6txv7M
