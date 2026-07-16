#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Iterable


PACKAGE_ID = "com.thinkingdata.analytics"
OFFICIAL_REVISION = "c2246848bd759a67a53d2eae61b7c466b9ac6f71"
TARGET_DEPENDENCY = (
    "https://github.com/ThinkingDataAnalytics/unity-sdk.git#" + OFFICIAL_REVISION
)

CORE_DIRECTORY_ROOTS = (
    "Assets/ThinkingAnalytics",
    "Assets/Plugins/iOS/TAThirdParty",
    "Assets/Plugins/iOS/ThinkingDataCore",
    "Assets/Plugins/iOS/ThinkingSDK",
    "Assets/Plugins/PC",
    "Assets/Plugins/OpenHarmony",
)

CORE_FILE_ROOTS = (
    "Assets/Editor/TDInspectors.cs",
    "Assets/Editor/TDPostprocessBuild.cs",
    "Assets/Editor/TDSettings.cs",
    "Assets/Plugins/Android/TDAnalytics.aar",
    "Assets/Plugins/Android/TDCore.aar",
    "Assets/Plugins/Android/ThinkingAnalyticsProxy.java",
    "Assets/Plugins/Android/ThinkingSDK-thirdparty.aar",
    "Assets/Plugins/iOS/ThinkingAnalytics.m",
    "Assets/Plugins/WxHelper.jslib",
)

PRESERVE_DIRECTORY_ROOTS = (
    "Assets/TDRemoteConfig",
    "Assets/TDStrategy",
    "Assets/Plugins/iOS/TDRemoteConfig.xcframework",
    "Assets/Plugins/iOS/TDStrategy.xcframework",
    "Assets/_Project/_Infra/Analytics/ThinkingData",
)

PRESERVE_FILE_ROOTS = (
    "Assets/Plugins/Android/TDRemoteConfig.aar",
    "Assets/Plugins/Android/TDRemoteConfigProxy.java",
    "Assets/Plugins/Android/TDStrategy.aar",
    "Assets/Plugins/Android/TDStrategyProxy.java",
    "Assets/Plugins/iOS/TDRemoteConfigProxy.m",
    "Assets/Plugins/iOS/TDStrategyProxy.m",
    "Assets/Resources/TDAnalyticSetting.asset",
    "Assets/_Project/_Infra/Analytics/TD_Ops.cs",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect the Cat Merge ThinkingData Core migration without changing files."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Unity project root containing Assets and Packages (default: current directory).",
    )
    return parser.parse_args()


def is_existing(path: Path) -> bool:
    return os.path.lexists(path)


def relative_path(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def enumerate_inventory(
    repo_root: Path,
    directory_roots: Iterable[str],
    file_roots: Iterable[str],
) -> list[str]:
    inventory: set[str] = set()
    for relative_root in directory_roots:
        root = repo_root / relative_root
        if root.is_symlink():
            inventory.add(relative_root)
        elif root.is_dir():
            for candidate in root.rglob("*"):
                if candidate.is_file() or candidate.is_symlink():
                    inventory.add(relative_path(repo_root, candidate))
        elif is_existing(root):
            inventory.add(relative_root)

        root_meta = repo_root / (relative_root + ".meta")
        if is_existing(root_meta):
            inventory.add(relative_root + ".meta")

    for relative_file in file_roots:
        candidate = repo_root / relative_file
        if is_existing(candidate):
            inventory.add(relative_file)
        meta = repo_root / (relative_file + ".meta")
        if is_existing(meta):
            inventory.add(relative_file + ".meta")

    return sorted(inventory)


def read_manifest(repo_root: Path) -> tuple[str, str, list[str]]:
    manifest_path = repo_root / "Packages" / "manifest.json"
    warnings: list[str] = []
    if not manifest_path.is_file():
        return "", "missing", ["Packages/manifest.json was not found."]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return "", "invalid", [f"Packages/manifest.json could not be parsed: {error}"]

    dependencies = manifest.get("dependencies")
    if not isinstance(dependencies, dict):
        warnings.append("Packages/manifest.json does not contain a dependencies object.")
        return "", "add", warnings

    current = dependencies.get(PACKAGE_ID, "")
    if not isinstance(current, str):
        warnings.append(f"{PACKAGE_ID} has a non-string manifest value.")
        return str(current), "replace", warnings
    if current == TARGET_DEPENDENCY:
        return current, "noChange", warnings
    return current, "replace" if current else "add", warnings


def create_plan(repo_root: Path) -> dict:
    removal_files = enumerate_inventory(repo_root, CORE_DIRECTORY_ROOTS, CORE_FILE_ROOTS)
    preserve_files = enumerate_inventory(
        repo_root,
        PRESERVE_DIRECTORY_ROOTS,
        PRESERVE_FILE_ROOTS,
    )
    overlap = sorted(set(removal_files).intersection(preserve_files))
    if overlap:
        raise RuntimeError("Removal and preservation inventories overlap: " + ", ".join(overlap))

    current_dependency, manifest_action, warnings = read_manifest(repo_root)
    content = {
        "schemaVersion": 1,
        "officialRevision": OFFICIAL_REVISION,
        "removalFiles": removal_files,
        "preserveFiles": preserve_files,
        "manifestChange": {
            "path": "Packages/manifest.json",
            "packageId": PACKAGE_ID,
            "action": manifest_action,
            "before": current_dependency,
            "after": TARGET_DEPENDENCY,
        },
    }
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    plan_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "success": True,
        "code": "INSPECTED",
        "message": "Inspected the ThinkingData migration without changing project state.",
        "planId": plan_id,
        **content,
        "summary": {
            "removalFileCount": len(removal_files),
            "preserveFileCount": len(preserve_files),
            "manifestAction": manifest_action,
        },
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    if not (repo_root / "Assets").is_dir() or not (repo_root / "Packages").is_dir():
        result = {
            "success": False,
            "code": "PROJECT_ROOT_INVALID",
            "message": "The repo root must contain Assets and Packages directories.",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    try:
        result = create_plan(repo_root)
    except (OSError, RuntimeError) as error:
        result = {
            "success": False,
            "code": "INSPECTION_FAILED",
            "message": str(error),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
