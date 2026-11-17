# Mac 有线定位测试

在 Mac 上用 USB 数据线连接自己的 iPhone，设置一个固定的开发测试位置。这个工具通过 [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) 使用 iOS 开发者定位模拟功能，可独立于 iap2loc 的蓝牙会话运行。

`set` 通过 USB 只向开发者定位服务发送经纬度。要同时指定高度、水平精度和垂直精度，用下方的 `fixture` 给自己的 App 生成测试样本。

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

## 生成固定定位测试样本

在自己的 App 中测试定位逻辑时，可以指定全部字段。`fixture` 只生成 Swift 源码，在 Mac 或 Windows 上使用 Python 3.11 及更新版本即可，无需连接 iPhone 或安装 `pymobiledevice3`。

```sh
python3 tools/macos-usb-location/iphone_usb_location.py fixture 31.2304 121.4737 \
  --altitude 20 --horizontal-accuracy 5 --vertical-accuracy 8 \
  --output FixedLocationFixture.swift
```

前两个值依次是纬度、经度，单位是十进制度。`--altitude` 是相对于海平面的高度（米），可为负数。`--horizontal-accuracy` 是坐标的不确定性半径，`--vertical-accuracy` 是高度的精度，两项单位均为米，需大于或等于 0。省略 `--output` 时输出到终端；指定了文件名时不会覆盖已有文件。

在 Xcode 中把生成的 `FixedLocationFixture.swift` 加到自己的测试 Target。调用 `FixedLocationFixture.make()` 取得 [`CLLocation`](https://developer.apple.com/documentation/corelocation/cllocation/init(coordinate:altitude:horizontalaccuracy:verticalaccuracy:timestamp:))，把它传给 App 中处理定位的函数。需要固定时间时可调用 `make(at:)`。

这个样本用于 App 内测试，不会修改 iPhone 的系统定位或定位来源。
