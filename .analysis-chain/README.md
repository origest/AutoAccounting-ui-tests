# Local draft: synthetic analysis chain once

Reviewed source is hash-pinned. Owner approved publication and one execution on 2026-11-14. This draft makes no claim of a completed device test.

Scope: public origest/AutoAccounting-ui-tests, main, manual workflow dispatch, exact checked-out SHA, first attempt only. Standard ubuntu-24.04 runner. Read-only preflight checks scope and all input pins before saving or changing KVM ACL. Current user only rw is restored and byte-compared in EXIT and always cleanup. No other permission or workflow changes.

Build full reviewed source using Gradle 8.11.1, JDK 21, SDK 36/build tools 35.0.0. Tasks :app:assembleAnalysisFixtureDebug and :app:assembleAnalysisFixtureDebugAndroidTest. Install only freshly built net.ankio.auto.analysisfixture and .test into a new API 34 owned AVD/private foreground ADB server. No baseline/old APK, existing device, snapshot, accounts, external AI, or real user data. The source fixture itself still requires parent audit for these properties.

Single named test: net.ankio.auto.testing.AnalysisCommitWaitDeviceTest#insertedBillSurvivesClientTimeoutWithoutReplay, freshAnalysisFixture=true. Require exactly one passing completion, terminal -1, OK (1 test), and sole analysisStage POST_INSERT_TIMEOUT_SINGLE_ROW_NO_REPLAY. Print only fixed stage and diagnostic enums; never raw instrumentation exceptions. This tests synthetic post-insert timeout semantics, not the original incident root cause, real Xposed capture, OEM background behavior, or app release compatibility.

No APK/log artifact upload, no release, no accounts. Temporary build logs and APKs removed with temp root. SDK/build child process groups are owned and stopped. Emulator and private ADB groups are stopped and guest directories removed even on failure; failed cleanup prevents a pass. Uncatchable host termination is bounded by disposable hosted-runner destruction and is not a verified normal cleanup.

Before publication, exclude __pycache__, local APK/build/cache directories and all unreviewed files. Run test_local_contract.py, py_compile and bash -n. Do not copy the historical parallel-proof source archive here; this workflow requires the full analysis-fixture source archive, which is now locally staged.
