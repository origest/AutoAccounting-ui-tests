# AutoAccounting isolated UI validation

This source-only test project is derived from
[AutoAccounting](https://github.com/AutoAccountingOrg/AutoAccounting). It builds
a dedicated isolated application from reviewed source and runs 19 exact
instrumentation methods on one fresh Android 13 / API 33 x86_64 emulator.

## Current local diagnostic candidate

This source-only candidate repairs two locally reproduced diagnostic defects:
first-failure reporting through JUnit/AndroidX, and classification of ordinary
Android binary logcat records. It has not been published or run on a device.
The actual initial UI/helper failure, the actual bytes that caused the previous
`BINARY_TAG` result, and the actor or timing of the KVM ACL change remain unknown.
Local diagnostic repair is not proof of a fixed application defect or a passing
UI suite. No automatic retry is added.

The latest completed public attempt was
[42931502732](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42931502732/job/130231114373),
commit `1c621b05534a0b551d9c442a27505efe70957beb`, attempt 1. It built and audited
both APKs, passed all 278 harness tests without skips, then reported **19 complete
terminal outcomes: 6 passed and 13 failed**. The primary summary was
`instrumentation / ValueError`, not a 600-second command timeout. The job lasted
464 seconds; this is not a per-test or instrumentation duration.

Its observed execution ordinals 1 through 6 passed, in this order:

1. nonSuccessAndMissingDataNeverMasqueradeAsEmpty (C03)
2. transportFailureShowsErrorAndActualRetryTapRecovers (C02)
3. successfulEmptyResponseShowsEmptyNotError (C01)
4. actualTypeFilterAndSearchTextSurviveVisibleRefreshAndReentry (C08)
5. activityRecreationRestoresNewFragmentFiltersPagesAndScroll (C10)
6. multiPagePassiveRefreshKeepsLoadedPageCountAndVisibleRowOffset (C09)

Ordinal 7, actualRepeatedSwipesDoNotDuplicateRowsOrLeaveSpinnerRunning (C05),
and ordinals 8 through 19 all failed with `HELPER_PRIOR_GUARD`. C05 was the first
observed failed case, but that hint does not identify its first exception or
prove that its body, swipe, or any particular UI stage ran. The output array is
still in configuration order; execution order comes from the recorded ordinals.
Thirteen failed terminals do not establish thirteen independent application
bugs. The local reproduction below shows distinct first errors can produce
exactly this same state/ordinal/hint projection.

Progress was `invalid / BINARY_TAG / binary`, with all times and observations
cleared and `tail_completeness="unverified"`. That enum identifies a rejecting
boundary. The original failing raw bytes were not published and are unavailable;
no particular empty tag, long tag, truncated message, or malformed target marker
can be attributed to the real run. The candidate cannot recover those bytes or
retroactively recover a case duration or step sequence.

Owned build/runtime termination was verified. Both KVM restoration attempts
refused an unknown ACL at `acl_compare / KVM_ACL_CHANGED_EXTERNALLY`, with
`write_attempted=false`, `restore_verified=false`, and receipt `pending`.
That is not successful exact restoration; ending the VM is not ACL readback
proof. The unchanged KVM interpretation and refusal are detailed below.

Earlier attempts remain historical evidence. Run
[42839027012](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42839027012)
also completed with 6 passes and 13 failures, but did not publish execution
ordinals or fixed failure/progress reasons. Run
[42805128904](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42805128904)
reached the 600-second command timeout with 6 passed, 1 started and 12 unknown.
Neither older result should be substituted for the latest complete result.

## What changes in this candidate

Four repository files change: `source.zip`, `harness.zip`, this README, and the
workflow's harness hash/size pin. `LICENSE` remains byte-for-byte unchanged.
There are **950 source members**, **548 protected files**, and **28 harness
members**. Source changes are limited to the fixture's rule wrapper, a new
`UiTestFailureRule.java`, and the protection manifest's corresponding hashes.
Harness changes are limited to `progress_capture.py`, its existing test file,
and source ZIP/tree identity in `runtime-lock.json`.

Production UI, both test classes, all 19 test identities and 72 assertion calls,
await predicates, `UiTestDeadline`, cleanup and poison behavior, the emitter,
dependencies and tool pins are unchanged. The strict success parser, JUnit
output generator, partial-result hint parser and public schemas are unchanged.
Only the source hash/size/tree binding and harness hash/size workflow pin change
outside the two diagnostic components. No local build adaptation is packaged.

### Preserve the first test failure

The actual JUnit 4.13.2 notifier expands `MultipleFailureException` into separate
failure callbacks. AndroidX Test Runner 1.6.2's `InstrumentationResultPrinter`
reuses the terminal bundle and overwrites its stack on each callback. When the
first timeout or interruption poisons the helper and `@After` subsequently
throws a prior-guard error, the last callback can hide the first exception in
that case's terminal stack. The strict parser cannot recover an error that was
overwritten before it received the bundle.

A pure-JVM reproduction uses the unchanged deadline helper, actual JUnit, and
unmodified relevant AndroidX runner source with explicitly synthetic Android
boundary stubs. Setup timeout, body timeout and body interruption each reproduce
the real run's exact 19-case state/ordinal/hint projection. Setup timeout enters
only six bodies, while body timeout/interruption enter seven. This proves the
public projection is insufficient to choose among these causes; it does not
identify the real trigger.

The fixture now wraps its existing `TestWatcher` with a test-only failure rule.
After the existing before/body/after/watcher sequence has finished, the rule
flattens aggregate failures in their original order, rethrows the first original
Throwable, and preserves later distinct errors as suppressed exceptions. It does
not skip cleanup, clear poison, change cancellation, or turn a failure into a
pass. For suppression-disabled or malformed/empty aggregate edge cases, a fixed
fail-closed wrapper retains errors instead of claiming every Throwable can stay
at the top level. Identity-based cycle/duplicate handling prevents
self-suppression and recursive traversal failure.

For the normal helper cases, the first helper header can now reach the existing
allowlisted top-level hint classifier. Ordinary/uncertain first errors remain
`UNKNOWN`; nested helper-looking secondary errors do not establish a helper
cause. Secondary Throwables remain in memory, but AndroidX `StackTrimmer` can
trim printed trace content. This is not a promise of complete raw secondary
traces, and raw stacks remain unpublished. All original result/strict-pass gates
continue to apply.

Official library references:
[JUnit 4.13.2 notifier](https://github.com/junit-team/junit4/blob/r4.13.2/src/main/java/org/junit/internal/runners/model/EachTestNotifier.java)
and [AndroidX runner 1.6.2 source archive](https://dl.google.com/dl/android/maven2/androidx/test/runner/1.6.2/runner-1.6.2-sources.jar).

### Discard ordinary log records before parsing target bodies

Released Android 13 source permits an empty ordinary tag, tags longer than
128 bytes, and tag bytes that are not strict UTF-8. Its 4068-byte transport cap
can truncate the ordinary message's final NUL, or leave no message bytes after
a complete tag. Binary `logcat -B` output bypasses display-tag filtering, so an
ordinary record can reach the UID stream even with the fixed display filter.
The previous relay applied target-like tag/body constraints before deciding
whether a frame contained the fixed progress tag. This is a confirmed format
compatibility defect, not proof that any particular such frame caused this run.

The relay still acquires exactly one complete bounded frame and validates its
header, UID/PID, main buffer, timestamp and allowed priority before classification.
It finds the first tag NUL within that frame, then compares tag bytes exactly:

- A complete non-target tag causes the whole frame to be discarded in memory.
  Empty/long/non-strict-UTF-8 tags and opaque ordinary bodies are not decoded,
  normalized, repaired, retained, or accepted as progress.
- Missing tag NUL still invalidates the collection. No scan crosses into the
  next frame and no framing recovery or resynchronization is attempted.
- The exact target still requires INFO, the original 160-byte payload envelope,
  final NUL, bounded ASCII tokens, sequence/nesting checks, and unchanged second
  decoding. Prefix/lookalike tags never become target records. Source/time/PID
  checks also apply to discarded noise and maintain stream continuity.

The generic minimum payload changes from four to three bytes to include
priority + empty tag NUL + empty message NUL. The defensive maximum stays 4096;
retention and runtime limits do not increase. Some malformed three-byte inputs
therefore reach a later rejecting validator rather than `BINARY_HEADER`; they
remain invalid. Fixed-tag acceptance and retained bytes are unchanged.

Official fixed Android 13 source references:
[writer](https://android.googlesource.com/platform/system/logging/+/6bfb380b168c7127d79977a0e931d6e5e469d887/liblog/logger_write.cpp),
[4068-byte transport clipping](https://android.googlesource.com/platform/system/logging/+/6bfb380b168c7127d79977a0e931d6e5e469d887/liblog/logd_writer.cpp),
[logd credentials and stored length](https://android.googlesource.com/platform/system/logging/+/6bfb380b168c7127d79977a0e931d6e5e469d887/logd/LogListener.cpp),
[text renderer truncation handling](https://android.googlesource.com/platform/system/logging/+/6bfb380b168c7127d79977a0e931d6e5e469d887/liblog/logprint.cpp),
and [Java/JNI log bridge](https://android.googlesource.com/platform/frameworks/base/+/0d3ff311e6e80dee7fe88a2a2cfa272ce231c3c6/core/jni/android_util_Log.cpp).
These are upstream source facts, not an observation of the failed downstream
image's bytes. No text-renderer repair is copied into target validation.

### Existing diagnostic and success boundaries

Execution ordinals remain protocol-observed start order, not independent device
attestation. Failure hints still require an allowlisted top-level helper header
and matching first frame; uncertain, nested or concatenated-root failures remain
`UNKNOWN`. An exact aggregate header can yield only the `MULTIPLE_FAILURES`
type hint. Hints do not grant a pass or identify a first cause independently.

Progress reasons/phases remain fixed closed enums. The first stream or terminal
error is latched before status persistence. Invalid diagnostics clear all case
times, active case, open steps and last-event time. Ordinary noise alone yields
missing progress, never invented events. Public tail completeness remains
mandatory and `unverified`. The original exact 19-case success parser and JUnit
output remain byte-for-byte unchanged.

## Existing collector and helper boundaries

The unchanged 12-second helper budget includes bounded main-thread work, idle
callbacks and diagnostics. Queued timed-out callbacks are cancelled. An
already-running action may still finish after cancellation; the helper poisons
further test actions, and subsequent setup/teardown fails explicitly. This does
not turn a timeout into a pass. Real sendPointerSync IPC and real swipes remain;
there is no direct business trigger replacing a swipe.

Fixed Log.i markers identify cases C01-C19 and BEGIN/END/ERROR steps with a
strictly increasing process-wide sequence and relative elapsed milliseconds.
Detailed main/idle/pointer/swipe steps are accepted only for C05, the repeated
swipe case. A CASE END records completion, not a passing assertion.

The diagnostic-only logcat reader uses the existing owned runtime, private ADB
endpoint and same verified emulator. It requests only the main buffer for the
unique UID of the just-installed target APK. Android 13 binary output bypasses
display-tag filters; the relay checks frames before retaining only exact bounded
ASCII IsolatedUiStep messages. Frames with complete non-target tags are discarded in memory after the
source/frame checks described above. The UID is checked against the complete bounded user-0 package/UID
inventory, rather than assumed to be the test APK UID. Every frame must match that UID, one positive consistent PID, the main buffer
and a fresh guest-clock boundary. Only retained progress markers additionally
require INFO priority and the exact fixed tag. UID/PID are backed by logd peer credentials; TID and
realtime are client-supplied, not independent kernel attestation. The clock is
only a freshness check. Mixed identities, PID changes, replay, sequence gaps,
truncated frames, malformed target encoding and excessive output are rejected. No UID, PID,
absolute timestamp, raw line, stack, environment, ACL text or private path is
published.

The stream starts before instrumentation and shares its original 600-second
budget plus the existing 18/20-second supervisor cleanup. It has no independent
600-second lifetime or new watchdog. Retention remains capped at 2 MiB and 8192
fixed-tag frames; source parsing remains capped at 8 MiB. Excess bytes are
discarded until existing owned cleanup, not retained. Only after verified
owned-process termination are stable, no-follow, owned regular files parsed.
There is no post-timeout ADB command, log clear, new server, app restart, new
privilege or timeout extension. The 660-second guest-clock freshness rejection
window is only an input validation bound, not additional runtime.

Binary stdout can lose whole trailing frames during shutdown even if the prefix
is valid. `active_case` and `last_event_ms` describe only the observed prefix,
not the actual final state. Truncated frames and sequence gaps are rejected, but
missing whole tails are not detectable. EOF/termination races may conservatively
produce invalid diagnostics. No recovery or retry is added. The real collector
path has not produced verified progress evidence; this candidate remains
device-unverified. Mock packet checks do not establish successful real capture.

First test/build failure remains in `summary.json`; cleanup and evidence-write
failures are recorded separately. Collector setup timeout/control/interrupt
failures preserve the original exception and prevent instrumentation from
starting on the stopped runtime. Only nonterminal diagnostic failures are
best-effort. Collection and cleanup failures cannot replace an earlier failure.

## KVM mask interpretation and unchanged refusal

Each of the latest main and always cleanup observations contains two sets of
six boolean ACL differences, not raw ACL text. **Conditional on the reviewed source's lease validation and
correct public projection**, each refusal observation implies that the original
ACL had no mask and no named entries, with owning-group permissions `rw-`; the
current ACL lacks the temporary current-UID named entry and differs from the
original only by an additional `mask::rw-`.

At each observed device identity and fixed credentials, that structure has the
same ACL discretionary-access decisions as the original: owning-group `rw-`
intersected with mask `rw-` is unchanged. This is a source-constrained deduction,
not a raw-ACL observation or proof that the current process could not open KVM.
It does not identify an actor, time of change, intermediate state, external open
file descriptor, other access mechanism or later permissions.

The extra mask is still a structural difference, so exact restoration is false.
A mask can affect later chmod or setfacl behavior even when current DAC decisions
are equal. In general, removing a mask can expand group permissions, and named
entries require a mask. No general mask-removal authorization follows from this
example. See [acl(5)](https://man7.org/linux/man-pages/man5/acl.5.html) and
[setfacl(1)](https://man7.org/linux/man-pages/man1/setfacl.1.html).

This candidate does not change `kvm_access.py`, its public ACL schema, restore
commands or allowed-write states. Unknown ACLs are still refused without writes;
the inferred structure is **not** added to the restore allowlist. Both failed
attempts remain failed, and the receipt remains pending.

## Local verification and remaining limits

The integrated harness discovered **295 local tests: 294 passed and one was
explicitly skipped**. The unchanged baseline discovered 278: 277 passed with the
same native thread-children enumeration skip. Controlled Python-process fixtures
do not verify that unavailable production enumeration path. A local runner guard
permitted only reviewed Python fixture subprocesses, prohibited real KVM opening
and nonlocal connections, and recorded zero prohibited attempts. This test-only
guard is not included in the package.

The failure rule passed 10 unchanged deadline contract checks, seven synthetic
actual-library lifecycle scenarios, 24 aggregate/error edge checks, and seven
original-parser/public-schema/strict-gate projection checks. Independent review
repeated these component checks. These are JVM mechanisms with Android boundary
stubs, not Android UI executions. The actual Kotlin fixture was checked by the separate
Android compilation described below.

The integrated deterministic comparison used **17,000 synthetic inputs**:
3,000 sequence-parser inputs and 14,000 binary inputs each tested through both
decoders and both stream filters. Counts overlap, not 31,000 independent inputs.
All parser and decoder results were identical. The candidate filter matched an
independently written source/frame oracle on all binary inputs; 11,195 stream
results were identical and 2,805 differences were confined to ordinary tag/body
classification and the three-byte minimum. A 5,000-input target/source/framing
subset preserved acceptance and retained bytes; 41 malformed three-byte inputs
changed only the rejection boundary. Within those binary inputs, 2,000
ordinary-noise projections retained exactly the original two target markers. No new target frame was
accepted. These are bounded regression checks, not proof over all possible inputs.

Source members, protection hashes, both unchanged test classes, their 19 methods
and 72 assertions, helper and production source were checked against the exact
previous archive. The integrated ZIP/tree/lock/workflow chain was checked, with
only the listed source and harness changes. The 28-member allowlist and embedded
bootstrap are unchanged. No repository test expectation, strict-success rule, cleanup check,
source-identity check, or runtime budget was changed to obtain a pass.

The frozen new source compiled **both APKs successfully** in a separate local
build using the command below with strict dependency verification: exit 0,
373.9 seconds, 137 Gradle tasks executed. All 950 source members' modes, sizes
and hashes and the input ZIP remained unchanged; the 548 protection hashes and
19-method list were rechecked after building. No saved old APK was used.

Fresh local APK identities (verification only; APKs are not packaged or uploaded):

- Target: 43,517,344 bytes, SHA-256
  `2425768f4926f2af615694ddf69fc49fa9511ce586157545ab970c49e90adf13`.
- Instrumentation: 988,343 bytes, SHA-256
  `ece4440493edfd6af24627dff66dfb132f47bfb4404a4ece0efd3439beaad5e3`.

Both passed archive integrity, exact package/manifest/component/runner checks,
excluded-vendor-payload checks and `apksigner verify`; their signer certificates
matched. Neither requests permissions or contains production components under
the existing audit. No Gradle Java process remained after this local build.

The local build used isolated tool/home/cache directories and process-only
settings for the existing system truststore and a credential-free network proxy.
TLS/hostname checks and strict dependency verification remained enabled; the
system truststore and source files were not changed. These settings, tools,
APKs, local keys and raw logs are outside all delivery packages. The deliberately
minimal local tool set had no platform-tools; its warning did not block the
build, and no ADB was installed or run.

The separate local build wrapper had a 1200-second wait cap; the build finished
in 373.9 seconds, within the unchanged production 900-second build budget. It
did not exercise the production owned-runtime supervisor, its timeout path, or
device cleanup. The repository's 600/240/900/26/30 limits are unchanged. Local
compilation and APK audit do not verify instrumentation on Android.

No new CI/device attempt, ADB server, emulator, real KVM operation, security or
permission change, or remote write was performed for this candidate. Passing
local tests and compiling APKs are not a successful real capture, a passing UI
suite, or proof that the next attempt will succeed. The real first UI/helper
failure and real progress-invalidity trigger remain unresolved.

## Source and build identity

source.zip: **1,813,023 bytes**, SHA-256:

    a0352fcf35b668d1ff1cb41e14b5fe6320dde9054c70f861d2c8029e8e7419df

Canonical source-tree SHA-256 (950 files):

    597ffa2ac55f7772be3b6e9634a1a1f8f9d7ccae83d65760775add0432729d66

The tree digest hashes UTF-8 lines sorted by complete relative POSIX path:
six-digit octal permission mode, space, decimal byte size, space, lowercase
file SHA-256, space, relative path, then LF. File-type bits are excluded from
permission mode. No local build directory or machine-specific settings are
included.

The build uses pinned Gradle 8.11.1, JDK 21, SDK 36 and Build Tools 35.0.0:

    bash gradlew --no-daemon --max-workers=2 --console=plain \
      --no-build-cache --no-configuration-cache --no-scan \
      --dependency-verification=strict -PisolatedUiTests=true \
      -Pandroid.builder.sdkDownload=false \
      -Dorg.gradle.java.installations.auto-download=false \
      -Pkotlin.compiler.execution.strategy=in-process \
      :app:assembleIsolatedUi :app:assembleIsolatedUiAndroidTest

All six official tool URLs/sizes/SHA-256 pins and strict dependency verification
remain unchanged. Existing cache-derived dependency pins are not an independent
cryptographic provenance audit. The seven previously repaired official Maven
POM/module descriptor pins remain unchanged. No dependency checksum is replaced,
no verification is disabled, and no machine-specific TLS, truststore, proxy or
network configuration is included in the repository.
Before a separately authorized device run, both newly built APKs must pass
package, manifest, signing and runner checks; installed bytes must match audited
APK hashes. Saved old APKs are unused.

## Scope and unchanged safeguards

- Ten DataPage tests use the real DataFragment, filtering/search, refresh,
  paging, view lifecycle and scroll restoration. Nine Refund tests use the real
  bill editor, provisional selection, confirmation, retries and local persistence.
  Synthetic data and an isolated backend are used. This does not test OCR,
  back-tap inference, crash reporting, production startup, physical devices,
  Xposed/LSPosed hooks or real accounts.
- Manual workflow_dispatch only, exact reviewed full commit, attempt 1 and
  explicit confirmation. No push/PR trigger, schedule, matrix or automatic retry.
- Standard ubuntu-24.04 job: 30 minutes. Main step: 26 minutes. Instrumentation:
  600 seconds; boot: 240 seconds; build: 900 seconds. No limit is increased.
- Supervisor capability checks precede any KVM grant. Build, emulator, private
  foreground ADB server and clients are owned children. Cleanup verifies
  parentage with waitid on pidfds before signaling those same handles. There is
  no arbitrary PID/name scan or process-group kill. A bound loopback listener
  passes directly to ADB using acceptfd.
- If KVM is already usable, no permission changes occur. When separately
  authorized and necessary, only the current non-root UID on the verified KVM
  device may receive temporary read/write ACL access. The existing mask must
  already allow it. A private receipt precedes the grant. No mask expansion,
  broad chmod, groups, udev, firewall or root emulator is permitted. Exact ACL
  and device identities are checked before scoped restoration. Unknown changes
  stop writes. Main and always cleanup both report; runner disposal is not
  proof of restoration.
- Free disk floor remains 8,804,682,957 bytes (8.2 GiB). Only this run's
  receipt-owned build, Gradle and download files can be reclaimed. No preinstalled
  runner content is deleted. Generic ZIP expansion remains 4 GiB, source
  expansion 150 MiB. Only the hash-locked AOSP archive has its exact 19-member /
  4,457,578,928-byte budget, existing reservation and 16 MiB headroom.
- Flat bootstrap checks exact harness hash, size and member list before running
  repository code. Embedded and standalone bootstrap are identical. Unexpected,
  duplicate, linked, special, oversized or escaping members are rejected. No
  existing destination can be overwritten. Source has independent hash and
  safe-extraction checks. The exact harness allowlist stays at 28 members.

## Public evidence, licensing and cost

Only up to eight schema-checked synthetic JSON/XML evidence records can leave
the temporary VM through the public job log/summary. Payload and summary caps
remain 512 KiB and 1 MiB. No raw build/emulator/instrumentation/logcat logs,
databases, APKs, credentials, caches, Actions artifacts, Packages or releases are
uploaded. Successful ADB exit is not a test pass. Published success requires all
19 exact methods, audited APKs, sufficient disk, verified owned-process cleanup,
both KVM attempt records, no evidence errors, and either no KVM change or
verified original-ACL restoration.

The source-only publication scope is `origest/AutoAccounting-ui-tests`; the
original private repository is unchanged. LICENSE retains upstream GPLv3 text;
source.zip retains notices. No third-party binary redistribution is certified.
Standard GitHub-hosted public-repository runner compute is free under its
[Actions billing rules](https://docs.github.com/en/billing/concepts/product-billing/github-actions#examples-of-how-usage-is-measured).
This requests no paid/larger runner or billed artifact/cache storage.

## Owner-performed update after review

The earlier GitHub content-write HTTP 403 remains unresolved; this candidate
does not retry or bypass it. The repository keeps exactly five files. After
independent review, manually replace these **four** files:

1. source.zip at the repository root.
2. harness.zip at the repository root.
3. README.md at the repository root.
4. isolated-ui.yml under .github/workflows/ (exact name).

Keep `LICENSE` unchanged. The four-file update ZIP contains precisely these four
relative paths; the complete five-file package additionally contains LICENSE.
Neither package includes APKs, build adaptations, raw logs, or private review
notes. Do not create a second differently named workflow. Verify all five exact
file hashes and the new full commit after updating.

The previous one-attempt authorization is consumed. A new single run and the
same narrow temporary current-UID KVM access, if needed, require fresh user
authorization against that verified commit. Local preparation, build and review
are not authorization to upload to Space, publish, run CI/device tests or change
real KVM permissions. Independent review must finish before any such request.
