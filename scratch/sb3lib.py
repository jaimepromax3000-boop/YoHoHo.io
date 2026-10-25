"""Mini-DSL para generar proyectos Scratch 3 (.sb3) desde Python.

Los bloques se escriben como expresiones/listas de Python y se serializan
al formato project.json que usa Scratch 3 / TurboWarp.
"""
import hashlib, json, zipfile, itertools, io

_ids = itertools.count(1)


def uid(prefix="b"):
    return f"{prefix}{next(_ids):06d}"


# ---------------------------------------------------------------- expresiones
class E:
    """Bloque reportero (valor) o booleano."""
    def __init__(self, op, inputs=None, fields=None, mutation=None, boolean=False):
        self.op, self.inputs, self.fields = op, inputs or {}, fields or {}
        self.mutation, self.boolean = mutation, boolean

    def __add__(s, o): return E("operator_add", {"NUM1": s, "NUM2": o})
    def __radd__(s, o): return E("operator_add", {"NUM1": o, "NUM2": s})
    def __sub__(s, o): return E("operator_subtract", {"NUM1": s, "NUM2": o})
    def __rsub__(s, o): return E("operator_subtract", {"NUM1": o, "NUM2": s})
    def __mul__(s, o): return E("operator_multiply", {"NUM1": s, "NUM2": o})
    def __rmul__(s, o): return E("operator_multiply", {"NUM1": o, "NUM2": s})
    def __truediv__(s, o): return E("operator_divide", {"NUM1": s, "NUM2": o})
    def __rtruediv__(s, o): return E("operator_divide", {"NUM1": o, "NUM2": s})
    def __mod__(s, o): return E("operator_mod", {"NUM1": s, "NUM2": o})
    def __rmod__(s, o): return E("operator_mod", {"NUM1": o, "NUM2": s})
    def __neg__(s): return E("operator_subtract", {"NUM1": 0, "NUM2": s})
    def __lt__(s, o): return E("operator_lt", {"OPERAND1": s, "OPERAND2": o}, boolean=True)
    def __gt__(s, o): return E("operator_gt", {"OPERAND1": s, "OPERAND2": o}, boolean=True)
    def __le__(s, o): return ~(s > o)
    def __ge__(s, o): return ~(s < o)
    def __and__(s, o): return E("operator_and", {"OPERAND1": s, "OPERAND2": o}, boolean=True)
    def __rand__(s, o): return E("operator_and", {"OPERAND1": o, "OPERAND2": s}, boolean=True)
    def __or__(s, o): return E("operator_or", {"OPERAND1": s, "OPERAND2": o}, boolean=True)
    def __ror__(s, o): return E("operator_or", {"OPERAND1": o, "OPERAND2": s}, boolean=True)
    def __invert__(s): return E("operator_not", {"OPERAND": s}, boolean=True)
    __hash__ = object.__hash__


def eq(a, b): return E("operator_equals", {"OPERAND1": a, "OPERAND2": b}, boolean=True)
def ne(a, b): return ~eq(a, b)
def rnd(a, b): return E("operator_random", {"FROM": a, "TO": b})
def join(a, b): return E("operator_join", {"STRING1": a, "STRING2": b})
def letter(i, s): return E("operator_letter_of", {"LETTER": i, "STRING": s})
def strlen(s): return E("operator_length", {"STRING": s})
def rround(a): return E("operator_round", {"NUM": a})
def mathop(op, a): return E("operator_mathop", {"NUM": a}, {"OPERATOR": [op, None]})
def floor(a): return mathop("floor", a)
def fabs(a): return mathop("abs", a)
def sqrt(a): return mathop("sqrt", a)
def sin(a): return mathop("sin", a)
def cos(a): return mathop("cos", a)
def atan(a): return mathop("atan", a)
def asin(a): return mathop("asin", a)
def emin(a, b): return E("__min", {"A": a, "B": b})  # se expande abajo
def emax(a, b): return E("__max", {"A": a, "B": b})
def clamp(v, lo, hi): return emax(lo, emin(v, hi))


def mouse_x(): return E("sensing_mousex")
def mouse_y(): return E("sensing_mousey")
def mouse_down(): return E("sensing_mousedown", boolean=True)
def timer(): return E("sensing_timer")
def answer(): return E("sensing_answer")
def costume_number(): return E("looks_costumenumbername", fields={"NUMBER_NAME": ["number", None]})
def key_pressed(key):
    return E("sensing_keypressed", {"KEY_OPTION": ("menu", "sensing_keyoptions", "KEY_OPTION", key)}, boolean=True)


