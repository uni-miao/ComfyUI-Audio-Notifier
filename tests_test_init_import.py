import importlib.util
import pathlib
import sys
import unittest


class TestComfyUIPackageImport(unittest.TestCase):
    def test_init_can_load_as_package_without_repo_on_sys_path(self):
        repo_root = pathlib.Path(__file__).resolve().parent
        init_file = repo_root / "__init__.py"

        module_name = "ComfyUI_Audio_Notifier"
        original_sys_path = list(sys.path)
        original_modules = dict(sys.modules)
        try:
            sys.path = [p for p in sys.path if pathlib.Path(p).resolve() != repo_root]

            spec = importlib.util.spec_from_file_location(
                module_name,
                init_file,
                submodule_search_locations=[str(repo_root)],
            )
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            expected_nodes = {
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

            for key, display_name in expected_nodes.items():
                self.assertIn(key, module.NODE_CLASS_MAPPINGS)
                self.assertEqual(module.NODE_DISPLAY_NAME_MAPPINGS[key], display_name)
                self.assertEqual(module.NODE_CLASS_MAPPINGS[key].CATEGORY, "Audio Notifier")

            self.assertEqual(module.NODE_CLASS_MAPPINGS["AudioNotifyVideoNode"].RETURN_TYPES, ("VIDEO",))

            trigger_keys = [
                "AudioNotifyTriggerNode",
                "AudioNotifyImageTriggerNode",
                "AudioNotifyLatentTriggerNode",
                "AudioNotifyAudioTriggerNode",
                "AudioNotifyVideoTriggerNode",
                "AudioNotifyTextTriggerNode",
            ]
            for key in trigger_keys:
                self.assertEqual(module.NODE_CLASS_MAPPINGS[key].RETURN_TYPES, ())
                self.assertTrue(module.NODE_CLASS_MAPPINGS[key].OUTPUT_NODE)

            self.assertIn("blocking_playback", module.NODE_CLASS_MAPPINGS["AudioNotifierNode"].INPUT_TYPES()["required"])
            self.assertIn("blocking_playback", module.NODE_CLASS_MAPPINGS["AudioNotifyImageNode"].INPUT_TYPES()["required"])
            self.assertIn("blocking_playback", module.NODE_CLASS_MAPPINGS["AudioNotifyTriggerNode"].INPUT_TYPES()["required"])

            self.assertIn("AudioNotifierNode", module.NODE_CLASS_MAPPINGS)
            self.assertIn("AudioNotifyTriggerNode", module.NODE_CLASS_MAPPINGS)
            self.assertIn("AudioNotifyPassthroughNode", module.NODE_CLASS_MAPPINGS)
        finally:
            sys.path = original_sys_path
            sys.modules.clear()
            sys.modules.update(original_modules)


if __name__ == "__main__":
    unittest.main()
