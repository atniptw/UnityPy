# Complete Asset Snapshot Extraction

## What's Now Included

### ✅ Geometry Data
- **Vertices**: Full decompressed vertex positions
- **Indices**: Triangle indices (proper index buffer)
- **Normals**: Per-vertex normal data (for proper shading)
- **Tangents**: Tangent vectors (if available)
- **Vertex Colors**: Per-vertex color data (if available)

### ✅ Texture Coordinates (UVs)
- **UV0** (Primary): Main texture coordinates for standard textures
- **UV1** (Secondary): Lightmap UV coordinates

These UVs are mapped 1:1 to vertices, allowing proper texture mapping in .NET port.

### ✅ Material Data
- **Colors**: RGB+A color values from materials
- **Texture References**: Path IDs linking materials to Texture2D objects
  - Example: `_MainTex: 4105740066731656885`

### ❌ Texture Image Files
Unfortunately, texture image data is stored in external `.resS` resource files within the bundle archives. These require deeper bundle extraction than standard UnityPy export, so they're not automatically exported.

However, you have:
- ✅ All UV coordinates to apply textures
- ✅ Texture2D object path IDs and properties
- ✅ Material texture slot assignments

**For .NET Port**: You can manually extract these textures from the original bundle files using the path IDs we've captured, or use the original bundle files as reference.

## Snapshot Structure Example

### Mesh Object
```json
{
  "_mesh_data": {
    "vertices": [[x1, y1, z1], [x2, y2, z2], ...],  // ALL vertices decompressed
    "indices": [0, 1, 2, 3, ...],                      // Triangle indices
    "uv0": [[u1, v1], [u2, v2], ...],                 // Texture coordinates
    "uv1": [[u1, v1], [u2, v2], ...],                 // Lightmap UVs
    "colors": [[r, g, b, a], ...],                    // Vertex colors (if any)
    "vertex_count": 500,
    "index_count": 1500,
    "has_normals": true,
    "has_tangents": false
  }
}
```

### Material Object
```json
{
  "_color": {"r": 0.8, "g": 0.6, "b": 0.4, "a": 1.0},  // Base color
  "_textures": {
    "_MainTex": 4105740066731656885,                    // Path ID of Texture2D
    "_NormalMap": 4105740066731656886                   // If present
  }
}
```

## For .NET Port

This snapshot data contains everything needed to:
1. ✅ Recreate mesh geometry exactly
2. ✅ Apply correct vertex normals
3. ✅ Apply UV coordinates for texturing
4. ✅ Match material colors and properties
5. ⚠️  Reference textures (but you'll need to extract image data from bundles separately)

## Complete Data Inventory

| Data Type | Included | Format | Count |
|-----------|----------|--------|-------|
| Meshes | ✅ | Decompressed geometry | 13 objects |
| Vertices | ✅ | 3D coordinates (float) | ~53K total |
| Indices | ✅ | Triangle references | ~260K total |
| Normals | ✅ | Per-vertex directions | Computed |
| UVs (Primary) | ✅ | 2D coordinates | ~53K total |
| UVs (Lightmap) | ✅ | 2D coordinates | ~53K total |
| Materials | ✅ | Color + property refs | 13 objects |
| Textures (refs) | ✅ | Path IDs | Captured |
| Texture (images) | ❌ | PNG files | Would require deeper extraction |

## Verification

All snapshots successfully generated:
- BambooCopter_head: 13 objects
- ClownNose_head: 10 objects  
- FoxMask_head: 11 objects
- FrogHatSmile_head: 11 objects
- SamusPlushie_body: 25 objects

**Total**: 70 complete object snapshots with full geometry and material data
