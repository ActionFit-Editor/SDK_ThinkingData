# AI Guide - ActionFit ThinkingData SDK

## Package Identity

- Package ID: `com.actionfit.sdk.thinkingdata`
- Current package version at generation time: `1.0.2`
- Public repository: `https://github.com/ActionFit-Editor/SDK_ThinkingData.git`
- Official SDK package ID: `com.thinkingdata.analytics`
- Official SDK version: `3.4.2`
- Official immutable revision: `c2246848bd759a67a53d2eae61b7c466b9ac6f71`

## Purpose And Boundary

This package is a public, source-only install bridge. It owns the versioned `Editor/SDKInstallProfile.json`, package documentation, contract tests, and a read-only Cat Merge migration inspector. It must not contain ThinkingData SDK source, native binaries, archives, credentials, or project configuration.

The bridge depends on `com.actionfit.custompackagemanager`. Use its Inspect and Plan APIs before any Apply. A bridge install does not authorize vendor SDK installation, Asset deletion, manifest writes, repository publication, catalog updates, or releases.

## Compatibility Contract

The official ThinkingData Unity SDK is pinned to commit `c2246848bd759a67a53d2eae61b7c466b9ac6f71` rather than a moving branch or the latest tag. Cat Merge intentionally uses the 3.4.2 native core with its separately installed TDRemoteConfig and TDStrategy modules. Do not upgrade the pinned revision without validating that complete operational-module set on Android and iOS.

Detection rules classify legacy ThinkingData Core files under `Assets` as conflicting. They classify TDRemoteConfig, TDStrategy, `Assets/Resources/TDAnalyticSetting.asset`, and project-owned analytics integration as adoptable preservation findings. A conflicting finding must block the generic SDK install plan.

## Migration Inspector

`Tools~/inspect_thinkingdata_migration.py` is read-only. It enumerates every existing legacy core file, lists preservation paths, previews the exact `Packages/manifest.json` dependency, and derives a deterministic Plan ID. It must never delete, move, rewrite, import, download, or install anything.

Run `Tests~/test_thinkingdata_migration_inspector.py` after changing its inventories. The tests use temporary fixtures and prove that inspection leaves the fixture byte-for-byte unchanged.

## Validation And Release

- Run the migration inspector tests.
- Run Custom Package Manager package contract validation for `com.actionfit.sdk.thinkingdata`.
- Run the package Editor tests in Unity.
- Confirm the package remains source-only and repository visibility remains Public.
- Publish only after `com.actionfit.custompackagemanager` version `1.1.96` is publicly resolvable.
- Repository creation, push, tag creation, catalog upsert, vendor installation, and project migration require the applicable explicit approval gates.

## Project Router Registration

Requested router entry:

- `Packages/com.actionfit.sdk.thinkingdata/AI_GUIDE.md` - ActionFit ThinkingData SDK owns the public source-only ThinkingData install profile, immutable official revision, and read-only Cat Merge migration inventory.
