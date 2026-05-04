# ComfyUI-Audio-Notifier

[English](README.md) | 中文

一个轻量的 ComfyUI 自定义节点包，用于在工作流不同阶段播放音频提示。

<img width="600" alt="Add Nodes" src="https://github.com/user-attachments/assets/15a69a83-29f2-4f47-98f2-45fb24b2f48e" />

> [!IMPORTANT]
> 这是**后端节点**。声音会在运行 ComfyUI 后端进程的机器上播放，不一定是你当前浏览器所在的机器。

## 概览

ComfyUI-Audio-Notifier 适用于本地长流程，让你在关键阶段通过声音获知进度。

适用场景：
- 长时间出图与采样等待。
- 图像 / 视频 / 音频处理流程。
- 本地工作流运行时，人不一直盯着屏幕。

它可以：
- 在流程执行到通知节点时播放声音。
- 提供输出式通知、触发式通知、直通式通知节点。

它不做的事：
- 不是浏览器通知插件。
- Trigger 节点不是“全局工作流完成监听器”。

## 功能特性

以下均基于当前代码实际能力：

- 基础通知节点：**Audio Notify**。
- 通用 Trigger 节点：**Audio Notify Trigger**（`*` 输入、无输出）。
- 通用 Passthrough 节点：**Audio Notify Passthrough**（`*` 输入、原样输出）。
- 保留类型化 Passthrough：IMAGE / LATENT / MODEL / CLIP / VAE / AUDIO / VIDEO / STRING。
- 保留类型化 Trigger：IMAGE / LATENT / AUDIO / VIDEO / STRING。
- 支持自定义绝对路径 `sound_path`。
- 支持从本仓库 `sounds/` 目录选择 `sound_name`（启动时扫描）。
- 播放参数支持：`repeat`、`delay_seconds`、`blocking_playback`。
- 开关参数支持：`notification_enabled`、`enable_sound_path`、`enable_sound_name`、`fallback_to_system_beep`。
- Windows/macOS/Linux 跨平台播放回退逻辑。
- 不依赖第三方 Python 包。

## 安装

