"""Escritor mínimo de NBT (gzip) para plantillas de estructura de Minecraft 1.21.1."""
import gzip, struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BARR, STRING, LIST, COMPOUND, IARR = range(12)


class Tag:
    def __init__(self, t, v, et=None):
        self.t, self.v, self.et = t, v, et


def Int(v): return Tag(INT, v)
def Byte(v): return Tag(BYTE, v)
def Str(v): return Tag(STRING, v)
def Dbl(v): return Tag(DOUBLE, v)
def Comp(d): return Tag(COMPOUND, d)
def List(et, items): return Tag(LIST, items, et)


def _str(buf, s):
    e = s.encode("utf-8")
    buf += struct.pack(">H", len(e)) + e


def _payload(buf, tag):
    t, v = tag.t, tag.v
    if t == BYTE: buf += struct.pack(">b", v)
    elif t == INT: buf += struct.pack(">i", v)
    elif t == DOUBLE: buf += struct.pack(">d", v)
    elif t == STRING: _str(buf, v)
    elif t == LIST:
        buf += struct.pack(">bi", tag.et, len(v))
        for item in v: _payload(buf, item)
    elif t == COMPOUND:
        for k, child in v.items():
            buf += struct.pack(">b", child.t)
            _str(buf, k)
            _payload(buf, child)
        buf += b"\x00"
    else:
        raise ValueError(t)


def dumps(root_dict):
    buf = bytearray()
    buf += struct.pack(">b", COMPOUND)
    _str(buf, "")
    _payload(buf, Comp(root_dict))
    return gzip.compress(bytes(buf), 9, mtime=0)


def parse_state(s):
    """'minecraft:oak_stairs[facing=north,half=bottom]' -> (name, {props})"""
    if "[" not in s:
        return s, {}
    name, rest = s.split("[", 1)
    props = dict(kv.split("=", 1) for kv in rest.rstrip("]").split(",") if kv)
    return name, props


DATA_VERSION = 3955  # Minecraft 1.21.1


def structure_nbt(size, blocks, entities):
    """blocks: {(x,y,z): state_str}; entities: [(x,y,z,entity_id,yaw)]"""
    palette, index = [], {}
    for st in blocks.values():
        if st not in index:
            index[st] = len(palette)
            name, props = parse_state(st)
            d = {"Name": Str(name)}
            if props:
                d["Properties"] = Comp({k: Str(v) for k, v in props.items()})
            palette.append(Comp(d))
    blist = [Comp({"pos": List(INT, [Int(x), Int(y), Int(z)]), "state": Int(index[st])})
             for (x, y, z), st in sorted(blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0]))]
    elist = []
    for (x, y, z, eid, yaw) in entities:
        if ":" not in eid:
            eid = "factionlands:" + eid   # el id debe llevar espacio de nombres o se resuelve como minecraft:<id>
        elist.append(Comp({
            "pos": List(DOUBLE, [Dbl(x + 0.5), Dbl(float(y)), Dbl(z + 0.5)]),
            "blockPos": List(INT, [Int(x), Int(y), Int(z)]),
            "nbt": Comp({"id": Str(eid), "PersistenceRequired": Byte(1)}),
        }))
    root = {
        "DataVersion": Int(DATA_VERSION),
        "size": List(INT, [Int(size[0]), Int(size[1]), Int(size[2])]),
        "palette": List(COMPOUND, palette),
        "blocks": List(COMPOUND, blist),
        "entities": List(COMPOUND, elist),
    }
    return dumps(root)
