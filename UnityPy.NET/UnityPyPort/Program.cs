using UnityPyPort;

if (args.Length < 2)
{
    Console.WriteLine("Usage: UnityPyPort <input_path> <output_path>");
    Console.WriteLine("  <input_path>  - Path to .hhh file or directory containing .hhh files");
    Console.WriteLine("  <output_path> - Directory where snapshots will be generated");
    return 1;
}

var inputPath = args[0];
var outputPath = args[1];

SnapshotGenerator.GenerateSnapshots(inputPath, outputPath);

Console.WriteLine("\n✅ Snapshot generation complete");
return 0;
