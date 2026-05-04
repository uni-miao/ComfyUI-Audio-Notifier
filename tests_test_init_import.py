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
            # Simulate ComfyUI loading from custom_nodes package path, not via repo-root import.
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

            self.assertIn("AudioNotifierNode", module.NODE_CLASS_MAPPINGS)
            self.assertEqual(
                module.NODE_DISPLAY_NAME_MAPPINGS["AudioNotifierNode"],
                "Audio Notify",
            )
            self.assertEqual(
                module.NODE_CLASS_MAPPINGS["AudioNotifierNode"].CATEGORY,
                "utils/audio",
            )
        finally:
            sys.path = original_sys_path
            sys.modules.clear()
            sys.modules.update(original_modules)


if __name__ == "__main__":
    unittest.main()
