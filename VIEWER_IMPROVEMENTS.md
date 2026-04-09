# Snapshot Viewer - Latest Improvements

## Changes Made

### 1. **Removed Debug Red Cube**
- Deleted the test geometry that was cluttering the viewport
- Replaced with an axes helper (RGB axes at origin) for reference

### 2. **Fixed Camera for Micro-Scale Objects**
- **Before**: Attempted to scale vertex data, which corrupted the original mesh data
- **After**: Proper Three.js camera setup using documented best practices:
  - Camera `near` plane: `boxSize / 100` (1/100th of bounding box)
  - Camera `far` plane: `boxSize * 100` (100x the bounding box)
  - Uses `frameArea` formula to calculate proper camera distance
  - Works for objects at ANY scale (0.0025 units to 1000 units)

### 3. **Enhanced Mesh Visualization**
- **Edge highlighting**: Each mesh now shows subtle dark edges to highlight polygon structure
- **Better shading**: Smooth vertex normals for detail visibility
- **Double-sided rendering**: See meshes from all angles
- **Proper material**: Phong shading with specularity for depth perception

### 4. **Added Visualization Controls**
- **Wireframe Toggle**: Switch between solid and wireframe rendering
- **Show Normals Toggle**: Visualize vertex normals as blue lines (helps debug geometry)
- Toggles update all meshes in real-time

### 5. **Improved Statistics**
- Now calculates live vertex and triangle counts from loaded geometry
- Displays total mesh objects, vertices, and triangles at bottom-right
- Updates automatically as meshes are loaded/cleared

### 6. **Better UI**
- Added "Visualization" section with checkboxes for render modes
- Improved layout and spacing
- Info messages guide user interaction

## Technical Details

### Camera Near/Far Planes
For a bounding box of size `s`:
```javascript
camera.near = s / 100;  // Very close for tiny objects
camera.far = s * 100;   // Very far for large scenes
```

This allows viewing objects from 0.0001 units to 10,000 units without clipping.

### Edge Geometry
```javascript
const edges = new THREE.EdgesGeometry(geometry);
const lineSegments = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ ... }));
mesh.add(lineSegments);
```

Shows polygon edges without affecting the underlying geometry.

### Normal Visualization
Uses `THREE.VertexNormalsHelper` to display per-vertex normals as blue lines (scale: 0.02 units).

## What's Next

The viewer now properly displays:
- ✅ Decompressed mesh geometry from all bundles
- ✅ Proper camera framing for micro-scale objects
- ✅ Visual quality with lighting and shading
- ✅ Real-time statistics
- ✅ Debug visualization options

The data is fully preserved and unscaled - ready for .NET port comparison or further processing.
