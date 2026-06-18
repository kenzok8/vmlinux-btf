<div align="center">

# 🧬 vmlinux-btf

**为没开 BTF 的 OpenWrt 固件补上内核 BTF，让 dae / daed 正常启动**

[![Build](https://github.com/kenzok8/vmlinux-btf/actions/workflows/build.yml/badge.svg)](https://github.com/kenzok8/vmlinux-btf/actions/workflows/build.yml)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
![Kernel](https://img.shields.io/badge/kernel-6.6%20%7C%206.12-orange.svg)

**简体中文 | [English](README_EN.md)**

</div>

---

## 🤔 为什么需要它

dae / daed 用 **CO-RE eBPF**，加载时需要当前内核的 BTF 信息。

| 内核情况 | `/sys/kernel/btf/vmlinux` | daed 能否启动 |
|---------|:--:|:--:|
| 开了 `CONFIG_DEBUG_INFO_BTF`（ImmortalWrt 25.12 等） | ✅ 有 | ✅ 正常 |
| 没开（官方 OpenWrt、在线 ImageBuilder 固件） | ❌ 无 | ❌ **起不来** |

很多固件默认**不开** BTF，daed 就会启动失败。装上本包即可补齐。

## ⚙️ 工作原理

```
OpenWrt 内核源码 + .config
        │  开启 DEBUG_INFO_BTF，编译影子内核
        ▼
   shadow vmlinux  ──pahole──▶  detached vmlinux.btf
        │  打包安装
        ▼
/usr/lib/debug/boot/vmlinux-<内核版本>
        │
        ▼
cilium/ebpf 在 /sys/kernel/btf/vmlinux 缺失时
自动 fallback 到这里读取 → daed 启动成功 ✓
```

> 包版本跟随内核版本（`PKG_VERSION = LINUX_VERSION`）。BTF 在同一内核 minor 系列内兼容，所以一个 `6.6.x` 的包可用于其它 `6.6.y` 固件。

## 📦 支持矩阵

| 内核 | 对应 SDK | 包管理 | 典型固件 |
|:--:|:--:|:--:|:--|
| `6.6.x` | ImmortalWrt 24.10 | IPK | 官方 OpenWrt 24.10、各类 24.10 衍生固件 |
| `6.12.x` | ImmortalWrt 25.12 | APK | 不带 BTF 的 25.12 衍生固件 |

> ImmortalWrt 自家固件通常已内置 BTF，无需本包。

## 🚀 安装

```sh
# 1. 确认固件确实缺 BTF
[ -e /sys/kernel/btf/vmlinux ] && echo "已有 BTF，无需安装" || echo "缺 BTF，需安装"

# 2. 查内核版本与架构，下载匹配的包后安装
uname -r            # 例如 6.6.141  → 选 6.6.x 的包
opkg install ./vmlinux-btf_*.ipk     # 或 apk add ./vmlinux-btf-*.apk

# 3. 重启 daed
/etc/init.d/daed restart
```

## 🔨 自行构建

```sh
gh workflow run build.yml
```

一次构建全部 9 架构 × {24.10 IPK, 25.12 APK}，完成后自动发布到 [Releases](../../releases/tag/latest)。

## 🙏 致谢

包构建方案改编自 [sbwml](https://github.com/sbwml/package_kernel_vmlinux-btf) / [QiuSimons](https://github.com/QiuSimons/vmlinux-btf) 的 `vmlinux-btf`。

---

<div align="center">
<sub>为 <a href="https://github.com/kenzok8/openwrt-daede">openwrt-daede</a> 等 eBPF 依赖提供 BTF 支持</sub>
</div>
