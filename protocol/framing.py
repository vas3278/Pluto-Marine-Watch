"""PMW1 binary framing, baseline PCM transport."""
import json
import struct
import zlib

PREFIX = struct.Struct(">4sII")
MAX_HEADER = 16384
MAX_PAYLOAD = 1048576

def encode(header, payload=b""):
    payload = bytes(payload)
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("payload too large")
    h = dict(header)
    h["payload_crc32"] = zlib.crc32(payload)
    raw = json.dumps(h, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_HEADER:
        raise ValueError("header too large")
    return PREFIX.pack(b"PMW1", len(raw), len(payload)) + raw + payload

def decode(frame):
    if len(frame) < PREFIX.size:
        raise ValueError("truncated prefix")
    magic, nh, np = PREFIX.unpack_from(frame)
    if magic != b"PMW1" or not 0 < nh <= MAX_HEADER or np > MAX_PAYLOAD:
        raise ValueError("invalid prefix")
    if len(frame) != PREFIX.size + nh + np:
        raise ValueError("invalid frame length")
    h = json.loads(frame[PREFIX.size:PREFIX.size+nh].decode("utf-8"))
    payload = frame[PREFIX.size+nh:]
    if not isinstance(h, dict) or h.get("payload_crc32") != zlib.crc32(payload):
        raise ValueError("invalid header or CRC")
    return h, payload
