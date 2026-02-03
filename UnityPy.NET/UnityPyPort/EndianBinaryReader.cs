using System;
using System.IO;
using System.Text;

namespace UnityPyPort
{
    /// <summary>
    /// Binary reader that supports both big-endian and little-endian reading
    /// </summary>
    public class EndianBinaryReader : IDisposable
    {
        private readonly Stream _stream;
        private readonly bool _isBigEndian;
        private bool _disposed;

        public long Position
        {
            get => _stream.Position;
            set => _stream.Position = value;
        }

        public long Length => _stream.Length;

        public bool IsBigEndian => _isBigEndian;

        public EndianBinaryReader(Stream stream, bool isBigEndian = false)
        {
            _stream = stream ?? throw new ArgumentNullException(nameof(stream));
            _isBigEndian = isBigEndian;
        }

        public byte ReadByte()
        {
            return (byte)_stream.ReadByte();
        }

        public byte[] ReadBytes(int count)
        {
            var buffer = new byte[count];
            _stream.Read(buffer, 0, count);
            return buffer;
        }

        public ushort ReadUInt16()
        {
            var bytes = ReadBytes(2);
            if (_isBigEndian != BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            return BitConverter.ToUInt16(bytes, 0);
        }

        public uint ReadUInt32()
        {
            var bytes = ReadBytes(4);
            if (_isBigEndian != BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            return BitConverter.ToUInt32(bytes, 0);
        }

        public int ReadInt32()
        {
            var bytes = ReadBytes(4);
            if (_isBigEndian != BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            return BitConverter.ToInt32(bytes, 0);
        }

        public long ReadInt64()
        {
            var bytes = ReadBytes(8);
            if (_isBigEndian != BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            return BitConverter.ToInt64(bytes, 0);
        }

        public ulong ReadUInt64()
        {
            var bytes = ReadBytes(8);
            if (_isBigEndian != BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            return BitConverter.ToUInt64(bytes, 0);
        }

        public string ReadStringToNull()
        {
            var bytes = new List<byte>();
            int b;
            while ((b = _stream.ReadByte()) > 0)
            {
                bytes.Add((byte)b);
            }
            return Encoding.UTF8.GetString(bytes.ToArray());
        }

        public void AlignStream(int alignment = 4)
        {
            var pos = _stream.Position;
            var mod = pos % alignment;
            if (mod != 0)
                _stream.Position += alignment - mod;
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _stream?.Dispose();
                _disposed = true;
            }
        }
    }
}