### A) 推荐：Git 克隆

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/uni-miao/ComfyUI-Audio-Notifier.git
```

然后重启 ComfyUI 后端。

### B) ZIP 手动安装

1. 打开仓库 GitHub 页面。
2. 点击 **Code → Download ZIP**。
3. 解压 ZIP。
4. 将解压后的文件夹放入 `ComfyUI/custom_nodes`。
5. 确认最终结构类似：

```text
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/__init__.py
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/audio_notifier.py
```

6. 重启 ComfyUI 后端。

### C) ComfyUI Portable / Windows 启动器说明

给 Windows 用户（含秋叶整合包 / 绘世启动器）：

- 先找到启动器**实际使用**的 ComfyUI 目录。
- 把仓库放到该目录下的 `ComfyUI/custom_nodes`。
- 重启的是**后端进程**（停止后再启动），不是只刷新浏览器页面。

### `requirements.txt` 说明

- 当前无需安装任何第三方 Python 依赖。
- 未来若通过 ComfyUI Manager 安装，依赖会从 `requirements.txt` 读取。

## 如何添加节点

当前代码中的节点分类为：

- **Add Node → Audio Notifier → Audio Notify**

也可以右键搜索：

- `Audio Notify`

<img width="300" alt="Add Nodes" src="https://github.com/user-attachments/assets/15a69a83-29f2-4f47-98f2-45fb24b2f48e" />

## 使用说明

### 5.1 Basic Audio Notify（基础通知）

**Audio Notify** 适合快速测试，或作为独立输出式提醒节点。

时序注意：
- 如果它没有上游依赖，可能在 prompt 开始时就较早执行，这不代表整个工作流已经完成。

### 5.2 Trigger Nodes（触发节点）

Trigger 节点有输入、无输出。
适用于“某数据准备好时播放声音”，但不需要继续传递该数据。

示例：

```text
VAE Decode (IMAGE)
├── Save Image
└── Audio Notify Image Trigger
```

重要说明：
- 当 Trigger 与 Save Image 并联时，ComfyUI 不保证 Save Image 一定先执行。
- Trigger 表示“输入数据就绪后触发”，不等价于“所有保存动作完成后触发”。

### 5.3 Passthrough Nodes（直通节点）

Passthrough 节点有输入也有输出，输出值与输入值相同。
可插在两个节点中间，不改变数据本身。

示例：

```text
KSampler -> Audio Notify Latent -> VAE Decode
```

含义：KSampler 输出 latent 后先播放提示音，再把 latent 继续传给 VAE Decode。

### 5.4 `sounds/` 目录

如果使用仓库内音频：

1. 将音频文件放到 `ComfyUI-Audio-Notifier/sounds/`。
2. 重启 ComfyUI 后端。
3. 在 `sound_name` 下拉框里选择。

当前代码不会按固定扩展名白名单过滤，而是列出 `sounds/` 下检测到的文件。

### 5.5 自定义 `sound_path`

也支持填写后端机器上的本地绝对路径。

Windows 示例：

```text
C:\Windows\Media\Windows Notify System Generic.wav
```

请注意路径解析发生在 ComfyUI 后端机器，而不是浏览器客户端。

## Playback 参数说明

共享参数：

- `notification_enabled`：总开关；为 `False` 时直接跳过播放。
- `repeat`：重复播放次数（`>=1`）。
- `delay_seconds`：播放前延迟秒数。
- `blocking_playback`：
  - `False`（默认）：后台守护线程异步播放，不阻塞流程。
  - `True`：同步播放，播放完才返回。
- `enable_sound_path`：是否启用 `sound_path`。
- `sound_path`：自定义音频文件路径。
- `enable_sound_name`：是否启用 `sound_name`。
- `sound_name`：从 `sounds/` 选择的文件名。
- `fallback_to_system_beep`：无可用文件时，是否允许系统提示音/终端 bell 回退。

当前代码中的优先级：
1. 若 `enable_sound_path=True` 且 `sound_path` 指向有效文件，优先使用 `sound_path`。
2. 否则若 `enable_sound_name=True` 且 `sound_name` 在 `sounds/` 中存在，使用 `sound_name`。
3. 否则没有可播放文件；若 `fallback_to_system_beep=True` 则尝试系统回退，否则跳过并打印日志。

## 音频格式支持说明

按当前实现：

- **Windows**
  - `.wav`：`winsound.PlaySound`，通常最稳定。
  - 非 `.wav`：先尝试 `ffplay`，再尝试 `os.startfile` 调系统默认播放器。
- **macOS**
  - 使用 `afplay`。
- **Linux**
  - 依次尝试 `ffplay`、`paplay`、`aplay`。

若都不可用，最终回退为系统提示音或终端 bell（取决于平台和设置）。

## 时序与限制

- 后端节点在 ComfyUI 调度到该节点时执行。
- Trigger 节点不是全局完成监听器。
- 并行分支执行顺序可能与直觉不同。
- 若要“严格在整个 prompt/queue 完成后播放”，需要未来扩展前端/全局监听机制。
- 声音始终在后端机器上播放。

## 故障排查

### 看不到节点

- 检查 `ComfyUI/custom_nodes` 下目录结构是否正确。
- 重启 ComfyUI 后端。
- 查看后端控制台是否有导入报错。

### 没有声音

- 检查后端机器系统音量与输出设备。
- Windows 建议先用 `.wav` 测试。
- Windows 可先试：
  - `C:\Windows\Media\Windows Notify System Generic.wav`

### mp3/m4a 播放失败

- 先用 `.wav` 验证链路。
- 若你的环境依赖 `ffplay`，请安装 FFmpeg/ffplay。

### 声音播放太早

- 检查节点依赖关系是否正确。
- Trigger 只表示输入就绪，不表示全流程结束。

### ZIP 安装后出现多层嵌套目录

请修正为：

```text
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/__init__.py
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/audio_notifier.py
```

## 开发说明

简要文件结构：

- `__init__.py`：ComfyUI 节点导出。
- `audio_notifier.py`：节点定义与播放逻辑。
- `README.md` / `README.zh-CN.md`：项目文档。
- `requirements.txt`：依赖占位文件。

语法检查：

```bash
python -m py_compile __init__.py audio_notifier.py
```

如果仓库包含测试，可按需运行测试。

## License

MIT
