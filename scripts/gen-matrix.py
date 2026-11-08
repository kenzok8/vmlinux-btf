#!/usr/bin/env python3
"""Print the (sdk, arch) build matrix as `matrix={json}` for $GITHUB_OUTPUT.

24.10 的点版本内核与分支 HEAD 不一致（例如 24.10.8 是 6.6.144，分支已到 6.6.159），
所以按需只编某一份，避免每次都排 18 个组合。
"""
import json
import os
import sys

ARCHES = [
    "aarch64_cortex-a53",
    "aarch64_cortex-a72",
    "aarch64_generic",
    "arm_cortex-a7_neon-vfpv4",
    "arm_cortex-a9_neon",
    "i386_pentium4",
    "mips_24kc",
    "mipsel_24kc",
    "x86_64",
]
SDKS = ["24.10", "25.12"]


def main() -> int:
    want_sdk = os.environ.get("WANT_SDK", "").strip()
    want_arch = os.environ.get("WANT_ARCH", "").strip()
    if want_sdk and want_sdk not in SDKS:
        print(f"unknown sdk: {want_sdk}", file=sys.stderr)
        return 2
    if want_arch and want_arch not in ARCHES:
        print(f"unknown arch: {want_arch}", file=sys.stderr)
        return 2
    include = [
        {"sdk": sdk, "arch": arch}
        for sdk in SDKS
        if not want_sdk or sdk == want_sdk
        for arch in ARCHES
        if not want_arch or arch == want_arch
    ]
    print("matrix=" + json.dumps({"include": include}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
