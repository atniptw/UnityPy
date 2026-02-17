using System;
using System.Diagnostics;
using System.IO;
using System.Text;

namespace UnityPyPort
{
    /// <summary>
    /// Helper class to invoke Python UnityPy for snapshot generation
    /// This provides a working implementation while the native C# port is being completed
    /// </summary>
    public class PythonUnityPyBridge
    {
        private readonly string _pythonPath;
        private readonly string _scriptPath;

        public PythonUnityPyBridge()
        {
            // Try to find python3 or python
            _pythonPath = FindPython();
            
            // The generate_snapshots.py script should be in the repository root
            var currentDir = Directory.GetCurrentDirectory();
            // Navigate up to find the script
            _scriptPath = FindGenerateSnapshotsScript(currentDir);
        }

        private string FindPython()
        {
            var pythonCommands = new[] { "python3", "python" };
            
            foreach (var cmd in pythonCommands)
            {
                try
                {
                    var process = new Process
                    {
                        StartInfo = new ProcessStartInfo
                        {
                            FileName = cmd,
                            Arguments = "--version",
                            RedirectStandardOutput = true,
                            RedirectStandardError = true,
                            UseShellExecute = false,
                            CreateNoWindow = true
                        }
                    };
                    
                    process.Start();
                    process.WaitForExit();
                    
                    if (process.ExitCode == 0)
                    {
                        return cmd;
                    }
                }
                catch
                {
                    // Command not found, try next
                }
            }
            
            return "python3"; // Default fallback
        }

        private string FindGenerateSnapshotsScript(string startDir)
        {
            var current = new DirectoryInfo(startDir);
            
            while (current != null)
            {
                var scriptPath = Path.Combine(current.FullName, "generate_snapshots.py");
                if (File.Exists(scriptPath))
                {
                    return scriptPath;
                }
                
                current = current.Parent;
            }
            
            throw new FileNotFoundException("Could not find generate_snapshots.py script");
        }

        public void GenerateSnapshots(string inputPath, string outputPath)
        {
            if (string.IsNullOrEmpty(_scriptPath) || !File.Exists(_scriptPath))
            {
                throw new FileNotFoundException($"Python script not found: {_scriptPath}");
            }

            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = $"\"{_scriptPath}\" \"{inputPath}\" \"{outputPath}\"",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };

            var output = new StringBuilder();
            var error = new StringBuilder();

            process.OutputDataReceived += (sender, e) =>
            {
                if (e.Data != null)
                {
                    Console.WriteLine(e.Data);
                    output.AppendLine(e.Data);
                }
            };

            process.ErrorDataReceived += (sender, e) =>
            {
                if (e.Data != null)
                {
                    Console.Error.WriteLine(e.Data);
                    error.AppendLine(e.Data);
                }
            };

            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                throw new Exception($"Python script failed with exit code {process.ExitCode}: {error}");
            }
        }
    }
}
