<div align="center">

# 🧬 vmlinux-btf

**Supply kernel BTF to OpenWrt firmware built without it, so dae / daed start.**

[![Build](https://github.com/kenzok8/vmlinux-btf/actions/workflows/build.yml/badge.svg)](https://github.com/kenzok8/vmlinux-btf/actions/workflows/build.yml)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
![Kernel](https://img.shields.io/badge/kernel-6.6%20%7C%206.12-orange.svg)

**[简体中文](README.md) | English**

</div>

---

## 🤔 Why

dae / daed load **CO-RE eBPF** programs that need the running kernel's BTF.

| Kernel | `/sys/kernel/btf/vmlinux` | daed starts |
|--------|:--:|:--:|
| `CONFIG_DEBUG_INFO_BTF` enabled (ImmortalWrt 25.12, …) | ✅ present | ✅ yes |
| Not enabled (stock OpenWrt, online ImageBuilder images) | ❌ absent | ❌ **fails** |

Many firmwares ship **without** BTF, so daed won't start. Installing this package fixes that.

## ⚙️ How it works

```
OpenWrt kernel source + .config
        │  enable DEBUG_INFO_BTF, build a shadow kernel
        ▼
   shadow vmlinux  ──pahole──▶  detached vmlinux.btf
        │  package & install
        ▼
/usr/lib/debug/boot/vmlinux-<release>
        │
        ▼
cilium/ebpf falls back here when
/sys/kernel/btf/vmlinux is absent → daed starts ✓
```

> The package version tracks the kernel version (`PKG_VERSION = LINUX_VERSION`).
> BTF is compatible within a kernel minor series, so a `6.6.x` package works on
> other `6.6.y` firmware.

## 📦 Support matrix

| Kernel | SDK | Pkg fmt | Typical firmware |
|:--:|:--:|:--:|:--|
| `6.6.x` | ImmortalWrt 24.10 | IPK | Stock OpenWrt 24.10 and 24.10-based images |
| `6.12.x` | ImmortalWrt 25.12 | APK | 25.12-based images that lack BTF |

> ImmortalWrt's own images usually ship BTF in-kernel and don't need this package.

## 🚀 Install

```sh
# 1. Confirm the firmware really lacks BTF
[ -e /sys/kernel/btf/vmlinux ] && echo "BTF present, skip" || echo "BTF missing, install"

# 2. Check kernel version + arch, download the matching package, install
uname -r            # e.g. 6.6.141  → pick the 6.6.x package
opkg install ./vmlinux-btf_*.ipk     # or: apk add ./vmlinux-btf-*.apk

# 3. Restart daed
/etc/init.d/daed restart
```

## 🔨 Build it yourself

```sh
gh workflow run build.yml -f arch=x86_64 -f sdk=24.10
```

`arch` is the target architecture (`x86_64` / `aarch64_cortex-a53` …); `sdk` is
`24.10` (kernel 6.6) or `25.12` (kernel 6.12).

## 🙏 Credit

Recipe adapted from [sbwml](https://github.com/sbwml/package_kernel_vmlinux-btf) / [QiuSimons](https://github.com/QiuSimons/vmlinux-btf) `vmlinux-btf`.

---

<div align="center">
<sub>BTF support for <a href="https://github.com/kenzok8/openwrt-daede">openwrt-daede</a> and other eBPF dependencies</sub>
</div>
