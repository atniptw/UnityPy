#!/usr/bin/env python3
"""
Generate JSON snapshots from .hhh files for cross-platform testing.

These snapshots contain complete object data (geometry, materials, textures)
optimized for three.js rendering and comparison testing.

Usage:
    python generate_snapshots.py <input_dir> <output_dir>
    python generate_snapshots.py SampleMods/ snapshots/
    python generate_snapshots.py SampleMods/BambooCopter_head.hhh snapshots/BambooCopter/
"""

import json
import os
import sys
import hashlib
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import traceback

import UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler
from UnityPy.export.Texture2DConverter import parse_image_data


def convert_pathids_to_strings(obj: Any) -> Any:
    """Recursively convert all m_PathID/path_id values to strings to preserve JS precision."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Convert PathID-like keys to strings
            if key in {"path_id", "m_PathID", "m_PathId", "pathID", "PathID"} and isinstance(value, int):
                result[key] = str(value)
            else:
                result[key] = convert_pathids_to_strings(value)
        return result
    elif isinstance(obj, list):
        return [convert_pathids_to_strings(item) for item in obj]
    else:
        return obj


@dataclass
class SnapshotMetadata:
    """Metadata about a snapshot file."""
    file_name: str
    file_path: str
    file_size: int
    unity_version: str
    platform: str
    header_version: int
    endianness: str
    object_count: int
    timestamp: str
    

def serialize_value(value: Any, key: Optional[str] = None) -> Any:
    """Convert values to JSON-serializable format."""
    import numpy as np
    
    if isinstance(value, bytes):
        return {
            "_binary": True,
            "_format": "base64",
            "size": len(value),
            "data": base64.b64encode(value).decode('ascii')
        }
    elif isinstance(value, (np.ndarray, np.generic)):
        # Handle numpy arrays - convert to list
        return serialize_value(value.tolist())
    elif isinstance(value, (float, np.floating)):
        # Ensure floats are valid JSON (not NaN, inf)
        f = float(value)
        if np.isnan(f) or np.isinf(f):
            return 0.0
        return f
    elif isinstance(value, (int, np.integer)):
        if key in {"path_id", "m_PathID", "m_PathId", "pathID", "PathID"}:
            return str(int(value))
        return int(value)
    elif isinstance(value, (list, tuple)):
        # Handle both lists and tuples - convert tuples to lists for JSON
        return [serialize_value(v, key) for v in value]
    elif isinstance(value, dict):
        return {k: serialize_value(v, k) for k, v in value.items()}
    elif hasattr(value, '__dict__'):
        # Handle custom objects
        return serialize_value(value.__dict__)
    else:
        return value


def extract_mesh_geometry(mesh_obj, version: tuple) -> Dict[str, Any]:
    """Extract decompressed mesh geometry using MeshHandler."""
    try:
        handler = MeshHandler(mesh_obj, version=version)
        handler.process()
        
        # Extract UV coordinates if available
        uv0 = []
        uv1 = []
        if hasattr(handler, 'm_UV0') and handler.m_UV0:
            uv0 = list(handler.m_UV0)
        if hasattr(handler, 'm_UV1') and handler.m_UV1:
            uv1 = list(handler.m_UV1)
        
        # Extract vertex colors if available
        colors = []
        if hasattr(handler, 'm_Colors') and handler.m_Colors:
            # Don't include vertex colors in snapshot - they create massive JSON
            # and we're not using them effectively anyway
            pass  # colors = list(handler.m_Colors)
        
        return {
            "vertices": handler.m_Vertices if handler.m_Vertices else [],  # Include ALL vertices
            "vertex_count": len(handler.m_Vertices) if handler.m_Vertices else 0,
            "indices": handler.m_IndexBuffer if handler.m_IndexBuffer else [],  # Include ALL indices
            "index_count": len(handler.m_IndexBuffer) if handler.m_IndexBuffer else 0,
            "uv0": uv0,  # Primary UV coordinates for texturing
            "uv1": uv1,  # Secondary UV coordinates (lightmap UVs)
            "colors": colors,  # Vertex colors
            "has_normals": bool(handler.m_Normals),
            "has_tangents": bool(handler.m_Tangents),
        }
    except Exception as e:
        return {
            "error": f"Failed to extract geometry: {str(e)}",
            "vertex_count": 0,
            "index_count": 0,
            "uv0": [],
            "uv1": [],
            "colors": [],
        }


def extract_texture_to_png(texture_obj, output_dir: str, name: str, version: tuple) -> Optional[str]:
    """Extract texture to PNG file and return relative path."""
    try:
        # Get texture data object  
        if not hasattr(texture_obj, 'read'):
            return None
            
        texture_data = texture_obj.read()
        if not texture_data:
            return None
        
        width = getattr(texture_data, 'm_Width', 0)
        height = getattr(texture_data, 'm_Height', 0)
        
        # Skip if no dimensions
        if not width or not height:
            return None
        
        # Use the built-in image property which handles .resS files automatically
        try:
            pil_image = texture_data.image
            
            if pil_image and pil_image.size != (0, 0):
                # Save as PNG
                filename = f"{name}.png"
                filepath = os.path.join(output_dir, "textures", filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                pil_image.save(filepath, "PNG")
                print(f"      ✓ {filename} ({width}x{height})")
                return f"textures/{filename}"
        except Exception as e:
            # Silent fail for unsupported formats
            pass
            
    except Exception as e:
        pass  # Silent fail
    
    return None


def collect_textures_from_bundle(asset_bundle, output_dir: str, version: tuple) -> Dict[int, str]:
    """Collect all textures from bundle and return pathId -> filename mapping."""
    textures = {}
    try:
        for obj in asset_bundle.objects:
            if obj.type.name == "Texture2D":
                try:
                    tex_path = extract_texture_to_png(obj, output_dir, f"tex_{obj.path_id}", version)
                    if tex_path:
                        textures[str(obj.path_id)] = tex_path
                except Exception as e:
                    pass  # Skip textures that fail
    except Exception as e:
        pass  # Skip if no object iteration
    return textures


def create_object_snapshot(obj_reader, path_id: int, version: tuple) -> Dict[str, Any]:
    """Create a snapshot of a single object."""
    try:
        obj_type = obj_reader.type.name
        
        # Parse as dict to get all data
        try:
            data = obj_reader.parse_as_dict()
        except Exception as e:
            data = {
                "_error": f"Failed to parse: {str(e)}",
                "_type": obj_type
            }
        
        # Add extra geometry info and decompressed mesh for Mesh objects
        extra_info = {}
        if obj_type == "Mesh" and isinstance(data, dict):
            # Read the actual mesh object to extract geometry
            mesh_obj = obj_reader.read()
            
            # Capture mesh topology for validation
            sub_meshes = data.get('m_SubMeshes', [])
            if sub_meshes:
                sm = sub_meshes[0]
                extra_info["_geometry_info"] = {
                    "vertex_count": sm.get('vertexCount', 0),
                    "index_count": sm.get('indexCount', 0),
                    "topology": sm.get('topology', 0),  # 0=triangles, 1=triangle_strip
                    "has_index_buffer": len(data.get('m_IndexBuffer', [])) > 0,
                    "has_compressed_mesh": bool(data.get('m_CompressedMesh', {})),
                    "has_stream_data": bool(data.get('m_StreamData', {})),
                    "stream_size": data.get('m_StreamData', {}).get('size', 0),
                }
            
            # Extract decompressed geometry
            extra_info["_mesh_data"] = extract_mesh_geometry(mesh_obj, version)
        
        # Extract material properties and textures for Material objects
        if obj_type == "Material" and isinstance(data, dict):
            saved_props = data.get('m_SavedProperties', {})
            
            # Extract all colors
            colors = saved_props.get('m_Colors', [])
            material_colors = {}
            for color_name, color_data in colors:
                if isinstance(color_data, dict):
                    material_colors[color_name] = {
                        "r": color_data.get('r', 1.0),
                        "g": color_data.get('g', 1.0),
                        "b": color_data.get('b', 1.0),
                        "a": color_data.get('a', 1.0),
                    }
            if material_colors:
                extra_info["_colors"] = material_colors
                if "_Color" in material_colors:
                    extra_info["_color"] = material_colors["_Color"]

            # Extract all floats
            floats = saved_props.get('m_Floats', [])
            material_floats = {}
            for float_name, float_value in floats:
                if isinstance(float_value, (int, float)):
                    material_floats[float_name] = float(float_value)
            if material_floats:
                extra_info["_floats"] = material_floats
            
            # Extract texture references and transforms
            tex_envs = saved_props.get('m_TexEnvs', [])
            textures = {}
            for tex_name, tex_data in tex_envs:
                if tex_data and isinstance(tex_data, dict):
                    tex_ref = tex_data.get('m_Texture', {})
                    tex_path_id = tex_ref.get('m_PathID') if isinstance(tex_ref, dict) else None
                    if tex_path_id:
                        scale = tex_data.get('m_Scale', {}) if isinstance(tex_data, dict) else {}
                        offset = tex_data.get('m_Offset', {}) if isinstance(tex_data, dict) else {}
                        textures[tex_name] = {
                            "path_id": str(tex_path_id),
                            "scale": {
                                "x": scale.get('x', 1.0),
                                "y": scale.get('y', 1.0)
                            },
                            "offset": {
                                "x": offset.get('x', 0.0),
                                "y": offset.get('y', 0.0)
                            }
                        }
            if textures:
                extra_info["_textures"] = textures  # {_MainTex: path_id, ...}
        
        snapshot = {
            "metadata": {
                "path_id": str(path_id),  # Store as string to preserve precision (JS int limit: 2^53)
                "class_id": obj_reader.class_id,
                "type": obj_type,
                "byte_start": obj_reader.byte_start,
                "byte_size": obj_reader.byte_size,
            },
            "data": serialize_value(data),
        }
        
        if extra_info:
            snapshot.update(extra_info)
        
        return snapshot
    except Exception as e:
        return {
            "metadata": {
                "path_id": str(path_id),
                "error": str(e)
            },
            "data": None
        }


def generate_file_snapshots(file_path: str, output_dir: str) -> Optional[Dict[str, Any]]:
    """Generate snapshots for all objects in a single file."""
    
    try:
        # Load the file
        env = UnityPy.load(file_path)
        
        if not env.files:
            print(f"  ⚠️  No files loaded from {file_path}")
            return None
        
        # Get the first file (could be BundleFile or SerializedFile)
        first_file = list(env.files.values())[0]
        
        # If it's a BundleFile, get the actual assets
        if hasattr(first_file, 'get_assets'):
            assets_files = list(first_file.get_assets())
            if not assets_files:
                print(f"  ⚠️  No asset files found in bundle")
                return None
            assets_file = assets_files[0]
        else:
            assets_file = first_file
        
        # Get Unity version as a proper tuple
        unity_version = assets_file.version if hasattr(assets_file, 'version') else 2022
        if isinstance(unity_version, int):
            version_tuple = (unity_version, 0, 0, 0)
        elif isinstance(unity_version, tuple):
            version_tuple = unity_version + (0,) * (4 - len(unity_version))
        else:
            version_tuple = (int(str(unity_version).split('.')[0]), 0, 0, 0)
        
        # Collect metadata
        objects = list(env.objects)
        
        # Get endianness from reader if available
        endian_str = "little"
        if hasattr(assets_file, 'reader') and hasattr(assets_file.reader, 'endian'):
            endian_str = "big" if assets_file.reader.endian else "little"
        
        # Build file metadata
        bundle_name = Path(file_path).stem
        metadata = {
            "bundle_name": bundle_name,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "unity_version": str(assets_file.version) if hasattr(assets_file, 'version') else "Unknown",
            "platform": str(assets_file.target_platform.name) if hasattr(assets_file, 'target_platform') else "Unknown",
            "header_version": assets_file.header.version if hasattr(assets_file, 'header') else 0,
            "endianness": endian_str,
            "object_count": len(objects),
        }
        
        # Build summary
        type_counts = {}
        object_list = []
        
        for obj in objects:
            type_name = obj.type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            object_list.append({
                "path_id": str(obj.path_id),
                "class_id": obj.class_id,
                "type": type_name,
                "byte_start": obj.byte_start,
                "byte_size": obj.byte_size,
            })
        
        summary = {
            "total_objects": len(objects),
            "objects_by_type": type_counts,
            "object_list": object_list,
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Collect textures from bundle first
        print(f"  📷 Extracting textures...")
        texture_map = {}
        try:
            # Get the asset bundle or file
            if hasattr(first_file, 'objects'):
                texture_map = collect_textures_from_bundle(first_file, output_dir, version_tuple)
            else:
                texture_map = collect_textures_from_bundle(env, output_dir, version_tuple)
            if texture_map:
                print(f"  ✓ Extracted {len(texture_map)} textures")
                # Write texture index
                with open(os.path.join(output_dir, "textures_index.json"), "w") as f:
                    json.dump(convert_pathids_to_strings(texture_map), f, indent=2)
        except Exception as e:
            print(f"  ⚠️  Could not extract textures: {e}")
        
        # Write manifest
        with open(os.path.join(output_dir, "manifest.json"), "w") as f:
            json.dump(convert_pathids_to_strings(metadata), f, indent=2)
        print(f"  ✓ manifest.json")
        
        # Write summary
        with open(os.path.join(output_dir, "summary.json"), "w") as f:
            json.dump(convert_pathids_to_strings(summary), f, indent=2)
        print(f"  ✓ summary.json")
        
        # Write individual objects
        objects_dir = os.path.join(output_dir, "objects")
        os.makedirs(objects_dir, exist_ok=True)
        
        for i, obj in enumerate(objects):
            try:
                snapshot = create_object_snapshot(obj, obj.path_id, version_tuple)
                
                # Use type name and path_id for filename
                type_name = obj.type.name
                filename = f"{i:03d}_{type_name}_{obj.path_id}.json"
                filepath = os.path.join(objects_dir, filename)
                
                # Convert pathids to strings before JSON serialization
                snapshot_converted = convert_pathids_to_strings(snapshot)
                
                with open(filepath, "w") as f:
                    json.dump(snapshot_converted, f, indent=2)
                
            except Exception as e:
                print(f"  ⚠️  Error processing object {obj.path_id}: {e}")
                traceback.print_exc()
        
        print(f"  ✓ {len(objects)} object snapshots")
        
        return metadata
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        traceback.print_exc()
        return None


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_base = sys.argv[2]
    
    if not os.path.exists(input_path):
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)
    
    # Handle single file or directory
    if os.path.isfile(input_path):
        files = [input_path]
    else:
        # Find all .hhh files
        files = [str(p) for p in Path(input_path).rglob("*.hhh")]
        if not files:
            print(f"No .hhh files found in {input_path}")
            sys.exit(1)
    
    print(f"\n🎬 Generating snapshots for {len(files)} file(s)...\n")
    
    results = []
    for file_path in sorted(files):
        file_name = os.path.basename(file_path)
        
        # Create output directory for this file
        file_output = os.path.join(output_base, Path(file_path).stem)
        
        print(f"📦 {file_name}")
        result = generate_file_snapshots(file_path, file_output)
        if result:
            results.append(result)
    
    print(f"\n✅ Generated {len(results)}/{len(files)} successful snapshots")
    print(f"📁 Output: {os.path.abspath(output_base)}")
    
    # Generate snapshots index for the viewer
    print("\n🔄 Generating snapshots index...")
    index = {}
    for result in results:
        bundle_name = result.get('bundle_name')
        if bundle_name:
            # List all object files in this bundle's objects directory
            objects_dir = os.path.join(output_base, bundle_name, 'objects')
            if os.path.isdir(objects_dir):
                object_files = sorted([f for f in os.listdir(objects_dir) if f.endswith('.json')])
                index[bundle_name] = {'objects': object_files}
    
    # Write index file
    index_path = os.path.join(output_base, '..', 'snapshots_index.json')
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    print(f"📋 Index written: {os.path.abspath(index_path)}")


if __name__ == "__main__":
    main()
