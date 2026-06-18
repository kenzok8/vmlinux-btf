# vmlinux-btf

Detached kernel BTF packages for CO-RE eBPF (dae / daed) on OpenWrt firmware
whose kernel was built **without** `CONFIG_DEBUG_INFO_BTF`.

## Why

dae/daed load CO-RE eBPF programs that need the running kernel's BTF. Kernels
with `CONFIG_DEBUG_INFO_BTF` expose it at `/sys/kernel/btf/vmlinux`. Many stock
OpenWrt builds (and the official online ImageBuilder) ship without it, so daed
fails to start. This package builds a shadow kernel from the same OpenWrt
source + `.config` with BTF enabled, encodes a detached `vmlinux.btf` via
`pahole`, and installs it to `/usr/lib/debug/boot/vmlinux-<release>` — a path
cilium/ebpf searches when `/sys/kernel/btf/vmlinux` is absent.

The package version tracks the kernel version (`PKG_VERSION = LINUX_VERSION`).
BTF is compatible within a kernel minor series, so a `6.6.x` package works on
other `6.6.y` firmware.

## Build

`gh workflow run build.yml -f arch=x86_64 -f sdk=24.10` (kernel 6.6 = SDK
24.10, kernel 6.12 = SDK 25.12).

## Credit

Package recipe adapted from sbwml / QiuSimons `vmlinux-btf`.
