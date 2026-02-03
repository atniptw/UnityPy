using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace UnityPyPort
{
    /// <summary>
    /// Generates JSON snapshots from Unity bundle files
    /// Currently uses Python UnityPy as backend while native C# implementation is completed
    /// </summary>
    public class SnapshotGenerator
    {
        private static bool _usePythonBridge = true; // Toggle to use Python or native C# (when ready)

        public static void GenerateSnapshots(string inputPath, string outputPath)
        {
            Console.WriteLine($"📂 Input: {inputPath}");
            Console.WriteLine($"📁 Output: {outputPath}\n");

            if (!Directory.Exists(outputPath))
            {
                Directory.CreateDirectory(outputPath);
            }

            if (_usePythonBridge)
            {
                // Use Python UnityPy bridge for now
                Console.WriteLine("Using Python UnityPy backend...\n");
                var bridge = new PythonUnityPyBridge();
                bridge.GenerateSnapshots(inputPath, outputPath);
            }
            else
            {
                // Use native C# implementation (work in progress)
                Console.WriteLine("Using native C# implementation...\n");
                
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

                // Load the bundle (native C# - work in progress)
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
                    ["object_count"] = 0
                };

                var manifestPath = Path.Combine(outputDir, "manifest.json");
                File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions 
                { 
                    WriteIndented = true,
                    DefaultIgnoreCondition = JsonIgnoreCondition.Never
                }));

                Console.WriteLine($"  ✓ manifest.json");

                // Create summary
                var summary = new Dictionary<string, object>
                {
                    ["total_objects"] = 0,
                    ["objects_by_type"] = new Dictionary<string, int>(),
                    ["object_list"] = new List<object>()
                };

                var summaryPath = Path.Combine(outputDir, "summary.json");
                File.WriteAllText(summaryPath, JsonSerializer.Serialize(summary, new JsonSerializerOptions 
                { 
                    WriteIndented = true 
                }));

                Console.WriteLine($"  ✓ summary.json");
                Console.WriteLine($"  ⚠️  Native implementation incomplete - no objects extracted");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  ✗ Error: {ex.Message}");
                throw;
            }
        }
    }
}
