# AutoAccounting isolated UI source candidate

This source-only project is a reduced-dependency test host for 19 existing Android UI tests. It is a new build, not verification of a previously built AutoAccounting APK and not a complete application release.

## Preserved behavior

The DataFragment screen, BillEditorDialog and dialog components, refund selection and validation, Room database/DAOs, bill-creation idempotency, and all 19 original UI test methods and assertions remain byte-identical to the frozen source baseline. The existing synthetic HTTP boundary is also unchanged: it uses an isolated real Room database and rejects unexpected endpoints. The original MMKV settings implementation is retained.

The isolated manifest requests no permissions and exposes only a non-exported test host activity, with no providers, services, receivers, or Xposed metadata. Production startup is skipped by the original build-time guard. The application package remains net.ankio.auto.isolatedui; the test runner remains net.ankio.auto.isolated.IsolatedUiTestRunner.

## Excluded functionality and inputs

- OCR module, OCR wrapper and models: removed. OCR adapter calls fail closed.
- Back-tap module, all nine models and vendor-derived algorithms: removed. Detector/logger adapter calls fail closed.
- Bugly SDK and native libraries: removed. Crash-report adapter calls fail closed.
- All original app web assets and Xposed asset entry point: excluded. Rule-editor and summary web views are not available.
- Historical screenshots, financial sample files, IDE/device configuration, Git history, old workflows, credentials, signing keys, build caches and logs: not included.
- Only the isolated app variant is enabled. Normal app startup, real network, AI login, OCR recognition, back-tap sensors, accessibility capture, notification/SMS collection, exports, and actual Xposed hooks are not tested.

Other production sources are retained to satisfy normal compile-time references without replacing the real UI. Their presence does not imply those entry points are enabled or tested. See NOTICE.md and docs/BOUNDARIES.md for the exact limited adapter changes.

## Build

Use JDK 21, Android SDK platform 36 and Android build-tools 35.0.0. Gradle 8.11.1 and its checksum are pinned by the wrapper. No private source repository is required.

    ./gradlew --no-daemon --max-workers=2 -PisolatedUiTests=true :app:assembleIsolatedUi :app:assembleIsolatedUiAndroidTest

Verify the preserved source and test set:

    python3 scripts/verify-source-boundaries.py

Local validation: both APKs assemble successfully; lint completed with 0 errors and 42 warnings. Static DEX inspection found all 19 expected JUnit-annotated methods. The local candidate has not been run on a device. A successful assemble only compiles the 19 tests; it does not mean they passed. Device execution needs an Android emulator or device. Do not publish generated APKs, AARs, model files, caches, raw build output, logcat, or screenshots as artifacts. Public CI must disclose only reviewed synthetic test results.

## Licensing

Retain the original GPL LICENSE and all author notices. See NOTICE.md for inherited header inconsistencies, the Gradle Wrapper license, and the distinction between this source package and binary redistribution. No third-party license or authorization is invented by this test isolation.

## Dependency integrity

The Gradle verification metadata pins SHA-256 values for the plugin/build/runtime artifacts resolved during this local build and lint run. It was bootstrapped from the existing local dependency cache, not an independent proof of publisher identity or license approval. Default strict verification must remain enabled in CI; a new or mismatching artifact must be reviewed rather than bypassed. verification/resolved-runtime-artifacts.json records the observed runtime coordinates and hashes without including their binaries or local paths.
