#!/usr/bin/env python3
"""Lint the hand-drawn inline SVG diagrams of an HTML page.

Usage: python3 svg_lint.py page.html [--quiet]

Errors (exit code 1):
  parse      an SVG fragment is not well-formed XML
  marker-id  one marker id is defined in more than one place on the page
  occluded   a connector runs under a filled shape that is painted after it
  viewbox    a text runs outside the viewBox
Warnings:
  overflow   a text runs past the edge of the box that it starts in
  no-head    a solid connector ends on a shape edge without an arrowhead
  text-line  a text crosses a connector
  text-text  two texts overlap

Text widths are estimates from the page CSS: a CJK glyph is 1.0 em, a Latin glyph about 0.56 em,
a monospace glyph 0.6 em. Rotated texts are skipped. Dashed connectors are associations and need
no arrowhead. Lifelines use the class `life` and are skipped.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET

DEFAULT_SIZE = 12.5
CJK_RANGES = [(0x2460, 0x24FF), (0x2E80, 0x9FFF), (0xF900, 0xFAFF), (0xFE30, 0xFE4F), (0xFF00, 0xFFEF)]
WIDE_PUNCT = set("「」『』，。：；（）？！、…—“”‘’《》【】")


def css_text_styles(html):
    """Map a class name to its font size, monospace flag, and bold flag, from `.x .cls {}` rules."""
    styles = {}
    base = {"size": DEFAULT_SIZE, "mono": False, "bold": False}
    css = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", html))
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        props = {}
        m = re.search(r"font-size:\s*([\d.]+)px", body)
        if m:
            props["size"] = float(m.group(1))
        if re.search(r"font-family:[^;]*mono", body, re.I):
            props["mono"] = True
        elif "font-family" in body:
            props["mono"] = False
        if re.search(r"font-weight:\s*(600|700|800|bold)", body):
            props["bold"] = True
        if not props:
            continue
        for sel in selectors.split(","):
            last = sel.strip().split()[-1] if sel.strip() else ""
            if last == "text" and sel.strip().startswith("."):
                base.update(props)
            elif last.startswith(".") and len(sel.strip().split()) >= 2:
                styles.setdefault(last[1:], {}).update(props)
    return base, styles


def char_em(ch, mono):
    code = ord(ch)
    if ch in WIDE_PUNCT or any(lo <= code <= hi for lo, hi in CJK_RANGES):
        return 1.0
    if mono:
        return 0.6
    if ch == " ":
        return 0.28
    if ch in "il.,:;|!'`":
        return 0.3
    if ch.isupper() or ch in "mwMW@%":
        return 0.68
    return 0.55


def num(el, name, default=0.0):
    value = el.get(name)
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def path_points(d):
    """Return polylines for absolute and relative M, L, H, V, C, Z commands. Curves are sampled."""
    tokens = re.findall(r"[MLHVCZmlhvcz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    lines, current, cmd = [], [], None
    x = y = 0.0
    start = (0.0, 0.0)
    i = 0

    def take(n):
        nonlocal i
        vals = [float(t) for t in tokens[i:i + n]]
        i += n
        return vals

    while i < len(tokens):
        t = tokens[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                if current:
                    current.append(start)
                continue
        if cmd is None:
            break
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            nx, ny = take(2)
            x, y = (x + nx, y + ny) if rel else (nx, ny)
            if current:
                lines.append(current)
            current = [(x, y)]
            start = (x, y)
            cmd = "l" if rel else "L"
        elif c == "L":
            nx, ny = take(2)
            x, y = (x + nx, y + ny) if rel else (nx, ny)
            current.append((x, y))
        elif c == "H":
            (nx,) = take(1)
            x = x + nx if rel else nx
            current.append((x, y))
        elif c == "V":
            (ny,) = take(1)
            y = y + ny if rel else ny
            current.append((x, y))
        elif c == "C":
            vals = take(6)
            if rel:
                vals = [vals[k] + (x if k % 2 == 0 else y) for k in range(6)]
            x0, y0 = x, y
            x1, y1, x2, y2, x3, y3 = vals
            for s in range(1, 13):
                u = s / 12
                bx = (1 - u) ** 3 * x0 + 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3 * x3
                by = (1 - u) ** 3 * y0 + 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u * u * y2 + u ** 3 * y3
                current.append((bx, by))
            x, y = x3, y3
        else:
            i += 1
    if current:
        lines.append(current)
    return [p for p in lines if len(p) >= 2]


def seg_hits_box(p, q, box):
    """True when segment p-q crosses the rectangle (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    steps = max(2, int(math.dist(p, q) / 3))
    for s in range(steps + 1):
        u = s / steps
        px, py = p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u
        if x0 < px < x1 and y0 < py < y1:
            return True
    return False


def lint_svg(index, svg_text, base, styles):
    issues = []
    label = ""
    m = re.search(r'aria-label="([^"]*)"', svg_text)
    if m:
        label = m.group(1)[:28]
    try:
        root = ET.fromstring(svg_text.replace("&nbsp;", " "))
    except ET.ParseError as exc:
        return [("error", "parse", str(exc))], label, []

    vb = [float(v) for v in (root.get("viewBox") or "0 0 0 0").replace(",", " ").split()]
    vw, vh = vb[2], vb[3]
    marker_ids = [el.get("id") for el in root.iter("marker") if el.get("id")]

    in_defs = set()
    for defs in list(root.iter("defs")) + list(root.iter("marker")):
        for el in defs.iter():
            in_defs.add(el)

    rects, connectors, texts = [], [], []
    for order, el in enumerate(root.iter()):
        if el in in_defs:
            continue
        cls = (el.get("class") or "").split()
        if el.tag == "rect":
            if el.get("fill") == "none":
                continue
            x, y, w, h = num(el, "x"), num(el, "y"), num(el, "width"), num(el, "height")
            rects.append({"order": order, "box": (x, y, x + w, y + h), "area": w * h})
        elif el.tag in ("line", "path"):
            if "life" in cls:
                continue
            if el.tag == "line":
                polys = [[(num(el, "x1"), num(el, "y1")), (num(el, "x2"), num(el, "y2"))]]
                desc = "line %g,%g→%g,%g" % (num(el, "x1"), num(el, "y1"), num(el, "x2"), num(el, "y2"))
            else:
                d = el.get("d") or ""
                polys = path_points(d)
                desc = "path " + d[:40]
            dashed = "dash" in cls or el.get("stroke-dasharray") is not None
            connectors.append({"order": order, "polys": polys, "desc": desc, "dashed": dashed,
                               "head_end": el.get("marker-end") is not None})
        elif el.tag == "text":
            content = "".join(el.itertext()).strip()
            if not content:
                continue
            style = dict(base)
            for c in cls:
                style.update(styles.get(c, {}))
            size = style["size"]
            width = sum(char_em(ch, style["mono"]) for ch in content) * size * (1.04 if style["bold"] else 1.0)
            x, y = num(el, "x"), num(el, "y")
            anchor = el.get("text-anchor", "start")
            left = x - width if anchor == "end" else x - width / 2 if anchor == "middle" else x
            rotated = "rotate" in (el.get("transform") or "")
            texts.append({"order": order, "text": content[:24], "x": x, "y": y, "rotated": rotated,
                          "box": (left, y - 0.8 * size, left + width, y + 0.22 * size)})

    for t in texts:
        if t["rotated"]:
            continue
        x0, y0, x1, y1 = t["box"]
        if x0 < -1 or x1 > vw + 1 or y0 < -1 or y1 > vh + 1:
            issues.append(("error", "viewbox", '"%s" spans x %.0f–%.0f, y %.0f–%.0f; viewBox is %gx%g'
                           % (t["text"], x0, x1, y0, y1, vw, vh)))
        probe = (x0 + 1, t["y"] - 3)
        holders = [r for r in rects if r["order"] < t["order"]
                   and r["box"][0] <= probe[0] <= r["box"][2] and r["box"][1] <= probe[1] <= r["box"][3]]
        if holders:
            r = min(holders, key=lambda h: h["area"])
            bx0, _, bx1, _ = r["box"]
            over = max(bx0 + 2 - x0, x1 - (bx1 - 2))
            if over > 0.5:
                issues.append(("warn", "overflow", '"%s" passes its box edge by about %.0f px' % (t["text"], over)))

    for c in connectors:
        for poly in c["polys"]:
            for p, q in zip(poly, poly[1:]):
                trimmed = []
                length = math.dist(p, q)
                if length < 1:
                    continue
                cut = min(4.0, length / 3) / length
                a = (p[0] + (q[0] - p[0]) * cut, p[1] + (q[1] - p[1]) * cut)
                b = (q[0] - (q[0] - p[0]) * cut, q[1] - (q[1] - p[1]) * cut)
                trimmed.append((a, b))
                for r in rects:
                    if r["order"] <= c["order"]:
                        continue
                    bx0, by0, bx1, by1 = r["box"]
                    if seg_hits_box(a, b, (bx0 + 1.5, by0 + 1.5, bx1 - 1.5, by1 - 1.5)):
                        issues.append(("error", "occluded", "%s runs under a shape painted later at %.0f,%.0f "
                                       "(draw connectors after the zones and boxes they cross)" % (c["desc"], bx0, by0)))
                        break
        if not c["dashed"] and not c["head_end"] and c["polys"]:
            end = c["polys"][-1][-1]
            for r in rects:
                bx0, by0, bx1, by1 = r["box"]
                near_x = bx0 - 4 <= end[0] <= bx1 + 4
                near_y = by0 - 4 <= end[1] <= by1 + 4
                on_edge = near_x and near_y and (min(abs(end[0] - bx0), abs(end[0] - bx1)) <= 4
                                                  or min(abs(end[1] - by0), abs(end[1] - by1)) <= 4)
                if on_edge:
                    issues.append(("warn", "no-head", "%s ends on a shape edge without an arrowhead "
                                   "(use a bus with one arrow, or a dashed association)" % c["desc"]))
                    break

    for t in texts:
        if t["rotated"]:
            continue
        x0, y0, x1, y1 = t["box"]
        box = (x0 + 1, y0 + 1, x1 - 1, y1 - 1)
        for c in connectors:
            hit = any(seg_hits_box(p, q, box) for poly in c["polys"] for p, q in zip(poly, poly[1:]))
            if hit:
                issues.append(("warn", "text-line", '"%s" crosses %s' % (t["text"], c["desc"])))
    plain = [t for t in texts if not t["rotated"]]
    for i, a in enumerate(plain):
        for b in plain[i + 1:]:
            ax0, ay0, ax1, ay1 = a["box"]
            bx0, by0, bx1, by1 = b["box"]
            if min(ax1, bx1) - max(ax0, bx0) > 1 and min(ay1, by1) - max(ay0, by0) > 1:
                issues.append(("warn", "text-text", '"%s" overlaps "%s"' % (a["text"], b["text"])))
    return issues, label, marker_ids


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    quiet = "--quiet" in argv
    html = open(argv[1], encoding="utf-8").read()
    base, styles = css_text_styles(html)
    svgs = re.findall(r"<svg\b[\s\S]*?</svg>", html)
    errors = warnings = 0
    seen = {}
    for n, svg in enumerate(svgs, 1):
        issues, label, markers = lint_svg(n, svg, base, styles)
        for mid in markers:
            seen.setdefault(mid, []).append(n)
        if issues and not (quiet and all(level == "warn" for level, _, _ in issues)):
            print('svg #%d "%s"' % (n, label))
        for level, kind, msg in issues:
            if level == "error":
                errors += 1
            else:
                warnings += 1
            if level == "error" or not quiet:
                print("  %-5s %-9s %s" % (level, kind, msg))
    for mid, where in seen.items():
        if len(where) > 1:
            errors += 1
            print("error marker-id  id %r is defined in svg %s" % (mid, where))
    print("%d svg, %d error, %d warning" % (len(svgs), errors, warnings))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