# ------------------------------------------------------------ statements
class S:
    def __init__(self, op, inputs=None, fields=None, mutation=None, subs=None):
        self.op, self.inputs, self.fields = op, inputs or {}, fields or {}
        self.mutation, self.subs = mutation, subs or {}


def stmt(op, **inp): return S(op, inp)


class Project:
    def __init__(self):
        self.vars, self.lists = {}, {}          # nombre -> (id, valor inicial)
        self.sprites = []                       # dicts de target
        self.assets = {}                        # md5ext -> bytes
        self.procs = {}                         # nombre -> info

    # ---- variables y listas (todas globales, viven en el Stage)
    def var(self, name, init=0):
        if name not in self.vars:
            self.vars[name] = (uid("v"), init)
        return self.vars[name]

    def lst(self, name, init=None):
        if name not in self.lists:
            self.lists[name] = (uid("l"), init or [])
        return self.lists[name]

    def V(self, name):
        i, _ = self.var(name)
        return E("data_variable", fields={"VARIABLE": [name, i]})

    def L(self, name):
        i, _ = self.lst(name)
        return i

    def add_asset(self, data, ext):
        md5 = hashlib.md5(data).hexdigest()
        self.assets[f"{md5}.{ext}"] = data
        return md5


P = Project()


def V(name): return P.V(name)


# ---- sentencias de datos
def setv(name, val):
    i, _ = P.var(name)
    return S("data_setvariableto", {"VALUE": val}, {"VARIABLE": [name, i]})

def chgv(name, val):
    i, _ = P.var(name)
    return S("data_changevariableby", {"VALUE": val}, {"VARIABLE": [name, i]})

def lfield(name):
    return {"LIST": [name, P.L(name)]}

def l_add(name, item): return S("data_addtolist", {"ITEM": item}, lfield(name))
def l_del(name, idx): return S("data_deleteoflist", {"INDEX": idx}, lfield(name))
def l_clear(name): return S("data_deletealloflist", {}, lfield(name))
def l_ins(name, idx, item): return S("data_insertatlist", {"INDEX": idx, "ITEM": item}, lfield(name))
def l_set(name, idx, item): return S("data_replaceitemoflist", {"INDEX": idx, "ITEM": item}, lfield(name))
def l_get(name, idx): return E("data_itemoflist", {"INDEX": idx}, lfield(name))
def l_len(name): return E("data_lengthoflist", {}, lfield(name))
def l_find(name, item): return E("data_itemnumoflist", {"ITEM": item}, lfield(name))
def l_has(name, item): return E("data_listcontainsitem", {"ITEM": item}, lfield(name), boolean=True)


# ---- control
def If(cond, then, els=None):
    if els is None:
        return S("control_if", {"CONDITION": cond}, subs={"SUBSTACK": then})
    return S("control_if_else", {"CONDITION": cond}, subs={"SUBSTACK": then, "SUBSTACK2": els})
def Repeat(n, body): return S("control_repeat", {"TIMES": n}, subs={"SUBSTACK": body})
def Forever(body): return S("control_forever", subs={"SUBSTACK": body})
def Until(cond, body): return S("control_repeat_until", {"CONDITION": cond}, subs={"SUBSTACK": body})
def Wait(t): return S("control_wait", {"DURATION": t})
def WaitUntil(c): return S("control_wait_until", {"CONDITION": c})
def StopAll(): return S("control_stop", fields={"STOP_OPTION": ["all", None]}, mutation={"tagName": "mutation", "children": [], "hasnext": "false"})
def StopThis(): return S("control_stop", fields={"STOP_OPTION": ["this script", None]}, mutation={"tagName": "mutation", "children": [], "hasnext": "false"})

# ---- motion / looks / pen
def goto(x, y): return S("motion_gotoxy", {"X": x, "Y": y})
def direction(d): return S("motion_pointindirection", {"DIRECTION": d})
def hide(): return S("looks_hide")
def show(): return S("looks_show")
def size_to(p): return S("looks_setsizeto", {"SIZE": p})
def costume(n): return S("looks_switchcostumeto", {"COSTUME": ("costumeexpr", n)})
def pen_clear(): return S("pen_clear")
def stamp(): return S("pen_stamp")
def pen_down(): return S("pen_penDown")
def pen_up(): return S("pen_penUp")
def pen_size(n): return S("pen_setPenSizeTo", {"SIZE": n})
def pen_color(hexcolor): return S("pen_setPenColorToColor", {"COLOR": ("color", hexcolor)})
def pen_transp(t): return S("pen_setPenColorParamTo", {"COLOR_PARAM": ("menu", "pen_menu_colorParam", "colorParam", "transparency"), "VALUE": t})
def ask(q): return S("sensing_askandwait", {"QUESTION": q})
def reset_timer(): return S("sensing_resettimer")
def effect(name, v): return S("looks_seteffectto", {"EFFECT": ("field_only",), "VALUE": v}, {"EFFECT": [name, None]})


