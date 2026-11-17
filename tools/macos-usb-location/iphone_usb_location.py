# /// script
# requires-python = ">=3.11"
# dependencies = ["pymobiledevice3==11.57.1"]
# ///
"""Mac 上为一台已经信任本机的 USB iPhone 设置开发测试位置。"""

import argparse
import asyncio
import contextlib
import re
import sys


async def run(args: argparse.Namespace) -> int:
    from pymobiledevice3.usbmux import select_devices_by_connection_type

    devices = await select_devices_by_connection_type("USB")
    if args.action == "list":
        print(f"检测到 {len(devices)} 台 USB iOS 设备。")
        if not devices:
            print("请用数据线直连、解锁 iPhone，并确认 Finder 能看到它。")
        return 0 if devices else 1
    if len(devices) != 1:
        raise RuntimeError(f"检测到 {len(devices)} 台 USB iOS 设备；请只连接要测试的一台 iPhone。")

    from pymobiledevice3.lockdown import create_using_usbmux
    from pymobiledevice3.remote.tunnel_service import CoreDeviceTunnelProxy
    from pymobiledevice3.remote.userspace_tunnel import TunnelProvider, UserspaceRsdTunnel
    from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
    from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation

    async def open_usb_provider():
        lockdown = await create_using_usbmux(
            serial=devices[0].serial, connection_type="USB", autopair=False
        )
        try:
            if not lockdown.paired:
                raise RuntimeError("iPhone 尚未信任本机。请解锁手机，在 Finder 完成信任。")
            if not lockdown.product_type.startswith("iPhone"):
                raise RuntimeError("当前 USB 设备不是 iPhone。")
            version = re.match(r"(\d+)\.(\d+)", lockdown.product_version)
            if version and tuple(map(int, version.groups())) < (17, 4):
                raise RuntimeError("这个 USB 工具需要 iOS 17.4 或更新版本；旧版可用匹配的 Xcode 测试。")
            return TunnelProvider(await CoreDeviceTunnelProxy.create(lockdown), lockdown)
        except BaseException:
            with contextlib.suppress(Exception):
                await lockdown.close()
            raise

    tunnel = UserspaceRsdTunnel(provider_factory=open_usb_provider)
    async with tunnel as rsd, DvtProvider(rsd) as dvt, LocationSimulation(dvt) as simulation:
        if args.action == "clear":
            await asyncio.wait_for(simulation.clear(), timeout=8)
            print("已发送清除指令，请在 iPhone 上确认。")
            return 0

        await simulation.set(args.latitude, args.longitude)
        print("已发送固定点。请在目标 App 验证；保持数据线连接，按 Ctrl+C 停止并清除。", flush=True)
        try:
            while tunnel.rsd is not None:
                await asyncio.sleep(0.5)
            raise RuntimeError("USB 会话已中断；如果模拟位置仍在，重新连线运行 clear。")
        finally:
            if tunnel.rsd is not None:
                try:
                    await asyncio.wait_for(simulation.clear(), timeout=8)
                    print("已发送清除指令，请在 iPhone 上确认。")
                except Exception as exc:
                    print(f"未能清除模拟位置（{type(exc).__name__}）；连线后运行 clear。", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("list", help="检查是否有通过 USB 连接的 iOS 设备")
    set_cmd = commands.add_parser("set", help="设置固定测试点，直到按 Ctrl+C")
    set_cmd.add_argument("latitude", type=float, help="纬度，十进制度")
    set_cmd.add_argument("longitude", type=float, help="经度，十进制度")
    commands.add_parser("clear", help="向 iPhone 发送清除模拟定位的命令")
    args = parser.parse_args()
    if args.action == "set" and not (-90 <= args.latitude <= 90 and -180 <= args.longitude <= 180):
        parser.error("纬度须为 [-90, 90]、经度须为 [-180, 180] 内的有限数值。")
    if sys.platform != "darwin":
        parser.error("请在连接 iPhone 的 Mac 上运行。")
    try:
        return asyncio.run(run(args))
    except KeyboardInterrupt:
        return 130
    except ModuleNotFoundError as exc:
        print(f"缺少依赖（{exc.name}）。请用 uv run 执行脚本。", file=sys.stderr)
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        print("请检查 USB 数据线、Finder 信任和 iPhone 开发者模式。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
