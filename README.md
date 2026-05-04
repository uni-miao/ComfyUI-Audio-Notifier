# ComfyUI-Audio-Notifier

A minimal ComfyUI custom node that plays a sound when the workflow reaches this node.

> [!IMPORTANT]
> The sound is played on the machine running the ComfyUI **backend** process, not necessarily on the browser/client machine.

## Features (MVP)

- Output node for end-of-workflow notification
- Node display name: **Audio Notify**
- Supports default system notification sound
- Supports local custom audio file path (`sound_path`)
- Supports repeat count (`repeat`)
- Supports delay in seconds (`delay_seconds`)
- No third-party Python dependency required

## Installation

1. Clone this repository into your ComfyUI custom nodes directory:

   ```bash
   cd ComfyUI/custom_nodes
   git clone <your-repo-url> ComfyUI-Audio-Notifier
   ```

2. Restart ComfyUI.

3. Search for node: **Audio Notify**.

## Usage

1. Add **Audio Notify** near the end of your workflow as an output node.
2. Configure parameters:
   - `repeat`: how many times to play the sound
   - `delay_seconds`: delay before first playback
   - `sound_path` (optional): local absolute/relative path on the backend machine
3. Queue Prompt.

### Default sound behavior

- If `sound_path` is empty, the node attempts to play a system/default notification sound.

### Custom file behavior

- If `sound_path` points to a valid local file, the node tries to play that file.
- If the file is invalid or playback command is unavailable, it falls back to terminal bell.

## Compatibility

### Windows

- Uses built-in `winsound` first.
- Supports default beep and local file playback through `winsound`.

### macOS

- Uses `afplay`.
- Default fallback sound: `/System/Library/Sounds/Ping.aiff`.

### Linux

Playback command attempt order:

1. `paplay`
2. `aplay`
3. `ffplay`
4. terminal bell (`\a`)

For default sound (no `sound_path`), it tries common system sound files when possible.

## Notes

- `IS_CHANGED` is implemented to force execution on every Queue Prompt, avoiding cache skip for this output node.
- If you run ComfyUI in Docker/WSL/headless servers, host audio setup may be required.