# ---- procedimientos propios
class Proc:
    def __init__(self, name, params, body, warp=True):
        self.name, self.params, self.body, self.warp = name, params, body, warp
        self.arg_ids = [uid("a") for _ in params]
        self.proccode = name + "".join(" %s" for _ in params)
        P.procs[name] = self


def arg(name): return E("argument_reporter_string_number", fields={"VALUE": [name, None]})


def call(name, *args):
    return S("__call", {"name": name, "args": list(args)})


def define(name, params, body, warp=True):
    return Proc(name, params, body, warp)


# ---------------------------------------------------------- serializador
class Target:
    def __init__(self, name, stage=False):
        self.name, self.stage = name, stage
        self.blocks = {}
        self.costumes = []
        self.scripts = []      # (hat, body, x, y)
        self.procs = []
        self.comments = {}
        self.y_cursor = 0

    def add_costume(self, name, data, ext, rcx, rcy, res=1):
        md5 = P.add_asset(data, ext)
        self.costumes.append({"name": name, "bitmapResolution": res, "dataFormat": ext,
                              "assetId": md5, "md5ext": f"{md5}.{ext}",
                              "rotationCenterX": rcx, "rotationCenterY": rcy})
        return len(self.costumes)   # indice 1-based

    # --- hats
    def on_flag(self, body): self.scripts.append((S("event_whenflagclicked"), body))
    def on_key(self, key, body): self.scripts.append((S("event_whenkeypressed", fields={"KEY_OPTION": [key, None]}), body))
    def on_click(self, body): self.scripts.append((S("event_whenthisspriteclicked"), body))

    # ---------- compilación
    def _new(self, op, parent=None, shadow=False, top=False):
        bid = uid()
        self.blocks[bid] = {"opcode": op, "next": None, "parent": parent, "inputs": {}, "fields": {},
                            "shadow": shadow, "topLevel": top}
        return bid

    def _menu(self, parent, op, field, value):
        bid = self._new(op, parent, shadow=True)
        self.blocks[bid]["fields"][field] = [value, None]
        return bid

    def _val(self, v, parent, boolean=False):
        """Devuelve el input [..] para un valor python o expresión."""
        if isinstance(v, E):
            rid = self._expr(v, parent)
            if boolean or v.boolean:
                return [2, rid]
            return [3, rid, [4, "0"]]
        if isinstance(v, bool):
            return [1, [10, "true" if v else "false"]]
        if isinstance(v, (int, float)):
            s = repr(int(v)) if float(v).is_integer() else repr(float(v))
            return [1, [4, s]]
        return [1, [10, str(v)]]

    def _expr(self, e, parent):
        if e.op == "__min" or e.op == "__max":
            # min(a,b) = if a<b then a else b  -> expresión aritmética sin ramas:
            # min = (a+b-|a-b|)/2 ; max = (a+b+|a-b|)/2
            a, b = e.inputs["A"], e.inputs["B"]
            sgn = "-" if e.op == "__min" else "+"
            core = (a + b - fabs(a - b)) / 2 if sgn == "-" else (a + b + fabs(a - b)) / 2
            return self._expr(core, parent)
        bid = self._new(e.op, parent)
        b = self.blocks[bid]
        for k, v in e.inputs.items():
            b["inputs"][k] = self._input(k, v, bid)
        b["fields"] = {k: list(v) for k, v in e.fields.items()}
        if e.mutation: b["mutation"] = e.mutation
        return bid

    def _input(self, name, v, parent):
        if isinstance(v, tuple):
            kind = v[0]
            if kind == "menu":
                mid = self._menu(parent, v[1], v[2], v[3])
                return [1, mid]
            if kind == "color":
                return [1, [9, v[1]]]
            if kind == "costumeexpr":
                val = v[1]
                if isinstance(val, E):
                    rid = self._expr(val, parent)
                    mid = self._menu(parent, "looks_costume", "COSTUME", "1")
                    return [3, rid, [1, mid]] if False else [3, rid, mid]
                mid = self._menu(parent, "looks_costume", "COSTUME", str(val))
                return [1, mid]
        return self._val(v, parent)

    def _stack(self, stmts, parent, top=False):
        first = prev = None
        for s in stmts:
            if s is None: continue
            if isinstance(s, list):   # permitir listas anidadas
                sub = self._stack(s, parent)
                if sub is None: continue
                # engancha la sublista: simplemente la expandimos
                raise ValueError("usa flat(...) para listas anidadas")
            bid = self._stmt(s, prev if prev else parent, top and first is None)
            if first is None: first = bid
            if prev: self.blocks[prev]["next"] = bid
            prev = bid
        return first

    def _stmt(self, s, parent, top=False):
        if s.op == "__call":
            p = P.procs[s.inputs["name"]]
            bid = self._new("procedures_call", parent, top=top)
            b = self.blocks[bid]
            b["mutation"] = {"tagName": "mutation", "children": [], "proccode": p.proccode,
                             "argumentids": json.dumps(p.arg_ids), "warp": "true" if p.warp else "false"}
            for aid, a in zip(p.arg_ids, s.inputs["args"]):
                b["inputs"][aid] = self._input(aid, a, bid)
            return bid
        bid = self._new(s.op, parent, top=top)
        b = self.blocks[bid]
        for k, v in s.inputs.items():
            b["inputs"][k] = self._input(k, v, bid)
        b["fields"] = {k: list(v) for k, v in s.fields.items()}
        if s.mutation: b["mutation"] = s.mutation
        for k, sub in s.subs.items():
            first = self._stack(flat(sub), bid)
            if first:
                b["inputs"][k] = [2, first]
        return bid

    def compile(self):
        y = 0
        for hat, body in self.scripts:
            hid = self._stmt(hat, None, top=True)
            self.blocks[hid].update({"x": 0, "y": y})
            first = self._stack(flat(body), hid)
            if first:
                self.blocks[hid]["next"] = first
                self.blocks[first]["parent"] = hid
            y += 400
        for p in self.procs:
            self._compile_proc(p, y); y += 400

    def _compile_proc(self, p, y):
        did = self._new("procedures_definition", None, top=True)
        self.blocks[did].update({"x": 800, "y": y})
        pid = self._new("procedures_prototype", did, shadow=True)
        pb = self.blocks[pid]
        pb["mutation"] = {"tagName": "mutation", "children": [], "proccode": p.proccode,
                          "argumentids": json.dumps(p.arg_ids), "argumentnames": json.dumps(p.params),
                          "argumentdefaults": json.dumps(["" for _ in p.params]),
                          "warp": "true" if p.warp else "false"}
        for aid, an in zip(p.arg_ids, p.params):
            rid = self._new("argument_reporter_string_number", pid, shadow=True)
            self.blocks[rid]["fields"]["VALUE"] = [an, None]
            pb["inputs"][aid] = [1, rid]
        self.blocks[did]["inputs"]["custom_block"] = [1, pid]
        first = self._stack(flat(p.body), did)
        if first:
            self.blocks[did]["next"] = first
            self.blocks[first]["parent"] = did

    def json(self, vars_, lists_):
        d = {"isStage": self.stage, "name": self.name,
             "variables": {i: [n, v] for n, (i, v) in vars_.items()} if self.stage else {},
             "lists": {i: [n, v] for n, (i, v) in lists_.items()} if self.stage else {},
             "broadcasts": {}, "blocks": self.blocks, "comments": self.comments,
             "currentCostume": 0, "costumes": self.costumes, "sounds": [], "volume": 100,
             "layerOrder": 0 if self.stage else 1}
        return d


