#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
INSPECTOR = SCRIPT_DIR.parent / "Tools~" / "inspect_thinkingdata_migration.py"
TARGET_DEPENDENCY = (
    "https://github.com/ThinkingDataAnalytics/unity-sdk.git#"
    "c2246848bd759a67a53d2eae61b7c466b9ac6f71"
)


class ThinkingDataMigrationInspectorTests(unittest.TestCase):
    def make_project(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "Assets" / "ThinkingAnalytics" / "Runtime").mkdir(parents=True)
        (root / "Assets" / "ThinkingAnalytics" / "Runtime" / "TDAnalytics.cs").write_text(
            "public class TDAnalytics {}\n",
            encoding="utf-8",
        )
        (root / "Assets" / "ThinkingAnalytics.meta").write_text("core-root-meta\n", encoding="utf-8")
        (root / "Assets" / "Plugins" / "Android").mkdir(parents=True)
        (root / "Assets" / "Plugins" / "Android" / "TDAnalytics.aar").write_bytes(b"core")
        (root / "Assets" / "Plugins" / "Android" / "TDRemoteConfig.aar").write_bytes(
            b"preserve"
        )
        remote_config_framework = (
            root
            / "Assets"
            / "Plugins"
            / "iOS"
            / "TDRemoteConfig.xcframework"
            / "ios-arm64"
        )
        remote_config_framework.mkdir(parents=True)
        (remote_config_framework / "TDRemoteConfig").write_bytes(b"preserve-ios")
        (root / "Assets" / "TDStrategy").mkdir(parents=True)
        (root / "Assets" / "TDStrategy" / "TDStrategy.cs").write_text(
            "public class TDStrategy {}\n",
            encoding="utf-8",
        )
        (root / "Assets" / "Resources").mkdir(parents=True)
        (root / "Assets" / "Resources" / "TDAnalyticSetting.asset").write_text(
            "project-setting\n",
            encoding="utf-8",
        )
        (root / "Packages").mkdir()
        (root / "Packages" / "manifest.json").write_text(
            json.dumps({"dependencies": {"com.example.keep": "1.0.0"}}, indent=2) + "\n",
            encoding="utf-8",
        )
        return temporary, root

    def snapshot(self, root: Path) -> dict[str, str]:
        result: dict[str, str] = {}
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = path.relative_to(root).as_posix()
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return result

    def run_inspector(self, root: Path) -> dict:
        completed = subprocess.run(
            [sys.executable, str(INSPECTOR), "--repo-root", str(root)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        return json.loads(completed.stdout)

    def test_inspection_lists_exact_core_and_preservation_files_without_writes(self) -> None:
        temporary, root = self.make_project()
        self.addCleanup(temporary.cleanup)
        before = self.snapshot(root)

        result = self.run_inspector(root)

        self.assertTrue(result["success"])
        self.assertEqual("INSPECTED", result["code"])
        self.assertIn(
            "Assets/ThinkingAnalytics/Runtime/TDAnalytics.cs",
            result["removalFiles"],
        )
        self.assertIn("Assets/ThinkingAnalytics.meta", result["removalFiles"])
        self.assertIn("Assets/Plugins/Android/TDAnalytics.aar", result["removalFiles"])
        self.assertIn("Assets/Plugins/Android/TDRemoteConfig.aar", result["preserveFiles"])
        self.assertIn(
            "Assets/Plugins/iOS/TDRemoteConfig.xcframework/ios-arm64/TDRemoteConfig",
            result["preserveFiles"],
        )
        self.assertIn("Assets/TDStrategy/TDStrategy.cs", result["preserveFiles"])
        self.assertIn(
            "Assets/Resources/TDAnalyticSetting.asset",
            result["preserveFiles"],
        )
        self.assertTrue(set(result["removalFiles"]).isdisjoint(result["preserveFiles"]))
        self.assertEqual("add", result["manifestChange"]["action"])
        self.assertEqual(TARGET_DEPENDENCY, result["manifestChange"]["after"])
        self.assertEqual(before, self.snapshot(root))

    def test_plan_id_is_deterministic_and_exact_dependency_is_no_change(self) -> None:
        temporary, root = self.make_project()
        self.addCleanup(temporary.cleanup)
        manifest_path = root / "Packages" / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {"dependencies": {"com.thinkingdata.analytics": TARGET_DEPENDENCY}},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        before = self.snapshot(root)

        first = self.run_inspector(root)
        second = self.run_inspector(root)

        self.assertEqual(first["planId"], second["planId"])
        self.assertEqual("noChange", first["manifestChange"]["action"])
        self.assertEqual(before, self.snapshot(root))


if __name__ == "__main__":
    unittest.main()
