# ComfyUI-Audio-Notifier

[English](README.md) | 中文

这是一个用于 ComfyUI 的后端音频提醒节点集合。当流程执行到指定节点时，会在后端机器上播放提示音。

> [!IMPORTANT]
> 声音播放发生在 ComfyUI 后端进程所在机器，不是在浏览器所在机器。

## 概览

ComfyUI-Audio-Notifier 提供输出节点、触发节点和直通节点，适合长流程中的阶段提醒和结束提醒。

## 功能特性

- 基础输出节点：**Audio Notify**
- 通用触发节点：**Audio Notify Trigger**（任意输入、无输出）
- 通用直通节点：**Audio Notify Passthrough**（任意输入，原样输出）
- 保留具体类型兼容节点（IMAGE/LATENT/MODEL/CLIP/VAE/AUDIO/VIDEO/STRING）
- 支持绝对路径音频和仓库 `sounds/` 目录音频
- 支持后台线程非阻塞播放
- 无第三方 Python 依赖

## 安装

1. 将本仓库克隆到 `ComfyUI/custom_nodes`。
2. 重启 ComfyUI。
3. 在菜单中添加节点：**Add Node → Audio Notifier → ...**

## 使用说明

### 基础 Audio Notify

把 **Audio Notify** 放在流程末端作为输出节点，用于最简单的完成提醒。

### Trigger 节点

当你只需要建立依赖关系并播放提示音、但不需要传出数据时，使用 **Audio Notify Trigger**。

- 输入名：`input`（通用任意类型）
- 输出：无（`RETURN_TYPES = ()`）
- `OUTPUT_NODE = True`

### Passthrough 节点

当你希望插在两个节点中间，同时不改变数据流时，使用 **Audio Notify Passthrough**。

- 输入名：`input`（通用任意类型）
- 输出：原始输入值（类型随输入）

### sounds/ 目录

把音频文件放到仓库 `sounds/` 目录，重启 ComfyUI 后即可在 `sound_name` 下拉中选择。

## 播放参数

所有节点共享以下参数：

- `repeat`
- `delay_seconds`
- `notification_enabled`
- `blocking_playback`（默认 `False`）
- `enable_sound_path`
- `sound_path`
- `enable_sound_name`
- `sound_name`
- `fallback_to_system_beep`

`blocking_playback` 行为：

- `False`：使用后台守护线程播放，节点立即返回，不阻塞后续执行
- `True`：同步播放，播放结束后再返回

当 `notification_enabled = False` 时，不会启动线程，也不会播放。

## Trigger 时序说明（重点）

Trigger 节点会在“其输入数据准备完成后”触发。

如果 **Audio Notify ... Trigger** 与 **Save Image** 并联在同一个 `IMAGE` 上，二者之间没有直接依赖关系，ComfyUI 调度顺序不保证 `Save Image` 一定先执行，因此可能出现“先响铃，后保存”。

如果你需要严格的“整个工作流完成后再提醒”，建议未来采用前端全局完成监听方案。

## 通用节点与具体类型节点的区别

当前版本已提供通用节点，同时保留具体类型节点作为兼容 fallback：

- 通用节点：菜单更简洁，连线更灵活
- 具体类型节点：当某些工作流/插件强依赖显式类型时更稳妥

## Windows/macOS/Linux 音频格式支持

- **Windows**
  - `.wav`：优先 `winsound.PlaySound`（最稳定）
  - 非 `.wav`：优先 `ffplay -nodisp -autoexit`
  - 回退：`os.startfile` 调系统默认播放器
- **macOS**
  - 使用 `afplay`
- **Linux**
  - 优先 `ffplay`，其次 `paplay` / `aplay`
  - 最后回退终端 bell

## 故障排查

- Docker/WSL/无头环境无声：通常需要主机音频转发配置。
- `sound_path` 无效：确认是后端机器路径且文件可读。
- Windows 非 WAV 无法播放：安装 `ffplay` 或改用 WAV。
- 每次 Queue 都执行：节点实现了 `IS_CHANGED` 强制触发。