def flat(x):
    out = []
    for i in x:
        if isinstance(i, (list, tuple)) and not isinstance(i, E):
            out.extend(flat(i))
        elif i is not None:
            out.append(i)
    return out


def write_sb3(path, stage, sprites, tw_config=None):
    # los procedimientos se asignan al sprite que los define
    for t in [stage] + sprites:
        t.compile()
    stage_json = stage.json(P.vars, P.lists)
    if tw_config:
        cid = uid("c")
        stage_json["comments"][cid] = {"blockId": None, "x": 0, "y": 0, "width": 350, "height": 170, "minimized": True,
            "text": "Configuration for https://turbowarp.org/\nYou can move, resize, and minimize this comment, but don't edit it by hand. This comment can be deleted to remove the stored settings.\n // _twconfig_ " + json.dumps(tw_config)}
    targets = [stage_json]
    for i, s in enumerate(sprites):
        j = s.json(P.vars, P.lists)
        j.update({"visible": getattr(s, "visible", False), "x": 0, "y": 0, "size": 100, "direction": 90,
                  "draggable": False, "rotationStyle": "all around"})
        j["layerOrder"] = i + 1
        targets.append(j)
    project = {"targets": targets, "monitors": [], "extensions": ["pen"],
               "meta": {"semver": "3.0.0", "vm": "0.2.0", "agent": "YoHoHo.io -> Scratch generator"}}
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps(project, separators=(",", ":")))
        for name, data in P.assets.items():
            z.writestr(name, data)
    return project
