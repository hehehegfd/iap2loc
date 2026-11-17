# Mac 有线定位测试

在 Mac 上用 USB 数据线连接自己的 iPhone，设置一个固定的开发测试位置。这个工具通过 [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) 使用 iOS 开发者定位模拟功能，可独立于 iap2loc 的蓝牙会话运行。

## 准备

1. 使用 Mac、iOS 17.4 或更新版本及支持数据传输的 USB 线。先解锁 iPhone，在 Finder 完成「信任」，并确认侧栏能看到设备。一次只接入一台要测试的 iPhone。[Apple USB 排查](https://support.apple.com/zh-cn/108643)
2. 在 iPhone 的「设置 → 隐私与安全性 → 开发者模式」中开启开发者模式，按提示重启并确认。没有这个选项时，先用与 iOS 版本匹配的 Xcode 连接真机。[Apple 开发者模式说明](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device)
3. 在 Mac 上安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)。首次运行时，uv 会按脚本声明安装 Python 依赖。

## 使用

在仓库根目录打开终端。下面的坐标只是示例，按「纬度、经度」顺序替换为需要测试的十进制度坐标。

```sh
uv run tools/macos-usb-location/iphone_usb_location.py list
uv run tools/macos-usb-location/iphone_usb_location.py set 31.2304 121.4737
```

测试期间保持数据线和终端会话。按 **Ctrl+C** 停止，脚本会尝试清除模拟位置。若中途拔线或位置未恢复，重新连线并运行：

```sh
uv run tools/macos-usb-location/iphone_usb_location.py clear
```

`list` 仅确认 USB 设备可见。若能列出设备但 `set` 失败，请先检查 Finder 信任及开发者模式。脚本已通过参数检查和离线模拟测试；目标 App 是否采用测试坐标，以及停止后定位是否恢复，需要在具体 iPhone 上验证。
