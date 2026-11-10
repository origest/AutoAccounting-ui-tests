# AutoAccounting isolated UI validation

This source-only test project is derived from
[AutoAccounting](https://github.com/AutoAccountingOrg/AutoAccounting). It builds
a dedicated isolated application from reviewed source and runs 19 exact
instrumentation methods on one fresh Android 13 / API 33 x86_64 emulator.

## Current local candidate, not a new device result

This candidate has not been published or run on a device. Independent review
and fresh authorization for one exact-commit attempt are required before use.
Local tests and compilation are not device results and do not promise that the
next attempt will succeed.

The latest completed public attempt was
[42805128904](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42805128904),
commit `2c6b190539bdc4cf6dd915d19e6a61f0cb92ca21`. Instrumentation reached its
unchanged 600-second command timeout. Valid but incomplete partial evidence
reported **6 passed, 1 started, 12 unknown**. The started method was
`actualRepeatedSwipesDoNotDuplicateRowsOrLeaveSpinnerRunning`. The six observed
passes were:

- successfulEmptyResponseShowsEmptyNotError
- transportFailureShowsErrorAndActualRetryTapRecovers
- nonSuccessAndMissingDataNeverMasqueradeAsEmpty
- actualTypeFilterAndSearchTextSurviveVisibleRefreshAndReentry
- multiPagePassiveRefreshKeepsLoadedPageCountAndVisibleRowOffset
- activityRecreationRestoresNewFragmentFiltersPagesAndScroll

These are partial observations, **not a 19-test suite pass**. That run did not
publish per-case durations. The entire 600 seconds cannot be attributed to the
started method, and the last observed method is not proof of the root cause.
Owned build/runtime termination was verified. Both KVM restore attempts stopped
at `acl_compare / KVM_ACL_CHANGED_EXTERNALLY`, with `write_attempted=false`:
the current ACL was neither the original nor the temporary leased ACL. The
actual differing entries, actor and cause remain unknown. Diagnostic additions
below cannot reconstruct missing evidence from that completed run.

## What changed locally

Only four test-side source files and their protection manifest change:
DataPageIsolatedUiTest.kt, IsolatedUiFixture.kt, and new UiTestDeadline.java and
IsolatedUiProgress.kt. Production UI, the 19 method identities, all 72 assertion
calls, existing await predicates, dependencies, tool locks and licenses remain
unchanged. All old protection entries remain; only the two changed test hashes
are refreshed and the two new helper files are added (547 protected files).

- The existing 12-second helper deadline now includes bounded main-thread work,
  idle callbacks and diagnostics. A queued timed-out callback is cancelled.
  Already-running work cannot safely be cancelled: the helper poisons further
  test actions and subsequent setup/teardown fails explicitly. It cannot turn a
  timeout into a pass. Real sendPointerSync IPC remains intact and may itself
  block. No direct business trigger replaces a real swipe.
- Fixed Log.i markers identify cases C01-C19 and BEGIN/END/ERROR steps with a
  strictly increasing process-wide sequence and relative elapsed milliseconds.
  C05 is the repeated-swipe method; detailed main/idle/pointer/swipe steps are
  accepted only for C05. A CASE END is completion, never a pass assertion.
- A diagnostic-only logcat reader uses the existing owned runtime, private ADB
  endpoint and the same already-verified emulator. It requests only the main
  buffer for the unique UID of the just-installed target APK. Android 13 binary
  output bypasses display-tag filters, so the relay validates each frame before
  retaining only IsolatedUiStep messages with the exact bounded ASCII protocol.
  Other well-formed target tags are discarded in memory, never written to disk.
  The target UID is checked against the complete bounded user-0 package/UID
  inventory, rather than assuming the test APK UID. Kernel logd binary headers
  must match that UID, one positive consistent process ID, the main buffer,
  INFO priority, fixed tag and a fresh guest-clock boundary. UID/PID are backed
  by logd peer credentials; TID and realtime are client-supplied fields, not
  independent kernel attestation. The clock is only a freshness check. PID changes,
  mixed identities, stale/replayed records, gaps, truncation, invalid encoding
  or excessive output are rejected. No UID, PID, absolute timestamp, raw log
  line, stack, environment, ACL text or private path is published.
- The stream starts before instrumentation and shares the original
  600-second instrumentation budget plus the existing 18/20-second supervisor
  cleanup. It has no independent 600-second lifetime or new watchdog. Retention is capped at 2 MiB and 8192 fixed-tag frames. Parsing is capped
  at 8 MiB of source input; exceeding any bound produces invalid diagnostics.
  Further bytes are discarded until existing owned cleanup, not retained. Only after verified owned-process
  termination are stable, no-follow, owned regular files parsed. No post-timeout
  ADB command, log clear, new server, app restart, privilege or timeout extension
  is added. Unsupported/failed collection becomes fixed invalid/missing
  diagnostics. A 660-second guest-clock freshness rejection window is only an
  input validation bound, not additional run time. This new real Android logcat
  path remains device-unverified; mock packet checks do not establish it works.
- progress.json publishes only fixed diagnostic states/cases/steps, optional
  0..600000 relative millisecond values, and mandatory
  `tail_completeness="unverified"`. Android 13 binary stdout may lose buffered
  trailing whole frames during shutdown, even when the retained prefix is valid.
  active_case and last_event_ms describe only the observed prefix, not the state
  at timeout or the actual final step. Truncated frames or sequence gaps are
  invalid, but a missing whole tail cannot be detected. A relay EOF/termination
  race may conservatively produce invalid. No recovery or retry is added. This
  record is never a test-success gate.
  instrumentation.json remains partial-only. The strict original result parser
  and exact 19-case JUnit success gate remain byte-for-byte unchanged.
- Unexpected KVM ACLs now report six fixed boolean difference classes relative
  to each of the original and leased ACLs. Both references require exact keys
  and actual booleans. No raw entries, UID/GID or actor inference is exposed.
  The existing single ACL read, device-identity binding, unknown-state refusal
  and narrowly scoped restore policy are unchanged. Unknown ACLs are not written.
- First test/build failure stays in summary.json. cleanup.json separately keeps
  main/always KVM attempts, owned-runtime termination and evidence-write errors.
  Collection, persistence or cleanup failure cannot replace an earlier timeout.
  Terminal timeout/control/interrupt failures during collector setup are
  rethrown as the first failure; instrumentation is not attempted on that stopped
  runtime. Only non-terminal collection/parse failures are best-effort.

## Local verification and remaining limits

The integrated harness ran 237 local tests: **236 passed, 1 explicitly skipped**.
The skip is the production /proc thread-children enumeration path unavailable in
this local environment. Controlled Python-process fixtures and mocks are not
verification of that missing production path. The independent Java helper check
executes the actual helper and reports 29 checks passed. The earlier component
checks also included 11 Python checks and 70 guarded ACL/evidence fake tests.
These are overlapping verification sets, not device tests or additive UI cases.

The exact final source ZIP below compiled both APKs successfully: exit 0,
6 minutes 34 seconds, all 137 tasks executed, including AndroidTest Kotlin and
Java compilation. Both APK signatures verified with exit 0; all 949 source
inputs were unchanged after the build. This used the hash-verified Gradle 8.11.1
distribution executable directly, not a fresh wrapper download/redirect chain.
A pre-existing local proxy and system Java truststore were selected only for
that process with normal TLS verification. Neither truststore nor host/CI
settings changed. Those local compatibility settings are not packaged.
The new Android logcat/UID/relay integration and all 19 tests on the changed APK
remain unexecuted. No local real KVM permission operation, ADB server, emulator,
remote repository update or new CI/device run is part of this repair.

## Source and build identity

source.zip: **1,818,209 bytes**, SHA-256:

    6e5550afd0ef929622fea6df2a4079f533350071e9c3f685036f3997f5087c51

Canonical source-tree SHA-256 (949 files):

    78438e036a4ab599bb00c3d8063e390298be8f75f29c52fa8cdd9d5aba83c341

The tree digest hashes UTF-8 lines sorted by complete relative POSIX path:
six-digit octal permission mode, space, decimal byte size, space, lowercase
file SHA-256, space, relative path, then LF. File-type bits are excluded from
permission mode. No local build directory, local.properties or machine-specific
network/trust settings are included.

The build uses pinned Gradle 8.11.1, JDK 21, SDK 36 and Build Tools 35.0.0:

    bash gradlew --no-daemon --max-workers=2 --console=plain \
      --no-build-cache --no-configuration-cache --no-scan \
      --dependency-verification=strict -PisolatedUiTests=true \
      -Pandroid.builder.sdkDownload=false \
      -Dorg.gradle.java.installations.auto-download=false \
      -Pkotlin.compiler.execution.strategy=in-process \
      :app:assembleIsolatedUi :app:assembleIsolatedUiAndroidTest

All six official tool URLs/sizes/SHA-256 pins and strict dependency verification
are retained. Existing cache-derived dependency pins are not an independent
cryptographic provenance audit. The seven previously repaired official Maven
POM/module descriptor pins remain unchanged. No dependency checksum is replaced,
no verification is disabled, and no TLS or local proxy workaround is put in CI.
Both newly built APKs must pass package, manifest, signing and runner checks, and
the installed bytes must match the audited APK hashes. Saved old APKs are unused.

## Scope and unchanged safeguards

- Ten DataPage tests use the real DataFragment, filtering/search, refresh,
  paging, view lifecycle and scroll restoration. Nine Refund tests use the real
  bill editor, provisional selection, confirmation, retries and local persistence.
  Synthetic data and the isolated backend are used. This does not test OCR,
  back-tap inference, crash reporting, production startup, physical devices,
  Xposed/LSPosed hooks or real accounts.
- Manual workflow_dispatch only, exact reviewed full commit, attempt 1 and
  explicit confirmation. No automatic retry, push/PR trigger, schedule or matrix.
- Standard ubuntu-24.04 job: 30 minutes. Main step: 26 minutes. Instrumentation:
  600 seconds; boot: 240 seconds; build: 900 seconds. No limits were increased.
- The existing Python preflight checks supervisor capabilities before any KVM
  grant. Build, emulator, private foreground ADB server and clients are owned
  children. Cleanup verifies parentage with waitid on pidfds before signaling
  those same handles. There is no arbitrary PID/name scan or process-group kill.
  The supervisor's bound loopback listener is passed directly to ADB via acceptfd.
- If KVM is already usable, no permission changes occur. When separately
  authorized and necessary, only the current non-root UID on the verified
  /dev/kvm may receive temporary read/write ACL access. The existing mask must
  already allow it. A private receipt is written before the grant. No mask
  expansion, broad chmod, groups, udev, firewall or root emulator is permitted.
  Original/leased/current ACL and device identities are checked before a scoped
  restoration. Unknown changes stop writes. Main and always cleanup both report.
  Forced termination or runner destruction cannot prove ACL readback restoration.
- Free disk floor remains 8,804,682,957 bytes. Only this run's receipt-owned build,
  Gradle and download files can be reclaimed. No preinstalled runner content is
  deleted. Generic ZIP expansion remains 4 GiB, source expansion 150 MiB. Only
  the hash-locked AOSP archive has its exact 19-member / 4,457,578,928-byte budget,
  plus existing free-space reservation and 16 MiB headroom requirements.
- Flat harness bootstrap checks exact hash, size and member list before running
  repository code; embedded and standalone bootstrap are identical. Unexpected,
  duplicate, linked, special, oversized or escaping members are rejected. No
  existing destination can be overwritten. Source gets independent hash and
  safe-extraction checks. New collector/parser tests are in the exact member list.

## Public evidence, licensing and cost

Only up to eight schema-checked synthetic JSON/XML evidence records can leave
the temporary VM through the public job log/summary. The payload cap stays
512 KiB and the summary cap 1 MiB. No raw build/emulator/instrumentation/logcat
logs, databases, APKs, credentials, caches, Actions artifacts, Packages or
releases are uploaded. Successful adb exit is not a test pass. Published success
still requires the exact 19 methods, audited APK identities, sufficient disk,
verified owned-process cleanup, both KVM attempt records, no evidence errors,
and either no KVM change or verified original-ACL restoration.

The source-only publication scope is `origest/AutoAccounting-ui-tests`; the
original private repository is unchanged. LICENSE retains upstream GPLv3 text;
source.zip retains notices. No third-party binary redistribution is certified.
GitHub standard hosted public-repository runner compute is free under its
[Actions billing rules](https://docs.github.com/en/billing/concepts/product-billing/github-actions#examples-of-how-usage-is-measured).
This requests neither paid/larger runners nor billed artifact/cache storage.

## Owner-performed update after review

The earlier GitHub content-write HTTP 403 remains unresolved; this repair does
not retry or bypass it. The repository keeps exactly five files. After this
candidate passes independent review, manually replace these **four** files:

1. source.zip at the repository root.
2. harness.zip at the repository root.
3. README.md at the repository root.
4. isolated-ui.yml under .github/workflows/ (exact name).

LICENSE is byte-for-byte unchanged. Do not add a second differently named
workflow. Read back and verify all five exact file hashes and the complete new
commit. The previous one-attempt authorization is consumed. A new single run
and the same narrow temporary current-UID KVM access, if needed, require fresh
user authorization against that verified commit. Local preparation, compilation
and review are not authorization to publish, run or change real KVM permissions.
