# Quick Reference: Snapshot Testing Setup

## 📊 What You Have Now

| Item | Status | Location |
|------|--------|----------|
| Snapshot Generator | ✅ Ready | `generate_snapshots.py` |
| Python Baselines | ✅ Generated | `snapshots/` (8.1 MB, 80 JSON files) |
| Usage Documentation | ✅ Complete | `SNAPSHOT_TESTING_README.md` |
| Architecture Guide | ✅ Complete | `SNAPSHOT_TESTING_PLAN.md` |
| Implementation Summary | ✅ Complete | `SNAPSHOT_TESTING_SUMMARY.md` |

## 🎯 Three Phase Testing Plan

### Phase 1: Review Baselines
```bash
# Explore what was captured
cat snapshots/SamusPlushie_body/manifest.json
cat snapshots/SamusPlushie_body/summary.json
cat snapshots/SamusPlushie_body/objects/001_Transform_*.json | head -30
```

### Phase 2: Implement Your .NET Parser
Your .NET code should:
1. Read `.hhh` files using your asset bundle reader
2. For each object, parse it and collect all properties
3. Output JSON matching this format:

```json
{
  "metadata": {
    "path_id": <int64>,
    "class_id": <int>,
    "type": "<type_name>"
  },
  "data": {
    // Full parsed object data
  }
}
```

### Phase 3: Validate Results
```bash
# Generate .NET snapshots (your code outputs them)
# Then compare:
python3 compare_snapshots.py snapshots/SamusPlushie_body snapshots_dotnet/SamusPlushie_body
```

## 📁 File Breakdown

### 5 Sample `.hhh` Files
- **SamusPlushie_body.hhh** (1.5M) - Complex: 25 objects, 3 meshes, 2 textures
- **FrogHatSmile_head.hhh** (289K) - Medium: 11 objects, 2 meshes, 2 textures  
- **FoxMask_head.hhh** (211K) - Medium: 11 objects, 2 meshes, 2 textures
- **ClownNose_head.hhh** (28K) - Small: 10 objects, 1 mesh, 0 textures
- **BambooCopter_head.hhh** (35K) - Small: 13 objects, 1 mesh, 0 textures

### Generated Snapshots (8.1 MB total)
- **manifest.json** per file - Metadata
- **summary.json** per file - Object type counts
- **80 JSON files** - One per object
  - Contains all parsed properties
  - Base64-encoded binary data
  - Complete rendering information

## 🔍 What Gets Tested

### ✅ Automatic Validation (What We Check)
- Object count matches
- All object types present
- All properties populated
- Data types correct
- Floating-point values within tolerance
- Texture metadata correct
- Material properties match

### 🎨 Visual Validation (Optional)
- Create a three.js viewer
- Load and render with both Python and .NET output
- Side-by-side comparison
- Verify rendering matches

## 💡 Key Files to Review

1. **Start here:** `SNAPSHOT_TESTING_README.md` - 5-minute read
2. **Implementation guide:** `SNAPSHOT_TESTING_PLAN.md` - Full architecture
3. **Example snapshots:** Browse `snapshots/BambooCopter_head/objects/` 

## 🚀 Quick Commands

```bash
# Generate snapshots (for new files)
python3 generate_snapshots.py SampleMods/YourFile.hhh snapshots/YourFile/

# Regenerate all
python3 generate_snapshots.py SampleMods/ snapshots/

# Check what was captured
find snapshots/ -name "summary.json" -exec cat {} \;

# See snapshot size breakdown
du -h snapshots/* | sort -h

# Count objects by type
grep -h '"type"' snapshots/*/objects/*.json | sort | uniq -c
```

## 📋 Snapshot Content Reference

### GameObject Example
```json
{
  "metadata": {"path_id": -8911878726397676121, "type": "GameObject"},
  "data": {
    "m_Name": "Cube.027",
    "m_Component": [
      {"component": {"m_FileID": 0, "m_PathID": 6034696777502009410}}
    ]
  }
}
```

### Material Example
```json
{
  "data": {
    "m_Name": "New Material",
    "m_Shader": {"m_PathID": -4850512016903265157},
    "m_SavedProperties": {
      "m_TexEnvs": [["_MainTex", {...}]],
      "m_Floats": [["_Metallic", 0.5]],
      "m_Colors": [["_Color", [1.0, 1.0, 1.0, 1.0]]]
    }
  }
}
```

### Texture Example  
```json
{
  "data": {
    "m_Name": "samus_hair",
    "m_Width": 1024,
    "m_Height": 1024,
    "m_TextureFormat": 12,
    "m_StreamData": {
      "offset": 1276448,
      "size": 1398128,
      "path": "archive:/CAB-xxx/CAB-xxx.resS"
    }
  }
}
```

## ⚠️ Important Notes

1. **Mesh data:** Some meshes show as empty arrays (may be runtime optimized)
2. **Texture images:** Stored in `.resS` files, referenced via `m_StreamData`
3. **Binary data:** Base64 encoded in JSON for compatibility
4. **Floating-point:** Tolerance ±0.0001 for positions, ±0.01 for colors
5. **PathIDs:** Can be negative (valid in Unity)

## 🎓 Learning Path

1. **Understand the format** (5 min)
   - Read: `SNAPSHOT_TESTING_README.md`
   
2. **Explore sample data** (10 min)
   - Browse: `snapshots/BambooCopter_head/`
   - Look at: `objects/*.json` files
   
3. **Implement parser** (varies)
   - Reference: Sample JSON files
   - Follow: Object type examples
   
4. **Generate .NET output** (depends on impl)
   - Match: JSON structure exactly
   - Validate: Using comparison tools

5. **Validate results** (5 min)
   - Run: comparison script
   - Review: diff report

## ✨ Success Indicators

Your .NET implementation is working correctly when:

```
✅ All objects parsed successfully
✅ Same number of objects as baseline
✅ All object types present
✅ All properties match (within tolerance)
✅ No parsing errors
✅ Can render 3D output
```

---

**Total Setup Time: ~30 minutes**  
**For full details, see:** `SNAPSHOT_TESTING_PLAN.md`
