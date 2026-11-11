# AutoAccounting isolated UI validation

This source-only test project is derived from
[AutoAccounting](https://github.com/AutoAccountingOrg/AutoAccounting). It builds
a dedicated isolated application from reviewed source and runs 19 exact
instrumentation methods on one fresh Android 13 / API 33 x86_64 emulator.

## Current local diagnostic candidate

This candidate has not been published or run on a device. It improves the
information available from a future authorized attempt. It does **not** establish
or fix the cause of the 13 failed cases, the invalid progress record, or the KVM
ACL change. Independent review and fresh authorization against one exact commit
are required before any new run. No automatic retry is added.

The latest completed public attempt was
[42839027012](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42839027012/job/129908916910),
commit `284e4f89c7c7ff23fe7d3cb57a56e75bf08fb9cd`, attempt 1. It built and audited
both APKs, then reported **6 passed and 13 failed**, with instrumentation protocol
`complete`. The primary summary was `instrumentation / ValueError`, **not a
600-second command timeout**. The entire job lasted 377 seconds; this is not a
per-test or instrumentation duration. Its 237 harness tests passed without skips.

The six observed passes were:

- successfulEmptyResponseShowsEmptyNotError
- transportFailureShowsErrorAndActualRetryTapRecovers
- nonSuccessAndMissingDataNeverMasqueradeAsEmpty
- actualTypeFilterAndSearchTextSurviveVisibleRefreshAndReentry
- multiPagePassiveRefreshKeepsLoadedPageCountAndVisibleRowOffset
- activityRecreationRestoresNewFragmentFiltersPagesAndScroll

The other four DataPage cases and all nine Refund cases reported failed terminal
outcomes. Published case rows follow configuration order, **not execution order**.
The first failed row is therefore not evidence of the first executed failure.
There is no published assertion trace, helper failure classification, verified
execution ordinal or per-case duration for that run. Thirteen failed outcomes do
not establish thirteen independent application defects. A pure-JVM example shows
that a shared poisoned helper can produce multiple failures, but does not prove
that explanation occurred on this device.

Its progress record was `invalid`, with all observations cleared and
`tail_completeness="unverified"`. The record had no reason or phase field; its
actual invalidity cause cannot be recovered from that output. The new fields
below cannot reconstruct missing data or be retroactively assigned to this run.
The earlier [42805128904](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42805128904)
at commit `2c6b190539bdc4cf6dd915d19e6a61f0cb92ca21` did reach the 600-second command
timeout with 6 passed, 1 started and 12 unknown. That older incomplete result must
not be substituted for the latest complete-but-failed result.

Owned build/runtime termination was verified on the latest run. Both KVM restore
attempts refused an unknown ACL at `acl_compare / KVM_ACL_CHANGED_EXTERNALLY`,
with `write_attempted=false`, `restore_verified=false` and receipt `pending`.
That is not successful restoration; ending the VM is not ACL readback evidence.

## What changes in this candidate

Only harness diagnostics and their tests change. The repository update consists
of `harness.zip`, this README, and the workflow's harness hash/size pin.
`source.zip` and `LICENSE` remain byte-for-byte unchanged. There are still 28
harness members, 949 source files and 547 protected files. Production UI, all 19
test identities, all 72 assertion calls, existing helper behavior, dependencies,
tool locks, source protection hashes and licenses are unchanged.

### Instrumentation observations

- Each case gains `execution_ordinal`: an integer from 1 through 19 assigned only
  after its valid start bundle, or `null` if no valid start was observed. Ordinals
  are unique and form the observed contiguous start sequence. The output array
  remains in configuration order. Invalid protocol clears every observation,
  including ordinals. This is protocol-observed start order, not independent
  device attestation or identification of a causal first failure.
- Each case gains a closed-vocabulary `failure_hint`. Only a failed terminal
  bundle with an exact allowlisted top-level helper exception header and matching
  first helper frame can receive a `HELPER_*` hint. Uncertain failures,
  helper-looking nested causes and lookalike text are `UNKNOWN`. An exact
  top-level MultipleFailureException header can yield only the type hint
  `MULTIPLE_FAILURES`, never a first-cause inference. JUnit can flatten multiple
  root stacks without that header; such concatenated roots, including two known
  helper stacks, remain `UNKNOWN`. Nonfailed cases use `NOT_APPLICABLE`. These
  are unauthenticated protocol hints, not proof of exception origin. Raw
  messages, frames, paths and stack text are never published.
- The strict original `parse_output` success parser and JUnit generation are
  byte-for-byte unchanged. These partial diagnostics never grant a test pass,
  change a terminal result or relax the exact 19-case success requirement.

### Progress invalidity diagnostics

- `progress.json` gains fixed `reason` and `phase` enums. They distinguish setup,
  cleanup, relay, stable-file, binary-frame, sequence and public-schema failure
  boundaries. The fields identify the rejecting check or operation boundary,
  not the deeper runtime cause. Arbitrary exception text, paths and identifiers
  cannot enter them. Each reason has exactly one allowed phase.
- An invalid record still clears all case times, active case, open steps and
  last-event time. Normal missing/incomplete/observed records use `NONE`/`none`.
  Public `tail_completeness` remains mandatory and always `unverified`.
- The first stream or terminal failure is latched before status persistence, so
  a later status-file write failure cannot overwrite its fixed reason. An
  otherwise unclassified status-write failure has its own fixed reason. The
  private status-file read cap changes from 32 to 80 bytes only to fit these
  allowlisted tokens; no raw text is accepted or retained through that channel.
- Baseline acceptance/rejection and retained logcat bytes remain unchanged in
  the deterministic 11,000-input differential check. Existing target identity,
  binary protocol, sequence, nesting and resource checks are not loosened.

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
ASCII IsolatedUiStep messages. Other well-formed target tags are discarded in
memory. The UID is checked against the complete bounded user-0 package/UID
inventory, rather than assumed to be the test APK UID. Headers must match that
UID, one positive consistent PID, the main buffer, INFO priority, fixed tag and a
fresh guest-clock boundary. UID/PID are backed by logd peer credentials; TID and
realtime are client-supplied, not independent kernel attestation. The clock is
only a freshness check. Mixed identities, PID changes, replay, sequence gaps,
truncation, malformed encoding and excessive output are rejected. No UID, PID,
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

The latest public evidence contains two sets of six boolean ACL differences,
not raw ACL text. **Conditional on the reviewed source's lease validation and
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

The integrated harness discovered **278 local tests: 277 passed and 1 was
explicitly skipped**. The existing skip is the unavailable native thread-children
enumeration path. Controlled Python-process fixtures do not replace verification
of that missing production path. A local test-runner guard allowed only reviewed
Python subprocess fixtures, prohibited real KVM opening and nonlocal connections,
and recorded no prohibited attempt; it is not part of the published harness.

The unchanged baseline passed 236 of 237 tests with the same skip. A component
baseline invocation had one transient mocked child-enumeration test error; an
unchanged repeat passed, and its cause remains unestablished. Failed/preparation
attempts and repeat results are retained in the local verification receipt; no
test expectation or safety check was weakened to obtain a pass.

The actual unchanged Java deadline helper passed **10 pure-JVM contract checks**.
The deterministic progress comparison passed **11,000 synthetic inputs**: 5,000
sequence-parser, 3,000 binary-decoder and 3,000 streaming-filter cases, preserving
baseline acceptance, existing result fields and retained bytes. These checks are
bounded, overlapping regression evidence, not additional Android UI cases or a
proof over every possible input. The strict success-parser/JUnit prefix,
source tree, protection manifest and all source hashes were independently
verified unchanged.

The unchanged source ZIP previously compiled both APKs locally, and the latest
real run built and audited fresh target and instrumentation APKs from that same
source hash. This diagnostic-only revision did **not** repeat APK compilation,
download tools or use old APKs. No new CI/device attempt, ADB server, emulator,
real KVM operation, security-setting change or remote write was performed.
Passing local tests is not a successful real capture, a passing UI suite, or
proof that the next attempt will succeed.

## Source and build identity

source.zip: **1,818,209 bytes**, SHA-256:

    6e5550afd0ef929622fea6df2a4079f533350071e9c3f685036f3997f5087c51

Canonical source-tree SHA-256 (949 files):

    78438e036a4ab599bb00c3d8063e390298be8f75f29c52fa8cdd9d5aba83c341

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
no verification is disabled, and no TLS or local network workaround is added.
Both newly built APKs must pass package, manifest, signing and runner checks;
installed bytes must match audited APK hashes. Saved old APKs are unused.

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
independent review, manually replace only these **three** files:

1. harness.zip at the repository root.
2. README.md at the repository root.
3. isolated-ui.yml under .github/workflows/ (exact name).

Keep `source.zip` and `LICENSE` unchanged. Do not create a second differently
named workflow. Verify all five exact file hashes and the new full commit after
updating. The previous one-attempt authorization is consumed. A new single run
and the same narrow temporary current-UID KVM access, if needed, require fresh
user authorization against that verified commit. Local preparation and review
are not authorization to publish, run or change real KVM permissions.
