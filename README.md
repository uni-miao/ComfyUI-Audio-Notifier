# ComfyUI-Audio-Notifier

English | [中文说明点这里](README.zh-CN.md)

A lightweight ComfyUI custom node pack that plays audio notifications at different stages of a workflow.

<img width="600" alt="ComfyUI-Audio-Notifier preview" src="https://github.com/user-attachments/assets/196649cb-ef08-407a-a3f0-c8b66b9ca650" />

> [!IMPORTANT]
> This is a **backend node pack**. Audio is played on the machine running the ComfyUI backend process, not necessarily on your browser/client machine.

## Overview

ComfyUI-Audio-Notifier helps you hear workflow progress in long-running local ComfyUI jobs.

Typical use cases:
- Long image generation and sampling waits.
- Image/video/audio processing chains.
- Local workflows where you may step away from the screen.

What it does:
- Plays a sound when execution reaches a notify node.
- Provides output-style notify, trigger-style notify, and passthrough-style notify nodes.

What it does **not** do:
- It is **not** a browser notification extension.
- Trigger nodes are **not** global “workflow fully completed” listeners.

## Features

Based on the current code implementation:

- Basic audio notify node: **Audio Notify**.
- Generic trigger node: **Audio Notify Trigger** (`*` input, no output).
- Generic passthrough node: **Audio Notify Passthrough** (`*` input, same output).
- Typed passthrough nodes: IMAGE / LATENT / MODEL / CLIP / VAE / AUDIO / VIDEO / STRING.
- Typed trigger nodes: IMAGE / LATENT / AUDIO / VIDEO / STRING.
- Custom absolute `sound_path` support.
- Local `sounds/` folder selection via `sound_name` dropdown (scan on startup).
- Playback controls: `repeat`, `delay_seconds`, `blocking_playback`.
- Enable/disable switches: `notification_enabled`, `enable_sound_path`, `enable_sound_name`, `fallback_to_system_beep`.
- Cross-platform fallback strategy for Windows/macOS/Linux.
- No third-party Python dependency required.

## Installation

