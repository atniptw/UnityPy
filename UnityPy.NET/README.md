# UnityPy .NET Port

This directory contains a .NET port of UnityPy's asset extraction logic for reading Unity bundle files (.hhh) and generating JSON snapshots.

## Project Structure

```
UnityPy.NET/
├── UnityPyPort.sln              # Solution file
└── UnityPyPort/
    ├── UnityPyPort.csproj       # Project file
    ├── Program.cs               # Entry point
    ├── EndianBinaryReader.cs    # Binary reader with endian support
    ├── BundleFile.cs            # Bundle file parser
    ├── SerializedFile.cs        # Serialized asset file representation
    └── SnapshotGenerator.cs     # JSON snapshot generator
```

## Current Status

### ✅ Implemented
- Basic project structure
- EndianBinaryReader for reading binary data with endianness support
- Partial BundleFile parser for UnityFS format
- Basic snapshot generator framework
- NuGet dependencies:
  - System.Text.Json (JSON serialization)
  - SixLabors.ImageSharp (image processing)
  - K4os.Compression.LZ4 (LZ4 decompression)

### 🚧 In Progress / Needs Completion
1. **BundleFile.cs**: Complete UnityFS block reading and decompression
   - Fix LZ4 decompression implementation
   - Handle LZMA compression
   - Read and parse SerializedFile data from blocks

2. **SerializedFile.cs**: Implement full serialized file parsing
   - Read object headers and type trees
   - Parse object data
   - Extract different Unity object types (GameObject, Transform, Mesh, Material, etc.)

3. **Object Readers**: Implement parsers for Unity object types
   - GameObject
   - Transform
   - Mesh (with geometry extraction)
   - Material (with colors, floats, textures)
   - Texture2D (with PNG export)
   - MeshRenderer / SkinnedMeshRenderer
   - ParticleSystem
   - AnimationClip

4. **SnapshotGenerator.cs**: Complete snapshot generation
   - Extract all objects from bundles
   - Generate manifest.json with correct metadata
   - Generate summary.json with object counts
   - Generate individual object JSON files
   - Extract and save textures as PNG
   - Generate textures_index.json

5. **Path ID Serialization**: Ensure all PathIDs are serialized as strings (for JavaScript 64-bit precision)

6. **Material TexEnvs**: Ensure proper tuple format: `[name, {m_Texture, m_Scale, m_Offset}]`

## Building and Running

### Prerequisites
- .NET 8.0 SDK or later

### Build
```bash
cd UnityPy.NET
dotnet build
```

### Run
```bash
cd UnityPyPort
dotnet run -- <input_path> <output_path>

# Example:
dotnet run -- ../../SampleMods/ClownNose_head.hhh ../../snapshots/
```

## Validation

The .NET port must generate identical JSON snapshots to the Python implementation. Use the validation tests in `/tests/test_snapshot_validation.py` to verify:

```bash
# Generate snapshots with .NET port
cd UnityPy.NET/UnityPyPort
dotnet run -- ../../SampleMods/ /tmp/dotnet_snapshots/

# Compare with Python implementation
cd ../..
python -m pytest tests/test_snapshot_validation.py -v
```

## Reference Bundles

10 test bundles are available in `SampleMods/`:
1. SamusPlushie_body (25 objects, 2 textures)
2. BambooCopter_head (13 objects, 0 textures)
3. ClownNose_head (10 objects, 0 textures)
4. FoxMask_head (11 objects, 1 texture)
5. FrogHatSmile_head (11 objects, 1 texture)
6. AmyBackpack_body (13 objects, 1 texture)
7. Aku Aku_world (228 objects, 1 texture, animated)
8. Cigar_neck (17 objects, 0 textures, particles)
9. Odradek_neck (55 objects, 0 textures)
10. Volleyball_world (22 objects, 0 textures)

Reference snapshots are in `snapshots/{bundle_name}/`.

## Success Criteria

✅ Generated snapshots match reference snapshots for all 10 bundles  
✅ Object counts match exactly (405 objects total)  
✅ Mesh geometry is byte-for-byte identical  
✅ All property values match (colors, floats, textures)  
✅ Texture PNGs match original extractions (8 textures)  
✅ PathIDs serialized as strings for JavaScript compatibility  
✅ Material TexEnvs properly formatted as tuples  

## Implementation Notes

This port is based on the Python UnityPy library. Key files to reference:

### Python Reference
- `UnityPy/environment.py` - Bundle loading
- `UnityPy/files/BundleFile.py` - Bundle file format
- `UnityPy/files/SerializedFile.py` - Asset file format
- `UnityPy/files/ObjectReader.py` - Object parsing
- `UnityPy/helpers/MeshHelper.py` - Mesh geometry extraction
- `generate_snapshots.py` - Snapshot generation logic

### Critical Implementation Details

1. **Endianness**: Unity bundles can be big-endian or little-endian
2. **Path IDs**: Must be serialized as strings (64-bit integers exceed JavaScript's safe integer range)
3. **Compression**: Support None, LZMA, LZ4, and LZ4HC
4. **Type Trees**: Object structure metadata that varies by Unity version
5. **Mesh Data**: May be compressed, streamed, or in separate .resS files
6. **Textures**: Various formats (DXT, ETC, ASTC, etc.) need conversion to PNG

## Next Steps

To complete the port:

1. **Fix LZ4 Decompression**: The current implementation has issues with the LZ4 block decompression. Need to handle Unity's specific LZ4 format.

2. **Implement SerializedFile Parser**: Create a full parser for reading Unity's serialized file format, including headers, type trees, and object data.

3. **Add Object Type Parsers**: Implement readers for each Unity object type (GameObject, Mesh, Material, etc.) that extract data matching the Python implementation.

4. **Complete Snapshot Generator**: Ensure JSON output matches the Python implementation exactly, including field names, data types, and structure.

5. **Add Texture Export**: Implement texture decoding and PNG export functionality.

6. **Comprehensive Testing**: Test against all 10 reference bundles and validate output matches.

## Resources

- [UnityPy GitHub](https://github.com/K0lb3/UnityPy) - Original Python implementation
- [AssetStudio](https://github.com/Perfare/AssetStudio) - C# Unity asset tool (alternative reference)
- [Unity Documentation](https://docs.unity3d.com/) - Unity asset format documentation

## License

Same as UnityPy (MIT License)
