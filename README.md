# ActionFit ThinkingData SDK (`com.actionfit.sdk.thinkingdata`)

ThinkingData Analytics Unity SDK를 공식 Git 저장소에서 설치하기 위한 공개 소스 전용 브리지입니다. SDK 소스, 바이너리, 프로젝트 설정과 인증 정보는 이 패키지에 재배포하지 않습니다.

## 설치

Custom Package Manager `1.1.96`가 공개된 뒤 `Packages/manifest.json`에 다음 의존성을 추가합니다.

```json
{
  "dependencies": {
    "com.actionfit.sdk.thinkingdata": "https://github.com/ActionFit-Editor/SDK_ThinkingData.git#1.0.4"
  }
}
```

브리지 설치만으로 벤더 SDK가 추가되지는 않습니다. Custom Package Manager의 SDK Profiles 화면에서 `Editor/SDKInstallProfile.json`을 열고 Inspect와 Plan 결과를 검토한 뒤 명시적으로 Apply해야 합니다.

## 고정 버전

프로필은 ThinkingData Unity SDK `3.4.2`의 공식 커밋 `c2246848bd759a67a53d2eae61b7c466b9ac6f71`을 사용합니다. Cat Merge에서 함께 사용하는 TDRemoteConfig와 TDStrategy의 네이티브 모듈 호환 세트를 유지하기 위한 고정값이며, 임의로 최신 태그를 따라가지 않습니다.

## Cat Merge 이전 점검

현재 `Assets` 기반 ThinkingData Core 설치가 있으면 설치 계획은 충돌로 차단됩니다. 아래 명령은 제거 대상, 보존 대상, manifest 변경과 내용 기반 Plan ID를 JSON으로 출력할 뿐 프로젝트를 변경하지 않습니다.

```bash
python3 Packages/com.actionfit.sdk.thinkingdata/Tools~/inspect_thinkingdata_migration.py --repo-root .
```

TDRemoteConfig, TDStrategy, `TDAnalyticSetting.asset`과 프로젝트 소유 분석 어댑터는 보존 대상입니다. 제거 또는 manifest 변경은 인스펙터 결과에 대한 별도 승인 후에만 수행합니다.

## 검증

```bash
python3 Packages/com.actionfit.sdk.thinkingdata/Tests~/test_thinkingdata_migration_inspector.py
python3 Packages/com.actionfit.custompackagemanager/Tools~/package_contract_validator.py --package com.actionfit.sdk.thinkingdata
```
