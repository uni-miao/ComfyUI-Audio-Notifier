# ComfyUI-Audio-Notifier

English | [中文说明点这里](README.zh-CN.md)

A backend audio notification node pack for ComfyUI. It plays a sound when execution reaches selected nodes.

> [!IMPORTANT]
> Audio is played on the machine running the ComfyUI backend process, not the browser machine.

## Overview

ComfyUI-Audio-Notifier provides output, trigger, and passthrough notification nodes so you can hear progress and completion moments in long workflows.

## Features

- Basic output node: **Audio Notify**
- Generic trigger node: **Audio Notify Trigger** (any input, no output)
- Generic passthrough node: **Audio Notify Passthrough** (any input -> same output)
- Typed compatibility fallback nodes (IMAGE/LATENT/MODEL/CLIP/VAE/AUDIO/VIDEO/STRING)
- Optional custom audio from absolute path or from local `sounds/` directory
- Optional non-blocking playback via background thread
- No third-party Python dependencies

## Installation

1. Clone this repository into `ComfyUI/custom_nodes`.
2. Restart ComfyUI.
3. Add nodes from: **Add Node → Audio Notifier → ...**

## Usage

### Basic Audio Notify

Use **Audio Notify** as an output node for simple completion beeps.

### Trigger node

Use **Audio Notify Trigger** when you want a dependency edge and notification, but no output value.

- Input name: `input` (generic/any type)
- Output: none (`RETURN_TYPES = ()`)
- `OUTPUT_NODE = True`

### Passthrough node

Use **Audio Notify Passthrough** between two nodes to keep data flow while adding sound.

- Input name: `input` (generic/any type)
- Output: same value/type as input

### sounds/ folder

Put audio files into repository `sounds/` and restart ComfyUI. They appear in the `sound_name` dropdown.

## Playback options

All nodes share these parameters:

- `repeat`
- `delay_seconds`
- `notification_enabled`
- `blocking_playback` (default `False`)
- `enable_sound_path`
- `sound_path`
- `enable_sound_name`
- `sound_name`
- `fallback_to_system_beep`

`blocking_playback` behavior:

- `False`: play in a daemon background thread and return immediately (non-blocking)
- `True`: play synchronously and return after playback ends (blocking)

If `notification_enabled = False`, playback is skipped and no background thread is started.

## Notes about trigger timing

Trigger nodes fire as soon as their own input data is ready.

If **Audio Notify ... Trigger** and **Save Image** are connected in parallel to the same `IMAGE`, ComfyUI scheduling does not guarantee `Save Image` finishes first. So sound may play before the file write finishes.

If you need strict “notify only after the whole workflow completes”, prefer a future frontend global completion listener approach.

## Generic vs typed nodes

This project now includes generic nodes and keeps typed nodes as compatibility fallback.

- Generic nodes: fewer menu entries, flexible wiring
- Typed nodes: useful if a ComfyUI setup/plugin expects explicit types

## Windows/macOS/Linux audio format support

- **Windows**
  - `.wav`: `winsound.PlaySound` (most reliable)
  - non-`.wav`: prefers `ffplay -nodisp -autoexit`
  - fallback: system default app (`os.startfile`)
- **macOS**
  - `afplay`
- **Linux**
  - prefers `ffplay`, then `paplay` / `aplay`
  - final fallback: terminal bell

## Troubleshooting

- No sound in Docker/WSL/headless: host audio forwarding may be required.
- `sound_path` invalid: check backend-machine path and permissions.
- Non-WAV on Windows not playing: install `ffplay` or use `.wav`.
- Node runs every queue: implemented `IS_CHANGED` to force execution.
