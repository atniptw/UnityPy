# Material Colors Implementation

## Changes Made

### 1. **Snapshot Generator (generate_snapshots.py)**
Added material color extraction:
- For each Material object, captures `m_SavedProperties.m_Colors._Color` (RGBA values)
- Stores in snapshot as `_color` field
- Regenerated all 5 bundles with color data

### 2. **Snapshot Viewer (snapshot_viewer.html)**

**Added Material Registry:**
```javascript
let materialRegistry = {};  // pathId -> {r, g, b, a}
```

**Updated Bundle Rendering:**
- Collects all Material objects and builds materialRegistry with their colors
- Passes allObjects to renderMesh() so it can look up material references

**Updated Mesh Rendering:**
- Tries to find the MeshRenderer that uses the mesh
- Looks up the material reference from MeshRenderer.m_Materials
- Uses actual asset color instead of random color
- Fallback: uses pseudo-random but consistent color based on mesh name
- Creates THREE.MeshPhongMaterial with proper color and emissive

## What You'll See Now

The viewer now displays:
- ✅ Actual asset colors from Unity materials
- ✅ Proper shading with material-based emissive (darker tones)
- ✅ Polygon detail with edge highlighting
- ✅ Consistent colors across loads (based on material data)

## Technical Details

**Material Color Lookup Chain:**
1. Load all objects in bundle
2. Extract Material objects → materialRegistry[pathId] = {r, g, b, a}
3. For each Mesh:
   - Find MeshRenderer in allObjects
   - Get m_Materials[0].m_PathID
   - Look up materialRegistry[matPathId]
   - Use real color if found, else fallback

**Color Application:**
```javascript
color = new THREE.Color(materialColor.r, materialColor.g, materialColor.b);
emissive = color.multiplyScalar(0.2);  // Dark version for emissive glow
```

This creates proper depth and material appearance without textures.

## Next Steps

The viewer now shows actual asset geometry AND colors. You could further enhance with:
- Texture extraction and UV mapping (if texture data is available)
- Metallic/specular properties from material floats
- Normal maps for surface detail
- Transparency/alpha blending setup
