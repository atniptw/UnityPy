#!/usr/bin/env python3
"""
Snapshot validation tests for UnityPy asset extraction.

Validates that generated snapshots match reference snapshots for all 10 bundles.
Tests:
- Object counts per bundle
- Mesh vertex/index/UV counts
- Material property values
- Texture extraction results
- Path IDs serialized as strings
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pytest

# Get the repository root
REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "SampleMods"
REFERENCE_SNAPSHOTS_DIR = REPO_ROOT / "snapshots"

# All 10 bundles to validate
BUNDLES = [
    ("SamusPlushie_body", 25, 2),      # (name, objects, textures)
    ("BambooCopter_head", 13, 0),
    ("ClownNose_head", 10, 0),
    ("FoxMask_head", 11, 1),
    ("FrogHatSmile_head", 11, 1),
    ("AmyBackpack_body", 13, 1),
    ("Aku Aku_world", 228, 1),
    ("Cigar_neck", 17, 0),
    ("Odradek_neck", 55, 0),
    ("Volleyball_world", 22, 0),
]


def generate_test_snapshot(bundle_name: str, temp_dir: str) -> Path:
    """Generate a snapshot for testing."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    from generate_snapshots import generate_file_snapshots
    
    bundle_path = SAMPLES_DIR / f"{bundle_name}.hhh"
    output_dir = Path(temp_dir) / bundle_name
    
    result = generate_file_snapshots(str(bundle_path), str(output_dir))
    assert result is not None, f"Failed to generate snapshot for {bundle_name}"
    
    return output_dir


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def compare_values(val1: Any, val2: Any, path: str = "") -> List[str]:
    """
    Recursively compare two values and return list of differences.
    
    Handles special cases:
    - Floats are compared with tolerance
    - Lists are compared element by element
    - Dicts are compared key by key
    - Ignores certain keys that may vary (timestamps, etc.)
    """
    differences = []
    
    # Skip certain keys that may legitimately differ
    skip_keys = {"timestamp", "file_path"}
    if any(key in path for key in skip_keys):
        return differences
    
    # Handle None
    if val1 is None and val2 is None:
        return differences
    if val1 is None or val2 is None:
        differences.append(f"{path}: {val1} != {val2}")
        return differences
    
    # Handle floats with tolerance
    if isinstance(val1, float) and isinstance(val2, float):
        if abs(val1 - val2) > 1e-6:
            differences.append(f"{path}: {val1} != {val2} (float diff > 1e-6)")
        return differences
    
    # Handle lists
    if isinstance(val1, list) and isinstance(val2, list):
        if len(val1) != len(val2):
            differences.append(f"{path}: list length {len(val1)} != {len(val2)}")
            return differences
        for i, (item1, item2) in enumerate(zip(val1, val2)):
            differences.extend(compare_values(item1, item2, f"{path}[{i}]"))
        return differences
    
    # Handle dicts
    if isinstance(val1, dict) and isinstance(val2, dict):
        all_keys = set(val1.keys()) | set(val2.keys())
        for key in all_keys:
            key_path = f"{path}.{key}" if path else key
            if key not in val1:
                differences.append(f"{key_path}: missing in first")
            elif key not in val2:
                differences.append(f"{key_path}: missing in second")
            else:
                differences.extend(compare_values(val1[key], val2[key], key_path))
        return differences
    
    # Handle basic types
    if val1 != val2:
        # Special case: numbers might be stored as int vs string
        if isinstance(val1, str) and isinstance(val2, int):
            if val1 == str(val2):
                return differences
        if isinstance(val2, str) and isinstance(val1, int):
            if val2 == str(val1):
                return differences
        differences.append(f"{path}: {val1} != {val2}")
    
    return differences


