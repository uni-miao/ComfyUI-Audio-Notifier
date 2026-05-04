import os
import platform
import shutil
import subprocess
import time
from pathlib import Path


class AudioNotifierNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repeat": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
                "delay_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
            },
            "optional": {
                "sound_path": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "notify"
    OUTPUT_NODE = True
    CATEGORY = "utils/audio"

    @classmethod
    def IS_CHANGED(cls, repeat, delay_seconds, sound_path=""):
        # Always run this output node on every queue execution.
        return time.time_ns()

    def notify(self, repeat, delay_seconds, sound_path=""):
        if delay_seconds > 0:
            time.sleep(delay_seconds)

        resolved = self._resolve_path(sound_path)

        for _ in range(max(1, repeat)):
            self._play_sound(resolved)

        return {}

    def _resolve_path(self, sound_path):
        if not sound_path:
            return None
        expanded = os.path.expandvars(os.path.expanduser(sound_path.strip()))
        if not expanded:
            return None
        p = Path(expanded)
        return p if p.is_file() else None

    def _play_sound(self, sound_file):
        system = platform.system().lower()

        if system == "windows":
            if self._play_windows(sound_file):
                return
        elif system == "darwin":
            if self._play_macos(sound_file):
                return
        else:
            if self._play_linux(sound_file):
                return

        # Final fallback: terminal bell
        print("\a", end="", flush=True)

    def _play_windows(self, sound_file):
        try:
            import winsound
        except Exception:
            return False

        try:
            if sound_file:
                winsound.PlaySound(str(sound_file), winsound.SND_FILENAME)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            return True
        except Exception:
            return False

    def _play_macos(self, sound_file):
        afplay = shutil.which("afplay")
        if afplay:
            if sound_file:
                return self._run_command([afplay, str(sound_file)])
            # Use bundled system sound when no file is provided.
            default_sound = "/System/Library/Sounds/Ping.aiff"
            return self._run_command([afplay, default_sound])
        return False

    def _play_linux(self, sound_file):
        if sound_file:
            players = ["paplay", "aplay", "ffplay"]
            for player in players:
                cmd = shutil.which(player)
                if not cmd:
                    continue
                if player == "ffplay":
                    ok = self._run_command([cmd, "-nodisp", "-autoexit", "-loglevel", "quiet", str(sound_file)])
                else:
                    ok = self._run_command([cmd, str(sound_file)])
                if ok:
                    return True
            return False

        # No custom file: try standard desktop/system beep options.
        paplay = shutil.which("paplay")
        if paplay:
            event_sound = "/usr/share/sounds/freedesktop/stereo/complete.oga"
            if Path(event_sound).is_file() and self._run_command([paplay, event_sound]):
                return True

        aplay = shutil.which("aplay")
        if aplay:
            # pcspkr fallback through ALSA utilities if present.
            return self._run_command([aplay, "/usr/share/sounds/alsa/Front_Center.wav"])

        return False

    def _run_command(self, cmd):
        try:
            proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return proc.returncode == 0
        except Exception:
            return False


NODE_CLASS_MAPPINGS = {
    "AudioNotifierNode": AudioNotifierNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AudioNotifierNode": "Audio Notify",
}
