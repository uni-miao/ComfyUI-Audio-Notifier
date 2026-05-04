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

            self.assertIn("NODE_CLASS_MAPPINGS", module.__all__)
            self.assertIn("NODE_DISPLAY_NAME_MAPPINGS", module.__all__)

            expected_nodes = {
                "AudioNotifierNode": "Audio Notify",
                "AudioNotifyImageNode": "Audio Notify Image",
                "AudioNotifyLatentNode": "Audio Notify Latent",
                "AudioNotifyModelNode": "Audio Notify Model",
                "AudioNotifyClipNode": "Audio Notify Clip",
                "AudioNotifyVAENode": "Audio Notify VAE",
                "AudioNotifyAudioNode": "Audio Notify Audio",
                "AudioNotifyTextNode": "Audio Notify Text",
            }

            for key, display_name in expected_nodes.items():
                self.assertIn(key, module.NODE_CLASS_MAPPINGS)
                self.assertEqual(module.NODE_DISPLAY_NAME_MAPPINGS[key], display_name)
                self.assertEqual(module.NODE_CLASS_MAPPINGS[key].CATEGORY, "utils/audio")

            return_types_expected = {
                "AudioNotifyImageNode": ("IMAGE",),
                "AudioNotifyLatentNode": ("LATENT",),
                "AudioNotifyModelNode": ("MODEL",),
                "AudioNotifyClipNode": ("CLIP",),
                "AudioNotifyVAENode": ("VAE",),
                "AudioNotifyAudioNode": ("AUDIO",),
                "AudioNotifyTextNode": ("STRING",),
            }
            for key, expected in return_types_expected.items():
                self.assertEqual(module.NODE_CLASS_MAPPINGS[key].RETURN_TYPES, expected)
        finally:
            sys.path = original_sys_path
            sys.modules.clear()
            sys.modules.update(original_modules)


if __name__ == "__main__":
    unittest.main()
