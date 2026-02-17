using System;
using System.Collections.Generic;

namespace UnityPyPort
{
    /// <summary>
    /// Represents a serialized Unity asset file
    /// </summary>
    public class SerializedFile
    {
        public string Name { get; set; } = string.Empty;
        public int Version { get; set; }
        public string UnityVersion { get; set; } = string.Empty;
        public int TargetPlatform { get; set; }
        public bool IsBigEndian { get; set; }
        public List<ObjectInfo> Objects { get; set; } = new();

        public class ObjectInfo
        {
            public long PathId { get; set; }
            public int ClassId { get; set; }
            public string TypeName { get; set; } = string.Empty;
            public long ByteStart { get; set; }
            public uint ByteSize { get; set; }
            public byte[] Data { get; set; } = Array.Empty<byte>();
        }
    }
}