### A) Recommended: Git clone

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/uni-miao/ComfyUI-Audio-Notifier.git
```

Then restart ComfyUI backend.

### B) Manual ZIP installation

1. Open this repository page on GitHub.
2. Click **Code → Download ZIP**.
3. Extract the ZIP.
4. Put the extracted folder into `ComfyUI/custom_nodes`.
5. Make sure the final structure is:

```text
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/__init__.py
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/audio_notifier.py
```

6. Restart ComfyUI backend.

### C) ComfyUI portable / Windows launcher notes

For Windows launcher users (including packages like 秋叶整合包 / 绘世启动器):

- Find the **actual ComfyUI directory used by your launcher**.
- Install this repo under that directory’s `ComfyUI/custom_nodes`.
- Restart the **backend process** (stop/start launcher), not only the browser tab.

### `requirements.txt` note

- No third-party dependency is required at the moment.
- If installed via ComfyUI Manager in the future, dependencies would be read from `requirements.txt`.

## How to Add Nodes

Node category in current code is:

- **Add Node → Audio Notifier → Audio Notify**

You can also right-click and search:

- `Audio Notify`

<img width="600" alt="Add Nodes" src="https://github.com/user-attachments/assets/15a69a83-29f2-4f47-98f2-45fb24b2f48e" />

## Usage

### 5.1 Basic Audio Notify

Use **Audio Notify** for quick tests or as a standalone output-style notify node.

Important timing note:
- If it has no upstream dependency, it may execute early when the prompt starts, which does **not** guarantee the whole workflow has completed.

### 5.2 Trigger Nodes

Trigger nodes have input but no output.
They are useful when you want “play sound when this data becomes ready” without forwarding data.

Example:

```text
VAE Decode (IMAGE)
├── Save Image
└── Audio Notify Image Trigger
```

Important:
- If Trigger and Save Image are parallel branches, ComfyUI does not guarantee Save Image runs first.
- Trigger means “notify after input data is ready”, not “notify after all downstream side effects are done”.

### 5.3 Passthrough Nodes

Passthrough nodes accept input and return the same value unchanged.
You can insert them between two nodes.

Example:

```text
KSampler -> Audio Notify Latent -> VAE Decode
```

This means: when KSampler output latent is ready, play sound, then pass latent to VAE Decode.

### 5.4 `sounds/` folder

If you use repository-local sounds:

1. Put audio files under `ComfyUI-Audio-Notifier/sounds/`.
2. Restart ComfyUI backend.
3. Select the file from `sound_name` dropdown.

Current code does not enforce a fixed extension list in the dropdown; it lists files found in `sounds/`.

### 5.5 Custom `sound_path`

You can also use an absolute/local path on backend machine.

Windows example:

```text
C:\Windows\Media\Windows Notify System Generic.wav
```

Path resolution is on the machine running ComfyUI backend.

## Playback Options

Shared parameters:

- `notification_enabled`: master on/off. If `False`, skip playback.
- `repeat`: play count (`>=1`).
- `delay_seconds`: delay before playback.
- `blocking_playback`:
  - `False` (default): non-blocking daemon thread.
  - `True`: synchronous/blocking playback.
- `enable_sound_path`: whether `sound_path` is considered.
- `sound_path`: custom file path.
- `enable_sound_name`: whether `sound_name` is considered.
- `sound_name`: filename selected from `sounds/`.
- `fallback_to_system_beep`: if no playable file resolves, allow platform beep/bell fallback.

Priority order in current code:
1. If `enable_sound_path=True` and `sound_path` resolves to an existing file, use it.
2. Else if `enable_sound_name=True` and `sound_name` exists in `sounds/`, use it.
3. Else no file is selected; if `fallback_to_system_beep=True`, use system fallback; otherwise skip with log.

## Audio Format Support

Implementation-level behavior:

- **Windows**
  - `.wav` is most reliable via `winsound.PlaySound`.
  - For non-`.wav`, code tries `ffplay` first, then `os.startfile` fallback.
- **macOS**
  - Uses `afplay` for file/default sound playback.
- **Linux**
  - Tries `ffplay`, then `paplay` / `aplay`.

If no playback method works, the final fallback is system beep or terminal bell (depending on platform and settings).

## Timing Notes and Limitations

- Backend nodes execute when ComfyUI scheduler reaches that node.
- Trigger nodes are not global workflow-completion listeners.
- Parallel branches may execute in an order different from user expectation.
- Strict “play only after entire prompt/queue is completed” requires a future frontend/global listener extension.
- Audio always plays on backend machine.

## Troubleshooting

### Node does not appear

- Check folder structure under `ComfyUI/custom_nodes`.
- Restart ComfyUI backend.
- Check backend console for import errors.

### No sound

- Check system volume and output device on backend machine.
- Try a `.wav` file first.
- On Windows, try:
  - `C:\Windows\Media\Windows Notify System Generic.wav`

### mp3/m4a does not play

- Try `.wav` first.
- If your setup depends on `ffplay`, install FFmpeg/ffplay.

### Sound plays too early

- Review node dependency graph.
- Trigger timing depends on input readiness, not global completion.

### ZIP install created nested folder

Fix so that files are directly under:

```text
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/__init__.py
ComfyUI/custom_nodes/ComfyUI-Audio-Notifier/audio_notifier.py
```

## Development

Brief structure:

- `__init__.py`: ComfyUI node exports.
- `audio_notifier.py`: node definitions and playback logic.
- `README.md` / `README.zh-CN.md`: project docs.
- `requirements.txt`: dependency placeholder.

Syntax check:

```bash
python -m py_compile __init__.py audio_notifier.py
```

If tests exist, run them as appropriate.

## License

MIT
