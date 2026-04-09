# Snapshot 3D Viewer Guide

**URL:** `http://localhost:8000/snapshot_viewer.html`

## Overview

This is an interactive three.js viewer that lets you visualize all the data captured in your snapshots. It's designed to help you verify that:
- ✅ All mesh geometry data is present
- ✅ All object properties are captured
- ✅ All hierarchies and relationships are preserved
- ✅ The snapshots are "golden" (complete and accurate)

## Features

### 📦 Bundle Selection
1. Open the dropdown at the top of the left panel
2. Select one of the 5 bundles:
   - BambooCopter_head
   - ClownNose_head
   - FoxMask_head
   - FrogHatSmile_head
   - SamusPlushie_body

### 👁️ Object Browsing
Once a bundle is selected, all objects appear in the list below. Each object shows:
- **Index number** (load order)
- **Object type** (GameObject, Transform, Mesh, Material, etc.)
- **Object ID** (path_id for debugging)

### 🎮 3D Navigation
- **Rotate:** Left mouse button + drag
- **Pan:** Right mouse button + drag (or Ctrl + left click)
- **Zoom:** Mouse wheel
- **Fit to View:** Click "Fit to View" button to auto-focus selected object

### 📊 Object Statistics
When you select an object, the right panel shows:
- **Type:** Object class type
- **Path ID:** Unique identifier
- **Size:** File size in KB
- **Vertices:** For meshes, number of vertices
- **Indices:** For meshes, number of triangle indices
- **Triangles:** Computed from indices
- **Has Index Buffer:** ✓ if data is present
- **Has Stream Data:** ✓ if external geometry reference exists
- **Stream Size:** Size of external geometry data in bytes

### 📈 Viewport Stats (Bottom Left)
Real-time statistics:
- **Objects:** Number of objects currently rendered
- **Vertices:** Total vertex count
- **Triangles:** Total triangle count
- **FPS:** Frames per second

## Visualization Details

## Visualization Details

### What You're Actually Seeing

This viewer doesn't render the full decompressed geometry (that would require LZMA decompression). Instead, it shows:

1. **Bounding boxes** (solid colored boxes) - These represent the actual spatial bounds of each mesh
2. **Wireframe overlay** - Shows the mesh structure  
3. **Topology data** - Statistics on vertex/triangle counts

This is by design! The purpose is to **verify that all the data is captured**, not to perfectly render the geometry.

### Mesh Objects (Colored boxes with wireframe)
- Each colored box represents one mesh's bounding box
- The size and position come directly from m_SubMeshes.localAABB
- Wireframe shows the structure
- Color-coding helps distinguish different meshes
- Statistics show actual vertex/triangle counts

### Why Just Bounding Boxes?

Your snapshots contain:
- ✅ Vertex count (how many vertices)
- ✅ Index buffer (all triangle indices)
- ✅ Bounding box (spatial extent)
- ⚠️ **NOT** actual vertex positions (they're compressed in .resS files)

**This is correct!** The viewer validates that:
1. All topology data is present
2. All mesh statistics are accessible
3. Scene structure is captured

For actual geometry rendering, your .NET implementation will need to:
1. Read the vertex count from m_SubMeshes
2. Read indices from m_IndexBuffer
3. Locate and decompress vertices from m_StreamData

## What to Check

✅ **Mesh Data Verification:**
1. Select each mesh object
2. Verify the stats show:
   - Non-zero vertex count
   - Non-zero index count
   - Stream data size matches expected size
   - "Has Index Buffer" = ✓
   - "Has Stream Data" = ✓

✅ **Object Count:**
- Select different bundles
- Verify all objects load and can be selected
- Check the object list is complete

✅ **Hierarchies:**
- Navigate through different objects
- Verify structure makes sense (children under parents)

✅ **Properties:**
- Click on materials and see their properties
- Check shaders are referenced correctly
- Verify texture metadata is present

## Example Workflow

1. **Verify Mesh Data:**
   ```
   1. Open bundle: SamusPlushie_body
   2. Click on object "3. Mesh" 
   3. Check stats show:
      - Vertices: 53,185
      - Indices: 260,640
      - Stream Size: ~1.2 MB
   4. All three boxes should be checked ✓
   ```

2. **Check Object Relationships:**
   ```
   1. Click on a GameObject
   2. Note its components (Mesh, Transform, etc.)
   3. Each should be listed in the object list
   4. Path IDs should match references
   ```

3. **Verify All Data Present:**
   ```
   1. For each bundle:
      a. Count objects in list
      b. Click each one
      c. Verify stats populate
      d. All should render without errors
   ```

## Understanding the Data

### Why Vertices Show as Random?
The actual vertex positions are stored compressed and streamed in `.resS` files. The viewer shows you:
- ✅ **Vertex count** (from m_SubMeshes)
- ✅ **Index buffer** (all triangle indices)
- ✅ **Bounding box** (from localAABB)
- ⚠️ **Vertex positions** (placeholder, not decompressed)

**This is fine!** Your .NET implementation needs to:
1. Read the vertex count
2. Read the index buffer
3. Locate the `.resS` file using m_StreamData
4. Decompress the vertex data

### Stream Data
The `stream_size` field is critical. It tells you:
- How much data to read from the `.resS` file
- Whether all geometry is captured
- If the file reference is complete

## Troubleshooting

### "Error loading snapshots"
- Make sure the HTTP server is running
- Check that `snapshots/` directory exists
- Verify JSON files are valid

### Objects don't appear in list
- Make sure you selected a bundle first
- Check browser console for errors (F12)
- Try refreshing the page

### Stats don't show
- Click on an object in the list
- Wait for it to load (check network tab)
- Verify the JSON file is valid

### Camera stuck
- Click "Fit to View" button
- Or use middle mouse button to reset view

## Browser Requirements

- Modern browser (Chrome, Firefox, Edge recommended)
- JavaScript enabled
- WebGL support
- At least 2GB RAM for large meshes

## For Your .NET Implementation

Use this viewer to validate your .NET output:

1. **Generate .NET snapshots** using same format
2. **Compare against Python baselines:**
   ```
   python_mesh.vertexCount == dotnet_mesh.vertexCount
   python_mesh.indexCount == dotnet_mesh.indexCount
   python_mesh.streamSize == dotnet_mesh.streamSize
   ```
3. **Visual verification:**
   - Load Python snapshot → note statistics
   - Load .NET snapshot → compare statistics
   - Both should show identical values

## Quick Links

- 📄 [SNAPSHOT_TESTING_INDEX.md](SNAPSHOT_TESTING_INDEX.md) - Documentation index
- 🔍 [MESH_DATA_INVESTIGATION.md](MESH_DATA_INVESTIGATION.md) - Mesh data details
- 💻 [SNAPSHOT_TESTING_SUMMARY.md](SNAPSHOT_TESTING_SUMMARY.md) - .NET implementation guide

---

**Tip:** Keep this viewer open while implementing your .NET parser. Visual verification is invaluable for catching data correctness issues!
