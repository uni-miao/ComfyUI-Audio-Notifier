# ComfyUI-Audio-Notifier

一个用于 ComfyUI 的音频提醒节点集合。到达节点时播放提示音，支持 output node、trigger node 和 passthrough 节点。

> [!IMPORTANT]
> 声音在运行 ComfyUI **后端进程** 的机器上播放，而不是浏览器所在机器。

## v0.2.1 后端增强功能

- 保留 Output 节点：**Audio Notify**
- 新增 Trigger 节点（无输出，仅建立执行依赖）
- 新增 Video passthrough：`VIDEO -> VIDEO`
- 新增 `sound_path` / `sound_name` 启用开关
- 无第三方 Python 依赖

## 安装

1. 克隆到 `ComfyUI/custom_nodes`。
2. 重启 ComfyUI。
3. 在节点搜索中输入 `Audio Notify`。

## 节点说明

所有节点均在分类：`utils/audio`

### 1) Output Node

- **Audio Notify**（输出节点）
- 用法：放在流程末尾，仅用于触发通知，不返回数据

### 2) Trigger Nodes（无输出）

这些节点有输入但没有输出，只用于建立执行依赖并播放声音：

- **Audio Notify Image Trigger**: 输入 `IMAGE`，无输出
- **Audio Notify Latent Trigger**: 输入 `LATENT`，无输出
- **Audio Notify Audio Trigger**: 输入 `AUDIO`，无输出
- **Audio Notify Video Trigger**: 输入 `VIDEO`，无输出
- **Audio Notify Text Trigger**: 输入 `STRING`（`forceInput=True`），无输出

示例：
- `VAE Decode` 的 `IMAGE` 同时连接到 `Save Image` 和 `Audio Notify Image Trigger`

### 3) Passthrough Nodes

这些节点会播放声音后原样输出输入值：

- **Audio Notify Image**: `IMAGE -> IMAGE`
- **Audio Notify Latent**: `LATENT -> LATENT`
- **Audio Notify Model**: `MODEL -> MODEL`
- **Audio Notify Clip**: `CLIP -> CLIP`
- **Audio Notify VAE**: `VAE -> VAE`
- **Audio Notify Audio**: `AUDIO -> AUDIO`
- **Audio Notify Video**: `VIDEO -> VIDEO`
- **Audio Notify Text**: `STRING -> STRING`（输入使用 `forceInput=True`）

示例：
- `KSampler -> Audio Notify Latent -> VAE Decode`

## 参数

所有节点统一参数：

- `repeat`: 播放次数
- `delay_seconds`: 首次播放前延迟秒数
- `notification_enabled`: 总开关，`False` 时不播放，仅打印日志
- `enable_sound_path`: 是否启用 `sound_path`
- `sound_path`: 自定义文件路径（后端机器上的路径）
- `enable_sound_name`: 是否启用 `sound_name`
- `sound_name`: 从仓库 `sounds/` 目录中选择文件名
- `fallback_to_system_beep`: 未选中可用音频时是否回退系统提示音

## 声音选择优先级

1. 若 `notification_enabled=False`：不播放，只打印日志
2. 若 `enable_sound_path=True` 且 `sound_path` 有效：播放 `sound_path`
3. 否则若 `enable_sound_name=True` 且 `sound_name` 有效：播放 `sounds/sound_name`
4. 否则若 `fallback_to_system_beep=True`：播放系统提示音（最终失败时回退终端 bell）
5. 否则：不播放，只打印日志

## sounds/ 目录用法

- 把音频文件放到本仓库 `sounds/` 目录。
- 重启 ComfyUI 后，可在 `sound_name` 下拉中选择文件。

## 类型限制说明

Passthrough 节点是强类型直通，只接受并返回对应类型，不能跨类型连接。

## 平台兼容与音频格式

- **Windows**:
  - `.wav` 优先走 `winsound.PlaySound`（最稳定）
  - 非 `.wav` 优先尝试 `ffplay -nodisp -autoexit <file>`
  - 若 `ffplay` 不可用，回退 `os.startfile(<file>)`（系统默认播放器）
- **macOS**: 使用 `afplay`，支持常见音频格式
- **Linux**: 优先 `ffplay`，其次 `paplay` / `aplay`，最后终端 bell

> mp3/m4a 等格式在 Windows 上依赖 `ffplay` 或系统默认播放器；`wav` 最稳定。

## 备注

- 节点实现了 `IS_CHANGED` 以确保每次 Queue Prompt 都会执行。
- Docker/WSL/无头环境可能需要额外主机音频配置。
