using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace UnityPyPort
{
    /// <summary>
    /// Generates JSON snapshots from Unity bundle files
    /// Pure .NET implementation based on AssetStudio architecture
    /// </summary>
    public class SnapshotGenerator
    {
        public static void GenerateSnapshots(string inputPath, string outputPath)
        {
            Console.WriteLine($"📂 Input: {inputPath}");
            Console.WriteLine($"📁 Output: {outputPath}\n");

            if (!Directory.Exists(outputPath))
            {
                Directory.CreateDirectory(outputPath);
            }

            if (File.Exists(inputPath) && inputPath.EndsWith(".hhh"))
            {
                ProcessBundleNative(inputPath, outputPath);
            }
            else if (Directory.Exists(inputPath))
            {
                foreach (var file in Directory.GetFiles(inputPath, "*.hhh", SearchOption.AllDirectories))
                {
                    ProcessBundleNative(file, outputPath);
                }
            }
            else
            {
                throw new ArgumentException($"Invalid input path: {inputPath}");
            }
        }

        private static void ProcessBundleNative(string bundlePath, string baseOutputPath)
        {
            try
            {
                var bundleName = Path.GetFileNameWithoutExtension(bundlePath);
                var outputDir = Path.Combine(baseOutputPath, bundleName);
                
                Console.WriteLine($"📦 Processing: {bundleName}");

                Directory.CreateDirectory(outputDir);
                Directory.CreateDirectory(Path.Combine(outputDir, "objects"));

                // Load the bundle using native C#
                var bundle = BundleFile.Load(bundlePath);

                // Create manifest
                var manifest = new Dictionary<string, object>
                {
                    ["bundle_name"] = bundleName,
                    ["file_name"] = Path.GetFileName(bundlePath),
                    ["file_size"] = new FileInfo(bundlePath).Length,
                    ["unity_version"] = bundle.VersionEngine,
                    ["platform"] = "StandaloneWindows64",
                    ["header_version"] = bundle.Version,
                    ["endianness"] = "big",
                    ["object_count"] = bundle.Objects.Count
                };

                var manifestPath = Path.Combine(outputDir, "manifest.json");
                File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions 
                { 
                    WriteIndented = true,
                    DefaultIgnoreCondition = JsonIgnoreCondition.Never
                }));

                Console.WriteLine($"  ✓ manifest.json");

                // Create summary
                var objectsByType = new Dictionary<string, int>();
                var objectList = new List<object>();

                foreach (var obj in bundle.Objects)
                {
                    var typeName = obj.TypeName;
                    objectsByType[typeName] = objectsByType.GetValueOrDefault(typeName) + 1;
                    
                    objectList.Add(new Dictionary<string, object>
                    {
                        ["path_id"] = obj.PathId.ToString(),
                        ["class_id"] = obj.ClassId,
                        ["type"] = typeName,
                        ["byte_start"] = obj.ByteStart,
                        ["byte_size"] = obj.ByteSize
                    });
                }

                var summary = new Dictionary<string, object>
                {
                    ["total_objects"] = bundle.Objects.Count,
                    ["objects_by_type"] = objectsByType,
                    ["object_list"] = objectList
                };

                var summaryPath = Path.Combine(outputDir, "summary.json");
                File.WriteAllText(summaryPath, JsonSerializer.Serialize(summary, new JsonSerializerOptions 
                { 
                    WriteIndented = true 
                }));

                Console.WriteLine($"  ✓ summary.json");

                // Generate individual object files
                for (int i = 0; i < bundle.Objects.Count; i++)
                {
                    var obj = bundle.Objects[i];
                    var filename = $"{i:D3}_{obj.TypeName}_{obj.PathId}.json";
                    var filepath = Path.Combine(outputDir, "objects", filename);

                    var objectData = new Dictionary<string, object>
                    {
                        ["metadata"] = new Dictionary<string, object>
                        {
                            ["path_id"] = obj.PathId.ToString(),
                            ["class_id"] = obj.ClassId,
                            ["type"] = obj.TypeName,
                            ["byte_start"] = obj.ByteStart,
                            ["byte_size"] = obj.ByteSize
                        },
                        ["data"] = obj.ParsedData ?? new Dictionary<string, object>()
                    };

                    File.WriteAllText(filepath, JsonSerializer.Serialize(objectData, new JsonSerializerOptions 
                    { 
                        WriteIndented = true 
                    }));
                }

                Console.WriteLine($"  ✓ {bundle.Objects.Count} object snapshots");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  ✗ Error: {ex.Message}");
                Console.WriteLine($"     {ex.StackTrace}");
                throw;
            }
        }
    }
}
