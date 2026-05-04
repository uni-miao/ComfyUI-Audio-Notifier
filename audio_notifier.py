import os
import platform
import shutil
import subprocess
import threading
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
    CATEGORY = "Audio Notifier"

    @classmethod
    def _common_inputs(cls):
        return {
            "repeat": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
            "delay_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
            "notification_enabled": ("BOOLEAN", {"default": True}),
            "blocking_playback": ("BOOLEAN", {"default": False}),
            "enable_sound_path": ("BOOLEAN", {"default": False}),
            "sound_path": ("STRING", {"default": "", "multiline": False}),
            "enable_sound_name": ("BOOLEAN", {"default": False}),
            "sound_name": (_list_sound_choices(), {"default": ""}),
            "fallback_to_system_beep": ("BOOLEAN", {"default": True}),
        }

    def _play_notify(
        self,
        repeat,
        delay_seconds,
        notification_enabled=True,
        blocking_playback=False,
        enable_sound_path=False,
        sound_path="",
        enable_sound_name=False,
        sound_name="",
        fallback_to_system_beep=True,
    ):
        if not notification_enabled:
            print("[Audio Notify] notification disabled; skipping playback")
            return

        kwargs = {
            "repeat": repeat,
            "delay_seconds": delay_seconds,
            "enable_sound_path": enable_sound_path,
            "sound_path": sound_path,
            "enable_sound_name": enable_sound_name,
            "sound_name": sound_name,
            "fallback_to_system_beep": fallback_to_system_beep,
        }

        if blocking_playback:
            self._play_notify_impl(**kwargs)
            return

        thread = threading.Thread(target=self._play_notify_bg, kwargs=kwargs, daemon=True)
        thread.start()

    def _play_notify_bg(self, **kwargs):
        try:
            self._play_notify_impl(**kwargs)
        except Exception as exc:
            print(f"[Audio Notify] background playback failed: {exc}")

    def _play_notify_impl(
        self,
        repeat,
        delay_seconds,
        enable_sound_path=False,
        sound_path="",
        enable_sound_name=False,
        sound_name="",
        fallback_to_system_beep=True,
    ):
        if delay_seconds > 0:
            time.sleep(delay_seconds)

        resolved = self._resolve_sound(enable_sound_path, sound_path, enable_sound_name, sound_name)
        if not resolved and not fallback_to_system_beep:
            print("[Audio Notify] no sound source selected; fallback_to_system_beep is disabled")
            return

        for _ in range(max(1, repeat)):
            self._play_sound(resolved)

    def _resolve_sound(self, enable_sound_path, sound_path, enable_sound_name, sound_name):
        if enable_sound_path:
            path_file = self._resolve_path(sound_path)
            if path_file:
                return path_file

        if enable_sound_name:
            named_file = self._resolve_named_sound(sound_name)
            if named_file:
                return named_file

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
        if sound_file and sound_file.suffix.lower() == ".wav":
            try:
                import winsound

                winsound.PlaySound(str(sound_file), winsound.SND_FILENAME)
                return True
            except Exception:
                return False

        if sound_file:
            ffplay = shutil.which("ffplay")
            if ffplay and self._run_command([ffplay, "-nodisp", "-autoexit", str(sound_file)]):
                return True

            try:
                os.startfile(str(sound_file))
                return True
            except Exception:
                return False

        try:
            import winsound

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
            ffplay = shutil.which("ffplay")
            if ffplay and self._run_command([ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet", str(sound_file)]):
                return True

            for player in ["paplay", "aplay"]:
                cmd = shutil.which(player)
                if cmd and self._run_command([cmd, str(sound_file)]):
                    return True
            return False

        for player, default_file in [
            ("paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"),
            ("aplay", "/usr/share/sounds/alsa/Front_Center.wav"),
        ]:
            cmd = shutil.which(player)
            if cmd and Path(default_file).is_file() and self._run_command([cmd, default_file]):
                return True
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
    def IS_CHANGED(cls, **kwargs):
        return time.time_ns()

    def notify(self, **kwargs):
        self._play_notify(**kwargs)
        return ()


class _AudioNotifyPassthroughBase(_AudioNotifyBase):
    OUTPUT_NODE = False

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return time.time_ns()

    def passthrough(self, value, **kwargs):
        self._play_notify(**kwargs)
        return (value,)


class _AudioNotifyTriggerBase(_AudioNotifyBase):
    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return time.time_ns()

    def trigger(self, **kwargs):
        self._play_notify(**kwargs)
        return ()


class AudioNotifyTriggerNode(_AudioNotifyTriggerBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"input": ("*", {}), **cls._common_inputs()}}

    def run(self, input, **kwargs):
        return self.trigger(**kwargs)


class AudioNotifyPassthroughNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"input": ("*", {}), **cls._common_inputs()}}

    RETURN_TYPES = ("*",)
    FUNCTION = "run"

    def run(self, input, **kwargs):
        return self.passthrough(input, **kwargs)


class AudioNotifyImageNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",), **cls._common_inputs()}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"

    def run(self, image, **kwargs):
        return self.passthrough(image, **kwargs)


class AudioNotifyLatentNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"latent": ("LATENT",), **cls._common_inputs()}}

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "run"

    def run(self, latent, **kwargs):
        return self.passthrough(latent, **kwargs)


class AudioNotifyModelNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model": ("MODEL",), **cls._common_inputs()}}

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "run"

    def run(self, model, **kwargs):
        return self.passthrough(model, **kwargs)


class AudioNotifyClipNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"clip": ("CLIP",), **cls._common_inputs()}}

    RETURN_TYPES = ("CLIP",)
    FUNCTION = "run"

    def run(self, clip, **kwargs):
        return self.passthrough(clip, **kwargs)


class AudioNotifyVAENode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"vae": ("VAE",), **cls._common_inputs()}}

    RETURN_TYPES = ("VAE",)
    FUNCTION = "run"

    def run(self, vae, **kwargs):
        return self.passthrough(vae, **kwargs)


class AudioNotifyAudioNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"audio": ("AUDIO",), **cls._common_inputs()}}

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "run"

    def run(self, audio, **kwargs):
        return self.passthrough(audio, **kwargs)


class AudioNotifyVideoNode(_AudioNotifyPassthroughBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"video": ("VIDEO",), **cls._common_inputs()}}

    RETURN_TYPES = ("VIDEO",)
    FUNCTION = "run"

    def run(self, video, **kwargs):
        return self.passthrough(video, **kwargs)


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

    def run(self, text, **kwargs):
        return self.passthrough(text, **kwargs)


class AudioNotifyImageTriggerNode(_AudioNotifyTriggerBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",), **cls._common_inputs()}}

    def run(self, image, **kwargs):
        return self.trigger(**kwargs)


class AudioNotifyLatentTriggerNode(_AudioNotifyTriggerBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"latent": ("LATENT",), **cls._common_inputs()}}

    def run(self, latent, **kwargs):
        return self.trigger(**kwargs)


class AudioNotifyAudioTriggerNode(_AudioNotifyTriggerBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"audio": ("AUDIO",), **cls._common_inputs()}}

    def run(self, audio, **kwargs):
        return self.trigger(**kwargs)


class AudioNotifyVideoTriggerNode(_AudioNotifyTriggerBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"video": ("VIDEO",), **cls._common_inputs()}}

    def run(self, video, **kwargs):
        return self.trigger(**kwargs)


class AudioNotifyTextTriggerNode(_AudioNotifyTriggerBase):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                **cls._common_inputs(),
            }
        }

    def run(self, text, **kwargs):
        return self.trigger(**kwargs)


NODE_CLASS_MAPPINGS = {
    "AudioNotifierNode": AudioNotifierNode,
    "AudioNotifyTriggerNode": AudioNotifyTriggerNode,
    "AudioNotifyPassthroughNode": AudioNotifyPassthroughNode,
    "AudioNotifyImageNode": AudioNotifyImageNode,
    "AudioNotifyLatentNode": AudioNotifyLatentNode,
    "AudioNotifyModelNode": AudioNotifyModelNode,
    "AudioNotifyClipNode": AudioNotifyClipNode,
    "AudioNotifyVAENode": AudioNotifyVAENode,
    "AudioNotifyAudioNode": AudioNotifyAudioNode,
    "AudioNotifyVideoNode": AudioNotifyVideoNode,
    "AudioNotifyTextNode": AudioNotifyTextNode,
    "AudioNotifyImageTriggerNode": AudioNotifyImageTriggerNode,
    "AudioNotifyLatentTriggerNode": AudioNotifyLatentTriggerNode,
    "AudioNotifyAudioTriggerNode": AudioNotifyAudioTriggerNode,
    "AudioNotifyVideoTriggerNode": AudioNotifyVideoTriggerNode,
    "AudioNotifyTextTriggerNode": AudioNotifyTextTriggerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AudioNotifierNode": "Audio Notify",
    "AudioNotifyTriggerNode": "Audio Notify Trigger",
    "AudioNotifyPassthroughNode": "Audio Notify Passthrough",
    "AudioNotifyImageNode": "Audio Notify Image",
    "AudioNotifyLatentNode": "Audio Notify Latent",
    "AudioNotifyModelNode": "Audio Notify Model",
    "AudioNotifyClipNode": "Audio Notify Clip",
    "AudioNotifyVAENode": "Audio Notify VAE",
    "AudioNotifyAudioNode": "Audio Notify Audio",
    "AudioNotifyVideoNode": "Audio Notify Video",
    "AudioNotifyTextNode": "Audio Notify Text",
    "AudioNotifyImageTriggerNode": "Audio Notify Image Trigger",
    "AudioNotifyLatentTriggerNode": "Audio Notify Latent Trigger",
    "AudioNotifyAudioTriggerNode": "Audio Notify Audio Trigger",
    "AudioNotifyVideoTriggerNode": "Audio Notify Video Trigger",
    "AudioNotifyTextTriggerNode": "Audio Notify Text Trigger",
}
