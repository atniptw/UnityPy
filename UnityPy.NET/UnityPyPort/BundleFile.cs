using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using K4os.Compression.LZ4;

namespace UnityPyPort
{
    /// <summary>
    /// Represents a Unity bundle file
    /// </summary>
    public class BundleFile
    {
        public string Signature { get; set; } = string.Empty;
        public uint Version { get; set; }
        public string VersionPlayer { get; set; } = string.Empty;
        public string VersionEngine { get; set; } = string.Empty;
        public List<SerializedFile> Files { get; set; } = new();

        public static BundleFile Load(string filePath)
        {
            using var fileStream = File.OpenRead(filePath);
            using var reader = new EndianBinaryReader(fileStream);
            
            var bundle = new BundleFile();
            bundle.Signature = reader.ReadStringToNull();
            bundle.Version = reader.ReadUInt32();
            bundle.VersionPlayer = reader.ReadStringToNull();
            bundle.VersionEngine = reader.ReadStringToNull();

            if (bundle.Signature == "UnityFS")
            {
                bundle.ReadFS(reader);
            }
            else
            {
                throw new NotSupportedException($"Bundle signature '{bundle.Signature}' is not supported");
            }

            return bundle;
        }

        private void ReadFS(EndianBinaryReader reader)
        {
            var size = reader.ReadInt64();
            var compressedSize = reader.ReadUInt32();
            var uncompressedSize = reader.ReadUInt32();
            var flags = reader.ReadUInt32();

            // Check if header is at the end
            bool headerAtEnd = (flags & 0x80) != 0;
            
            if (headerAtEnd)
            {
                reader.Position = reader.Length - compressedSize;
            }

            // Read and decompress block info
            var blocksInfoBytes = reader.ReadBytes((int)compressedSize);
            byte[] uncompressedBlocksInfo;

            var compressionType = flags & 0x3F;
            if (compressionType == 0) // None
            {
                uncompressedBlocksInfo = blocksInfoBytes;
            }
            else if (compressionType == 1) // LZMA
            {
                // For now, we'll skip LZMA decompression
                throw new NotSupportedException("LZMA compression not yet implemented");
            }
            else if (compressionType == 2 || compressionType == 3) // LZ4
            {
                uncompressedBlocksInfo = DecompressLZ4(blocksInfoBytes, (int)uncompressedSize);
            }
            else
            {
                throw new NotSupportedException($"Compression type {compressionType} not supported");
            }

            // Parse blocks info
            using var blocksReader = new EndianBinaryReader(new MemoryStream(uncompressedBlocksInfo), true);
            
            // Skip GUID
            blocksReader.ReadBytes(16);
            
            var blockCount = blocksReader.ReadInt32();
            var blocks = new List<(uint uncompressedSize, uint compressedSize, ushort flags)>();
            
            for (int i = 0; i < blockCount; i++)
            {
                var uncompSize = blocksReader.ReadUInt32();
                var compSize = blocksReader.ReadUInt32();
                var blockFlags = (ushort)blocksReader.ReadUInt16();
                blocks.Add((uncompSize, compSize, blockFlags));
            }

            var nodeCount = blocksReader.ReadInt32();
            var directoryInfo = new List<(string path, long offset, long size)>();
            
            for (int i = 0; i < nodeCount; i++)
            {
                var offset = blocksReader.ReadInt64();
                var nodeSize = blocksReader.ReadInt64();
                var status = blocksReader.ReadUInt32();
                var path = blocksReader.ReadStringToNull();
                directoryInfo.Add((path, offset, nodeSize));
            }

            // Read actual file data
            var dataStartPosition = headerAtEnd ? 
                reader.Position - compressedSize - blocks.Count * 16 : 
                reader.Position;

            foreach (var fileInfo in directoryInfo)
            {
                // For now, we'll just note the file exists
                // Full implementation would read and parse each serialized file
                Console.WriteLine($"Found file: {fileInfo.path} (offset: {fileInfo.offset}, size: {fileInfo.size})");
            }
        }

        private byte[] DecompressLZ4(byte[] compressedData, int uncompressedSize)
        {
            // Use K4os.Compression.LZ4 library for decompression
            if (compressedData.Length == uncompressedSize)
                return compressedData;
            
            var uncompressed = new byte[uncompressedSize];
            var decoded = LZ4Codec.Decode(compressedData, 0, compressedData.Length, uncompressed, 0, uncompressedSize);
            
            if (decoded != uncompressedSize)
            {
                throw new InvalidDataException($"LZ4 decompression failed: expected {uncompressedSize} bytes, got {decoded}");
            }
            
            return uncompressed;
        }
    }
}
