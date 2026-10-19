#!/usr/bin/env python3
"""Convert hwind2021 Quantumult X blocking lists to Loon remote rules."""
from __future__ import annotations

import argparse
import ipaddress
import re
import os
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "https://raw.githubusercontent.com/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/filter/"
LICENSE = "https://github.com/hwind2021/QuantumultX-AdBlock-CN/blob/main/LICENSE"
FEEDS = {"Splash-Killer": 300, "BlockHttpDNS": 40, "AdBlock-Lite": 12000}
MAP = {"HOST": "DOMAIN", "HOST-SUFFIX": "DOMAIN-SUFFIX", "HOST-KEYWORD": "DOMAIN-KEYWORD", "IP-CIDR": "IP-CIDR", "IP6-CIDR": "IP-CIDR6"}
MAX_RULES = 100000


class SyncError(Exception):
    pass


def fetch(name):
    url = BASE + name + ".list"
    request = Request(url, headers={"User-Agent": "Loon-AdBlock-Sync/1.0", "Accept": "text/plain"})
    last_error = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as reply:
                data = reply.read(5000001)
            if len(data) > 5000000:
                raise SyncError(name + ": upstream file too large")
            return data.decode("utf-8-sig")
        except (HTTPError, URLError, TimeoutError, UnicodeError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise SyncError(f"{name}: download failed: {last_error}")


def parse(source, name, minimum):
    found = set()
    rules = []
    for lineno, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(("#", ";", "//")):
            continue
        fields = [f.strip() for f in line.split(",")]
        if len(fields) < 3:
            raise SyncError(f"{name}:{lineno}: malformed rule: {line[:120]}")
        kind, value, policy, *flags = fields
        target = MAP.get(kind.upper())
        if not target or not value or policy.upper() != "REJECT":
            raise SyncError(f"{name}:{lineno}: unsupported rule: {line[:120]}")
        if flags and (flags != ["no-resolve"] or target not in ("IP-CIDR", "IP-CIDR6")):
            raise SyncError(f"{name}:{lineno}: unsupported parameters: {line[:120]}")
        if target in ("IP-CIDR", "IP-CIDR6"):
            try:
                addr = ipaddress.ip_network(value, strict=False)
            except ValueError as exc:
                raise SyncError(f"{name}:{lineno}: invalid IP: {value}") from exc
            if addr.version != (4 if target == "IP-CIDR" else 6):
                raise SyncError(f"{name}:{lineno}: incorrect IP version: {value}")
        elif any(ch.isspace() for ch in value):
            raise SyncError(f"{name}:{lineno}: whitespace in domain: {value}")
        converted = ",".join((target, value, *flags))
        if converted not in found:
            found.add(converted)
            rules.append(converted)
    if not minimum <= len(rules) <= MAX_RULES:
        raise SyncError(f"{name}: unexpected rule count {len(rules)} (minimum {minimum})")
    return rules


def upstream_metadata(source, expected_name):
    """Read the upstream's own updated timestamp, author and description."""
    values = {}
    for line in source.splitlines():
        match = re.fullmatch(r"#\s*(NAME|AUTHOR|UPDATED|DESC):\s*(.*)", line.strip())
        if match:
            values[match.group(1)] = match.group(2).strip()
    if values.get("NAME") != expected_name:
        raise SyncError(f"{expected_name}: upstream NAME missing or changed")
    updated = values.get("UPDATED", "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \(UTC\+8\)", updated):
        raise SyncError(f"{expected_name}: upstream UPDATED missing or invalid: {updated!r}")
    if not values.get("DESC") or not values.get("AUTHOR"):
        raise SyncError(f"{expected_name}: upstream description or author missing")
    return values


def render(name, rules, metadata):
    updated = metadata["UPDATED"]
    description = metadata["DESC"]
    author = metadata["AUTHOR"]
    loon_date = updated.replace("-", "/").split(" (UTC+8)")[0]
    header = [
        f"#!name={name} (Loon)",
        f"#!desc={description}",
        f"#!date={loon_date}",
        f"# NAME: {name} (Loon)",
        f"# 规则用途: {description}",
        f"# 原作者: {author}",
        f"# 上游更新时间: {updated}",
        "# 自动检查间隔: 每 12 小时（GitHub Actions，运行时间可能延迟）",
        "# 更新时间说明: 来自原 QX 规则的 UPDATED；实际检查时间请查看仓库 Actions。",
        "# Loon 使用方法: 添加为远程规则，策略选择 REJECT；不是插件，无需 MITM。",
        f"# UPSTREAM: {BASE}{name}.list",
        f"# SOURCE LICENSE: {LICENSE}",
        f"# Rule count: {len(rules)}",
        "",
    ]
    return "\n".join(header + rules) + "\n"


def check_retention(path, rules):
    if not path.exists():
        return
    previous = [v.strip() for v in path.read_text(encoding="utf-8").splitlines()
                if v.strip() and not v.lstrip().startswith(("#", "//", ";"))]
    if previous and len(rules) < len(previous) * 0.65:
        raise SyncError(f"{path.name}: suspicious shrink {len(previous)} -> {len(rules)}")


def synchronize(destination=Path("loon"), dry_run=False):
    generated = {}
    for name, minimum in FEEDS.items():
        source = fetch(name)
        metadata = upstream_metadata(source, name)
        rules = parse(source, name, minimum)
        target = destination / f"{name}.list"
        check_retention(target, rules)
        generated[target] = render(name, rules, metadata)
        print(f"{name}: validated {len(rules)} rules")
    if dry_run:
        return
    destination.mkdir(parents=True, exist_ok=True)
    for path, data in generated.items():
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=destination, delete=False) as handle:
                handle.write(data)
                temporary = handle.name
            os.replace(temporary, path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=Path("loon"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        synchronize(args.destination, dry_run=args.dry_run)
    except SyncError as exc:
        parser.exit(1, f"SYNC FAILED: {exc}\n")


if __name__ == "__main__":
    main()
