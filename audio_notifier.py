import os
import platform
import shutil
import subprocess
import time
from pathlib import Path


SOUNDS_DIR = Path(__file__).resolve().parent / "sounds"


def _list_sound_choices():
    choices = [""]
    if not SOUNDS_DIR.is_dir():
        return choices
    for p in sorted(SOUNDS_DIR.iterdir()):
        if p.is_file():
            choices.append(p.name)
    return choices


class _AudioNotifyBase:
    CATEGORY = "utils/audio"

    @classmethod
    def _common_inputs(cls):
        return {
            "repeat": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
            "delay_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
            "sound_path": ("STRING", {"default": "", "multiline": False}),
            "sound_name": (_list_sound_choices(), {"default": ""}),
        }

    def _play_notify(self, repeat, delay_seconds, sound_path="", sound_name=""):
        if delay_seconds > 0:
            time.sleep(delay_seconds)

        resolved = self._resolve_sound(sound_path, sound_name)

        for _ in range(max(1, repeat)):
            self._play_sound(resolved)

    def _resolve_sound(self, sound_path, sound_name):
        # 1) Explicit path has highest priority.
        path_file = self._resolve_path(sound_path)
        if path_file:
            return path_file

        # 2) Named sound under sounds/ directory.
        named_file = self._resolve_named_sound(sound_name)
        if named_file:
            return named_file

        # 3) Fallback to platform default/system sound.
        return None

    def _resolve_named_sound(self, sound_name):
        name = (sound_name or "").strip()
        if not name:
            return None
        candidate = SOUNDS_DIR / name
        return candidate if candidate.is_file() else None

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

        print("\a", end="", flush=True)

    def _play_windows(self, sound_file):
        try:
            import winsound
        except Exception:
            return False

        try:
            if sound_file and sound_file.suffix.lower() == ".wav":
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
            return self._run_command([afplay, "/System/Library/Sounds/Ping.aiff"])
        return False

    def _play_linux(self, sound_file):
        if sound_file:
            for player in ["paplay", "aplay", "ffplay"]:
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

        paplay = shutil.which("paplay")
        if paplay:
            event_sound = "/usr/share/sounds/freedesktop/stereo/complete.oga"
            if Path(event_sound).is_file() and self._run_command([paplay, event_sound]):
                return True

        aplay = shutil.which("aplay")
        if aplay:
            return self._run_command([aplay, "/usr/share/sounds/alsa/Front_Center.wav"])

        return False

    def _run_command(self, cmd):
        try:
            proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return proc.returncode == 0
        except Exception:
            return False


class AudioNotifierNode(_AudioNotifyBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": cls._common_inputs()}

    RETURN_TYPES = ()
    FUNCTION = "notify"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, repeat, delay_seconds, sound_path="", sound_name=""):
        return time.time_ns()

    def notify(self, repeat, delay_seconds, sound_path="", sound_name=""):
        self._play_notify(repeat, delay_seconds, sound_path, sound_name)
        return ()


class _AudioNotifyPassthroughBase(_AudioNotifyBase):
    OUTPUT_NODE = False

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return time.time_ns()

    def passthrough(self, value, repeat, delay_seconds, sound_path="", sound_name=""):
        self._play_notify(repeat, delay_seconds, sound_path, sound_name)
        return (value,)


class AudioNotifyImageNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",), **cls._common_inputs()}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"

    def run(self, image, repeat, delay_seconds, sound_path="", sound_name=""):
        return self.passthrough(image, repeat, delay_seconds, sound_path, sound_name)


class AudioNotifyLatentNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"latent": ("LATENT",), **cls._common_inputs()}}

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "run"

    def run(self, latent, repeat, delay_seconds, sound_path="", sound_name=""):
        return self.passthrough(latent, repeat, delay_seconds, sound_path, sound_name)


class AudioNotifyModelNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model": ("MODEL",), **cls._common_inputs()}}

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "run"

    def run(self, model, repeat, delay_seconds, sound_path="", sound_name=""):
        return self.passthrough(model, repeat, delay_seconds, sound_path, sound_name)


class AudioNotifyClipNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"clip": ("CLIP",), **cls._common_inputs()}}

    RETURN_TYPES = ("CLIP",)
    FUNCTION = "run"

    def run(self, clip, repeat, delay_seconds, sound_path="", sound_name=""):
        return self.passthrough(clip, repeat, delay_seconds, sound_path, sound_name)


class AudioNotifyVAENode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"vae": ("VAE",), **cls._common_inputs()}}

    RETURN_TYPES = ("VAE",)
    FUNCTION = "run"

    def run(self, vae, repeat, delay_seconds, sound_path="", sound_name=""):
        return self.passthrough(vae, repeat, delay_seconds, sound_path, sound_name)


class AudioNotifyAudioNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"audio": ("AUDIO",), **cls._common_inputs()}}

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "run"

    def run(self, audio, repeat, delay_seconds, sound_path="", sound_name=""):
        return self.passthrough(audio, repeat, delay_seconds, sound_path, sound_name)


class AudioNotifyTextNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                **cls._common_inputs(),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"

    def run(self, text, repeat, delay_seconds, sound_path="", sound_name=""):
        return self.passthrough(text, repeat, delay_seconds, sound_path, sound_name)


NODE_CLASS_MAPPINGS = {
    "AudioNotifierNode": AudioNotifierNode,
    "AudioNotifyImageNode": AudioNotifyImageNode,
    "AudioNotifyLatentNode": AudioNotifyLatentNode,
    "AudioNotifyModelNode": AudioNotifyModelNode,
    "AudioNotifyClipNode": AudioNotifyClipNode,
    "AudioNotifyVAENode": AudioNotifyVAENode,
    "AudioNotifyAudioNode": AudioNotifyAudioNode,
    "AudioNotifyTextNode": AudioNotifyTextNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AudioNotifierNode": "Audio Notify",
    "AudioNotifyImageNode": "Audio Notify Image",
    "AudioNotifyLatentNode": "Audio Notify Latent",
    "AudioNotifyModelNode": "Audio Notify Model",
    "AudioNotifyClipNode": "Audio Notify Clip",
    "AudioNotifyVAENode": "Audio Notify VAE",
    "AudioNotifyAudioNode": "Audio Notify Audio",
    "AudioNotifyTextNode": "Audio Notify Text",
}
