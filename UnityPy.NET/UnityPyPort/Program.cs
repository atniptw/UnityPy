using UnityPyPort;
using System.Diagnostics;

if (args.Length < 2)
{
    Console.WriteLine("Usage: UnityPyPort <input_path> <output_path>");
    Console.WriteLine("  <input_path>  - Path to .hhh file or directory containing .hhh files");
    Console.WriteLine("  <output_path> - Directory where snapshots will be generated");
    return 1;
}

var inputPath = args[0];
var outputPath = args[1];

Console.WriteLine("UnityPy .NET Port - Snapshot Generator");
Console.WriteLine("======================================\n");

try
{
    SnapshotGenerator.GenerateSnapshots(inputPath, outputPath);
    Console.WriteLine("\n✅ Snapshot generation complete");
    return 0;
}
catch (Exception ex)
{
    Console.WriteLine($"\n❌ Error: {ex.Message}");
    if (ex.InnerException != null)
    {
        Console.WriteLine($"   Inner: {ex.InnerException.Message}");
    }
    Console.WriteLine($"\n{ex.StackTrace}");
    return 1;
}
