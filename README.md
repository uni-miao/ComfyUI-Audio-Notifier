# ComfyUI-Audio-Notifier

一个用于 ComfyUI 的音频提醒节点集合。到达节点时播放提示音，支持 output node 和多个 passthrough 节点。

> [!IMPORTANT]
> 声音在运行 ComfyUI **后端进程** 的机器上播放，而不是浏览器所在机器。

## v0.2 后端增强功能

- 保留 Output 节点：**Audio Notify**
- 新增 Passthrough 节点（可插入工作流中间）
- 新增 `sounds/` 目录下拉选择（`sound_name`）
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

### 2) Passthrough Nodes

这些节点会播放声音后原样输出输入值：

- **Audio Notify Image**: `IMAGE -> IMAGE`
- **Audio Notify Latent**: `LATENT -> LATENT`
- **Audio Notify Model**: `MODEL -> MODEL`
- **Audio Notify Clip**: `CLIP -> CLIP`
- **Audio Notify VAE**: `VAE -> VAE`
- **Audio Notify Audio**: `AUDIO -> AUDIO`
- **Audio Notify Text**: `STRING -> STRING`（输入使用 `forceInput=True`）

## 参数

所有节点统一参数：

- `repeat`: 播放次数
- `delay_seconds`: 首次播放前延迟秒数
- `sound_path`: 自定义文件路径（后端机器上的路径）
- `sound_name`: 从仓库 `sounds/` 目录中选择文件名

## 声音选择优先级

1. 若 `sound_path` 非空且文件存在：播放 `sound_path`
2. 否则若 `sound_name` 对应 `sounds/` 中文件：播放该文件
3. 否则：播放系统提示音（最终失败时回退终端 bell）

## sounds/ 目录用法

- 把音频文件放到本仓库 `sounds/` 目录。
- 重启 ComfyUI 后，可在 `sound_name` 下拉中选择文件。
- `sound_path` 与 `sound_name` 同时设置时，`sound_path` 优先。

## 类型限制说明

Passthrough 节点是强类型直通，只接受并返回对应类型，不能跨类型连接。

## 工作流示例

- `KSampler -> Audio Notify Latent -> VAE Decode`
- `VAE Decode -> Audio Notify Image -> Save Image`

## 平台兼容

- **Windows**: 优先 `winsound`，并继续优先支持 `wav` 文件播放。
- **macOS**: 使用 `afplay`。
- **Linux**: 依次尝试 `paplay` / `aplay` / `ffplay`。

## 备注

- 节点实现了 `IS_CHANGED` 以确保每次 Queue Prompt 都会执行。
- Docker/WSL/无头环境可能需要额外主机音频配置。
