#!/usr/bin/env python3
"""Generate the `latest` release body for vmlinux-btf, grouped by architecture.

The release is cumulative: old kernel packages stay, new ones are added.
The body is rebuilt from the full asset list (existing release assets +
this run's dist/) so it always matches what is actually downloadable.

Layout: one section per architecture (## <arch>), each with a table whose
rows are grouped by SDK (25.12 apk first, then 24.10 ipk), kernel versions
newest-first. Download links point at the `latest` tag so they keep working
after the next build.

Usage (CI):
    python3 scripts/gen-release-body.py --repo kenzok8/vmlinux-btf \
        --dist dist --output BODY.md
Usage (local test, no gh call):
    python3 scripts/gen-release-body.py --repo kenzok8/vmlinux-btf \
        --dist dist --assets-file assets.txt --output BODY.md
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

# Display order for architectures: most common first, then gen-matrix order.
ARCH_ORDER = [
    "x86_64",
    "aarch64_generic",
    "aarch64_cortex-a53",
    "aarch64_cortex-a72",
    "arm_cortex-a7_neon-vfpv4",
    "arm_cortex-a9_neon",
    "i386_pentium4",
    "mips_24kc",
    "mipsel_24kc",
]

# apk: vmlinux-btf-6.12.113-r1-x86_64.apk        -> 25.12
# ipk: vmlinux-btf_6.6.151-r1_x86_64.ipk        -> 24.10
APK_RE = re.compile(r"^vmlinux-btf-(.+)-r\d+-(.+)\.apk$")
IPK_RE = re.compile(r"^vmlinux-btf_(.+)-r\d+_(.+)\.ipk$")


def parse(name):
    """Return (sdk, kernel, arch) or None if not a vmlinux-btf package."""
    m = APK_RE.match(name)
    if m:
        return ("25.12", m.group(1), m.group(2))
    m = IPK_RE.match(name)
    if m:
        return ("24.10", m.group(1), m.group(2))
    return None


def kernel_key(version):
    """Sortable key for a kernel version like 6.18.60 (numeric, newest first)."""
    parts = []
    for p in re.split(r"[.-]", version):
        parts.append(int(p) if p.isdigit() else 0)
    return tuple(parts)


def arch_key(arch):
    try:
        return (0, ARCH_ORDER.index(arch))
    except ValueError:
        return (1, arch)


def existing_assets(repo, attempts=3):
    """Asset names already on the `latest` release.

    Retries a few times: two release jobs can update `latest` concurrently
    and the API can 404/409 mid-update. Fails loudly instead of silently
    returning an empty list, otherwise the body would only list this run's
    packages and look like a per-build table instead of the summary.
    """
    last_err = ""
    for i in range(attempts):
        out = subprocess.run(
            ["gh", "api", "--paginate", f"repos/{repo}/releases/tags/latest",
             "--jq", ".assets[].name"],
            capture_output=True, text=True, check=False)
        if out.returncode == 0:
            names = [l.strip() for l in out.stdout.splitlines() if l.strip()]
            print(f"existing release assets: {len(names)}", file=sys.stderr)
            return names
        last_err = (out.stderr or "").strip().splitlines()
        last_err = last_err[-1] if last_err else f"exit {out.returncode}"
        print(f"gh api attempt {i + 1}/{attempts} failed: {last_err}",
              file=sys.stderr)
        time.sleep(5)
    print(f"cannot list existing release assets after {attempts} attempts: "
          f"{last_err}", file=sys.stderr)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--dist", default="dist", help="dir with this run's packages")
    ap.add_argument("--assets-file", help="one asset name per line (local test)")
    ap.add_argument("--output", default="BODY.md")
    args = ap.parse_args()

    names = set()
    if args.assets_file:
        with open(args.assets_file) as f:
            names.update(l.strip() for l in f if l.strip())
    else:
        existing = existing_assets(args.repo)
        if existing is None:
            # Refuse to publish a body that only lists this run's packages.
            return 2
        names.update(existing)
    if os.path.isdir(args.dist):
        names.update(
            f for f in os.listdir(args.dist)
            if f.endswith((".apk", ".ipk")))

    # Group by arch -> list of (sdk, kernel, filename).
    by_arch = {}
    for name in sorted(names):
        parsed = parse(name)
        if not parsed:
            continue
        sdk, kernel, arch = parsed
        by_arch.setdefault(arch, []).append((sdk, kernel, name))

    if not by_arch:
        print("no vmlinux-btf packages found; refusing to write an empty body",
              file=sys.stderr)
        return 1

    lines = []
    lines.append("为 **dae / daed** 提供独立的内核 BTF 数据包，适配**未开启 `CONFIG_DEBUG_INFO_BTF`** 的固件。")
    lines.append("")
    lines.append("dae/daed 的 CO-RE eBPF 运行时需要内核 BTF（`/sys/kernel/btf/vmlinux`）。官方 OpenWrt、在线 ImageBuilder 等固件常常没开，导致 daed 启动失败——装上对应的 vmlinux-btf 包即可补齐这块。")
    lines.append("")
    lines.append("## 如何选包")
    lines.append("")
    lines.append("先看 `uname -r` 拿到内核版本，再按设备架构在下面找到对应的包：25.12 用 `.apk`，24.10 用 `.ipk`。")
    lines.append("")
    lines.append("> 💡 用 [openwrt-daede 一键脚本](https://github.com/kenzok8/openwrt-daede) 安装时会**自动检测内核 BTF、缺失则自动下载安装匹配的包**，无需手动操作。")
    lines.append("")
    lines.append("> ⚠️ 必须按照 `uname -r` 的输出**精确匹配**版本，不要装近似版本。BTF 描述的是具体内核的结构布局，版本不符时 eBPF 校验可能失败，或更糟——跑出错误的字段偏移。")
    lines.append("")
    lines.append("历史内核版本的包会一直保留在这里，不会被新构建覆盖。找不到某个内核版本时提 issue，我们按需补编。")
    lines.append("")

    for arch in sorted(by_arch, key=arch_key):
        rows = by_arch[arch]
        # Stable sorts: kernel newest-first, then SDK group (25.12 before 24.10).
        rows.sort(key=lambda r: kernel_key(r[1]), reverse=True)
        rows.sort(key=lambda r: 0 if r[0] == "25.12" else 1)
        lines.append(f"## {arch}")
        lines.append("")
        lines.append("| 固件 | 内核版本 | 包 |")
        lines.append("|---|---|---|")
        for sdk, kernel, name in rows:
            url = f"https://github.com/{args.repo}/releases/download/latest/{name}"
            lines.append(f"| {sdk} | {kernel} | [{name}]({url}) |")
        lines.append("")

    lines.append("## 校验")
    lines.append("")
    lines.append("```sh")
    lines.append("sha256sum -c SHA256SUMS --ignore-missing")
    lines.append("```")
    lines.append("")

    with open(args.output, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {args.output}: {sum(len(v) for v in by_arch.values())} packages, "
          f"{len(by_arch)} architectures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