def validate_pathids_are_strings(data: Any, path: str = "") -> List[str]:
    """
    Validate that all PathID-like fields are strings.
    
    This is critical for JavaScript compatibility (preserves 64-bit precision).
    """
    issues = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Check if this is a PathID field
            if key in {"path_id", "m_PathID", "m_PathId", "pathID", "PathID"}:
                if not isinstance(value, str):
                    issues.append(f"{path}.{key}: PathID is {type(value).__name__}, should be str")
            else:
                # Recurse into nested structures
                key_path = f"{path}.{key}" if path else key
                issues.extend(validate_pathids_are_strings(value, key_path))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            issues.extend(validate_pathids_are_strings(item, f"{path}[{i}]"))
    
    return issues


@pytest.mark.parametrize("bundle_name,expected_objects,expected_textures", BUNDLES)
def test_bundle_snapshot_validation(bundle_name: str, expected_objects: int, expected_textures: int):
    """Test that generated snapshots match reference snapshots."""
    
    # Generate test snapshot in temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_snapshot_dir = generate_test_snapshot(bundle_name, temp_dir)
        reference_snapshot_dir = REFERENCE_SNAPSHOTS_DIR / bundle_name
        
        # Validate manifest
        test_manifest = load_json(test_snapshot_dir / "manifest.json")
        ref_manifest = load_json(reference_snapshot_dir / "manifest.json")
        
        # Check object count
        assert test_manifest["object_count"] == expected_objects, \
            f"Expected {expected_objects} objects, got {test_manifest['object_count']}"
        assert test_manifest["object_count"] == ref_manifest["object_count"], \
            "Object count differs from reference"
        
        # Validate summary
        test_summary = load_json(test_snapshot_dir / "summary.json")
        ref_summary = load_json(reference_snapshot_dir / "summary.json")
        
        # Check total objects match
        assert test_summary["total_objects"] == expected_objects
        assert test_summary["total_objects"] == ref_summary["total_objects"]
        
        # Check object type counts match
        assert test_summary["objects_by_type"] == ref_summary["objects_by_type"], \
            f"Object type counts differ:\nTest: {test_summary['objects_by_type']}\nRef: {ref_summary['objects_by_type']}"
        
        # Validate texture count
        test_textures_path = test_snapshot_dir / "textures_index.json"
        ref_textures_path = reference_snapshot_dir / "textures_index.json"
        
        if expected_textures > 0:
            assert test_textures_path.exists(), "Missing textures_index.json"
            assert ref_textures_path.exists(), "Reference missing textures_index.json"
            
            test_textures = load_json(test_textures_path)
            ref_textures = load_json(ref_textures_path)
            
            assert len(test_textures) == expected_textures, \
                f"Expected {expected_textures} textures, got {len(test_textures)}"
            assert len(test_textures) == len(ref_textures), \
                "Texture count differs from reference"
        
        # Validate PathIDs are strings in manifest and summary
        pathid_issues = []
        pathid_issues.extend(validate_pathids_are_strings(test_manifest, "manifest"))
        pathid_issues.extend(validate_pathids_are_strings(test_summary, "summary"))
        
        assert len(pathid_issues) == 0, \
            f"PathID validation failed:\n" + "\n".join(pathid_issues[:10])
        
        # Validate individual objects
        test_objects_dir = test_snapshot_dir / "objects"
        ref_objects_dir = reference_snapshot_dir / "objects"
        
        test_object_files = sorted([f for f in test_objects_dir.glob("*.json")])
        ref_object_files = sorted([f for f in ref_objects_dir.glob("*.json")])
        
        assert len(test_object_files) == expected_objects, \
            f"Expected {expected_objects} object files, got {len(test_object_files)}"
        assert len(test_object_files) == len(ref_object_files), \
            "Object file count differs from reference"
        
        # Sample validation: check first, middle, and last objects
        sample_indices = [0, len(test_object_files) // 2, -1]
        
        for idx in sample_indices:
            test_obj = load_json(test_object_files[idx])
            ref_obj = load_json(ref_object_files[idx])
            
            # Validate PathIDs in object
            pathid_issues = validate_pathids_are_strings(test_obj, f"object_{idx}")
            assert len(pathid_issues) == 0, \
                f"PathID validation failed in {test_object_files[idx].name}:\n" + \
                "\n".join(pathid_issues[:5])
            
            # Check metadata matches
            assert test_obj["metadata"]["type"] == ref_obj["metadata"]["type"]
            assert test_obj["metadata"]["path_id"] == ref_obj["metadata"]["path_id"]
            
            # For Mesh objects, validate geometry
            if test_obj["metadata"]["type"] == "Mesh":
                validate_mesh_geometry(test_obj, ref_obj, test_object_files[idx].name)
            
            # For Material objects, validate properties
            if test_obj["metadata"]["type"] == "Material":
                validate_material_properties(test_obj, ref_obj, test_object_files[idx].name)


def validate_mesh_geometry(test_obj: Dict, ref_obj: Dict, filename: str):
    """Validate mesh geometry data."""
    
    # Check if _mesh_data exists
    if "_mesh_data" in test_obj and "_mesh_data" in ref_obj:
        test_mesh = test_obj["_mesh_data"]
        ref_mesh = ref_obj["_mesh_data"]
        
        # Validate vertex count
        assert test_mesh.get("vertex_count") == ref_mesh.get("vertex_count"), \
            f"{filename}: Vertex count mismatch"
        
        # Validate index count
        assert test_mesh.get("index_count") == ref_mesh.get("index_count"), \
            f"{filename}: Index count mismatch"
        
        # Validate UV data
        if "uv0" in test_mesh and "uv0" in ref_mesh:
            assert len(test_mesh["uv0"]) == len(ref_mesh["uv0"]), \
                f"{filename}: UV0 length mismatch"
        
        if "uv1" in test_mesh and "uv1" in ref_mesh:
            assert len(test_mesh["uv1"]) == len(ref_mesh["uv1"]), \
                f"{filename}: UV1 length mismatch"
    
    # Check _geometry_info if present
    if "_geometry_info" in test_obj and "_geometry_info" in ref_obj:
        test_info = test_obj["_geometry_info"]
        ref_info = ref_obj["_geometry_info"]
        
        assert test_info.get("vertex_count") == ref_info.get("vertex_count"), \
            f"{filename}: Geometry vertex count mismatch"
        assert test_info.get("index_count") == ref_info.get("index_count"), \
            f"{filename}: Geometry index count mismatch"


def validate_material_properties(test_obj: Dict, ref_obj: Dict, filename: str):
    """Validate material properties."""
    
    # Check colors
    if "_colors" in test_obj and "_colors" in ref_obj:
        test_colors = test_obj["_colors"]
        ref_colors = ref_obj["_colors"]
        
        assert set(test_colors.keys()) == set(ref_colors.keys()), \
            f"{filename}: Color keys mismatch"
        
        for color_name in test_colors.keys():
            test_color = test_colors[color_name]
            ref_color = ref_colors[color_name]
            
            # Compare with float tolerance
            for component in ["r", "g", "b", "a"]:
                test_val = test_color.get(component, 1.0)
                ref_val = ref_color.get(component, 1.0)
                assert abs(test_val - ref_val) < 1e-6, \
                    f"{filename}: Color {color_name}.{component} mismatch: {test_val} != {ref_val}"
    
    # Check floats
    if "_floats" in test_obj and "_floats" in ref_obj:
        test_floats = test_obj["_floats"]
        ref_floats = ref_obj["_floats"]
        
        assert set(test_floats.keys()) == set(ref_floats.keys()), \
            f"{filename}: Float keys mismatch"
        
        for float_name in test_floats.keys():
            test_val = test_floats[float_name]
            ref_val = ref_floats[float_name]
            assert abs(test_val - ref_val) < 1e-6, \
                f"{filename}: Float {float_name} mismatch: {test_val} != {ref_val}"
    
    # Check textures
    if "_textures" in test_obj and "_textures" in ref_obj:
        test_textures = test_obj["_textures"]
        ref_textures = ref_obj["_textures"]
        
        assert set(test_textures.keys()) == set(ref_textures.keys()), \
            f"{filename}: Texture keys mismatch"
        
        for tex_name in test_textures.keys():
            test_tex = test_textures[tex_name]
            ref_tex = ref_textures[tex_name]
            
            # Validate path_id is string
            assert isinstance(test_tex["path_id"], str), \
                f"{filename}: Texture {tex_name} path_id should be string"
            
            # Compare path_id
            assert test_tex["path_id"] == ref_tex["path_id"], \
                f"{filename}: Texture {tex_name} path_id mismatch"


def test_pathid_string_serialization():
    """Test that PathIDs are always serialized as strings."""
    
    # Test a few bundles that have large PathIDs (negative 64-bit integers)
    test_bundles = [
        "SamusPlushie_body",  # Has PathIDs like -8911878726397676121
        "Aku Aku_world",       # Large bundle with many objects
    ]
    
    for bundle_name in test_bundles:
        ref_snapshot_dir = REFERENCE_SNAPSHOTS_DIR / bundle_name
        
        # Check manifest
        manifest = load_json(ref_snapshot_dir / "manifest.json")
        issues = validate_pathids_are_strings(manifest, f"{bundle_name}/manifest")
        assert len(issues) == 0, f"PathID validation failed:\n" + "\n".join(issues)
        
        # Check summary
        summary = load_json(ref_snapshot_dir / "summary.json")
        issues = validate_pathids_are_strings(summary, f"{bundle_name}/summary")
        assert len(issues) == 0, f"PathID validation failed:\n" + "\n".join(issues)
        
        # Check a few object files
        objects_dir = ref_snapshot_dir / "objects"
        object_files = sorted(list(objects_dir.glob("*.json")))[:5]
        
        for obj_file in object_files:
            obj_data = load_json(obj_file)
            issues = validate_pathids_are_strings(obj_data, f"{bundle_name}/{obj_file.name}")
            assert len(issues) == 0, f"PathID validation failed:\n" + "\n".join(issues[:5])


def test_material_texenv_format():
    """Test that Material TexEnvs are properly formatted as tuples."""
    
    # Find materials in reference snapshots
    materials_found = 0
    
    for bundle_name, _, _ in BUNDLES:
        objects_dir = REFERENCE_SNAPSHOTS_DIR / bundle_name / "objects"
        
        for obj_file in objects_dir.glob("*Material*.json"):
            obj_data = load_json(obj_file)
            
            if obj_data["metadata"]["type"] == "Material":
                materials_found += 1
                
                # Check if m_SavedProperties exists
                if "m_SavedProperties" in obj_data.get("data", {}):
                    saved_props = obj_data["data"]["m_SavedProperties"]
                    
                    # TexEnvs should be a list of tuples (converted to lists in JSON)
                    if "m_TexEnvs" in saved_props:
                        tex_envs = saved_props["m_TexEnvs"]
                        assert isinstance(tex_envs, list), \
                            f"{obj_file.name}: m_TexEnvs should be list"
                        
                        for tex_env in tex_envs:
                            # Each entry should be a 2-element list [name, data]
                            assert isinstance(tex_env, list), \
                                f"{obj_file.name}: TexEnv entry should be list"
                            assert len(tex_env) == 2, \
                                f"{obj_file.name}: TexEnv entry should have 2 elements"
                            
                            tex_name, tex_data = tex_env
                            assert isinstance(tex_name, str), \
                                f"{obj_file.name}: TexEnv name should be string"
    
    # Ensure we actually found and tested materials
    assert materials_found > 0, "No materials found to test"


def test_all_bundles_present():
    """Test that all 10 reference bundles are present."""
    
    for bundle_name, _, _ in BUNDLES:
        bundle_path = SAMPLES_DIR / f"{bundle_name}.hhh"
        assert bundle_path.exists(), f"Bundle file missing: {bundle_name}.hhh"
        
        snapshot_dir = REFERENCE_SNAPSHOTS_DIR / bundle_name
        assert snapshot_dir.exists(), f"Snapshot directory missing: {bundle_name}"
        
        assert (snapshot_dir / "manifest.json").exists(), \
            f"Missing manifest.json for {bundle_name}"
        assert (snapshot_dir / "summary.json").exists(), \
            f"Missing summary.json for {bundle_name}"
        assert (snapshot_dir / "objects").exists(), \
            f"Missing objects directory for {bundle_name}"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
