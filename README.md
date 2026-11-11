# AutoAccounting isolated UI validation

This source-only project builds a dedicated isolated application and runs 19 exact
instrumentation methods on one Android 13 / API 33 x86_64 emulator. It is derived
from [AutoAccounting](https://github.com/AutoAccountingOrg/AutoAccounting).

## Current harness-only diagnostic candidate

This candidate adds **fixed failure call-site diagnostics for future complete
instrumentation terminals**. It does not change Android source, APK behavior,
assertions, guards, timeouts, cleanup, KVM handling or the strict success gate.
It has not been published or tested on Android. It does not repair or identify
the underlying UI failure, and does not authorize another run.

The frozen public baseline is
`c0246e3d8a4306c73451b62465824c381f6917fb`. The latest completed attempt is
[42944460874](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42944460874/job/130273795850).
Its 295 harness self-tests passed, then all 19 terminal outcomes were observed:
**6 passed, 13 failed**. Execution ordinal 7 was C05,
`actualRepeatedSwipesDoNotDuplicateRowsOrLeaveSpinnerRunning`, with
`HELPER_DEADLINE`. The remaining 12 failures were `HELPER_PRIOR_GUARD`.
Those later terminals do not establish 12 independent application bugs.

That deadline means the shared helper's remaining budget was exhausted or its
timed Future.get expired. It does **not** prove the main thread was continuously
blocked for 12 seconds. An await shares one deadline across its polls and can
expire at the last budget edge even if the final action has completed. The old
terminal stack was private and is not available here. Setup, body, first/second
swipe, await and teardown therefore cannot be reconstructed for that run.

Its progress result was `invalid / BINARY_TRUNCATED / binary`, with observations
cleared and tail completeness `unverified`. This means an incomplete binary frame
was detected, not which producer or transport layer lost data. The unchanged
collector may still produce that result. It is not repaired or relaxed here.
The terminal path below does not depend on usable logcat progress.

Both KVM restoration attempts refused an unrecognized ACL without writing,
reported `restore_verified=false`, and retained a pending receipt. Exact KVM
restoration remains unverified. The new diagnostics do not change that refusal.

## Exact update scope

Only **three repository files** are update candidates:

1. `harness.zip`.
2. `README.md`.
3. `.github/workflows/isolated-ui.yml`, with only the harness SHA-256/size pin changed.

`source.zip` and `LICENSE` are byte-for-byte unchanged. Source remains 950 members,
548 protected files, 19 exact test methods and 72 assertion calls. Harness remains
28 members. Inside it, only four existing members change: `scripts/result_parser.py`,
`scripts/public_evidence.py`, `scripts/test_result_parser.py` and
`scripts/test_diagnostic_evidence.py`. No new archive member, output record,
download, raw-log retention, permission, ADB command or Android dependency is added.

The existing runtime lock, source ZIP/tree pins, all tool pins, bootstrap and
workflow logic are unchanged. The original `parse_output`, `junit_xml` and
`_failure_hint` function bodies are unchanged. Existing instrumentation acceptance,
protocol-invalidity behavior, 2 MiB/16 KiB/16384-line budgets and 19-success gate
remain unchanged. No failing or skipped terminal becomes a pass.

## Fixed terminal call-site fields

Each case in diagnostic `instrumentation.json` retains class, method, state,
execution_ordinal and failure_hint and adds:

- `failure_phase`: fixed lifecycle stage, C05 swipe stage, or a fixed
  `BODY_Cnn_Lnnn` value identifying the selected test method's outer call line.
  For example BODY_C01_L042 is the call at line 42 in C01's frozen source method.
  These are literal reviewed enums, not arbitrary input text or inferred ranges.
- `failure_wait`: `MAIN`, `POLL_MAIN`, `IDLE` or `CLEANUP`, identifying the helper
  caller chain. POLL_MAIN specifically requires the full await chain.
- Failed cases without a complete recognized chain use `UNKNOWN` for both fields.
  All nonfailed states, including skipped, started and unknown, use
  `NOT_APPLICABLE` for both. Prior-guard failures remain UNKNOWN: they do not
  establish a newly attempted wait.

Known sites require one of the unchanged exact first-helper hints
HELPER_DEADLINE, HELPER_INTERRUPTED or HELPER_CHECKED_ACTION. Public validation
checks case, state, hint, phase and wait together, including allowed phase/wait
pairs. A phase from a different case or a partial UNKNOWN/known pair is rejected.
The unchanged successful JUnit XML still contains only the 19 exact success cases;
it is not derived from a site or partial diagnostic.

The parser processes only a legally terminated, matching case bundle. It matches
the **complete ordered first Throwable caller chain**, including fixture methods,
static lambdas, exact D8 bridges, step wrappers and a unique case/lifecycle root.
It does not collect an unordered set of plausible frames. Suppressed exceptions,
Caused by sections, stream prose, other cases and concatenated errors cannot
supply missing call-site evidence. Unrecognized, misplaced, repeated, changed or
omitted relevant frames yield UNKNOWN, or preserve the original invalid protocol.
It never repairs or guesses a missing bridge, source filename or line.
Only the exact primary chain through its root is recognized: additional runner
frames also yield UNKNOWN. Secondary headers, indentation and elisions are
structure-checked without using their call-site content. Enclosed elision counts
cannot exceed the directly enclosing Throwable's complete frame count.

Diagnostic matching additionally requires at most 32 KiB of UTF-8 stack text and
128 primary frames. These stricter call-site-only bounds leave the original
failure hint and protocol budgets unchanged. They reject AndroidX's 65537-character
truncation output even when a cut happens to end on otherwise valid syntax.
No raw stack, error message, path, view text, environment, URL, UID or PID is
published by this projection. Only fixed enums leave the private parser.

This console input is not authenticated. A byte-for-byte fabrication of another
complete accepted chain cannot be distinguished from that chain. The values are
call-site observations, **not proof of main-thread blockage, a business root cause,
execution of all preceding steps, or an independent test-success result**.

## Frozen mapping and coverage limits

Source pin: `a0352fcf35b668d1ff1cb41e14b5fe6320dde9054c70f861d2c8029e8e7419df`.
Mapping evidence reuses the prior local instrumentation build, SHA-256
`ece4440493edfd6af24627dff66dfb132f47bfb4404a4ece0efd3439beaad5e3`, and its
classes4.dex, SHA-256
`af20e4259ddcb46124af08f39ef5508eb6495562a5318fcf93ce849295767974`.
These are evidence anchors, not a promise that a fresh APK's signed bytes match.
No Android rebuild or toolchain download was performed for this candidate.

Exact source invocation sites and existing JVM line tables were checked against
DEX bridge call relationships. The allowlist contains 14 exact D8 bridge pairs.
Each inner $r8$lambda$HASH has its original fixed .kt SourceFile but no positions;
its precise **file-only** token, such as `(IsolatedUiFixture.kt)`, is allowed only
for that named bridge at that exact position. Its paired external synthetic
invoke frame has exact `D8$$SyntheticClass:0`. This is not a wildcard for missing
line numbers. Unknown Source, guessed negative/zero lines on the inner bridge,
unknown hashes, mismatched synthetic numbers and file-only ordinary frames are
not accepted. Simplified JVM chains with the D8 bridges removed are not accepted.

The map has 440 accepted ordered paths across all 19 cases: body calls plus each
case's six shared lifecycle paths. Lifecycle stages are SETUP_RESET, SETUP_IDLE,
TEARDOWN_HOST_FINISH, TEARDOWN_HOST_DESTROYED, TEARDOWN_REQUESTS and TEARDOWN_DATABASE.
C05 includes SWIPE_SHOW, SWIPE_INITIAL_ROWS, SWIPE_FIRST, SWIPE_REQUEST_OBSERVED,
SWIPE_SECOND, SWIPE_FINAL_ROWS and SWIPE_FINAL_ERROR. Initial, observed-request
and final-row awaits remain separate. First and second swipe bounds/idle paths
remain separate. MAIN is not silently interpreted as POLL_MAIN or IDLE.

Thirty-seven valid shorter call paths are deliberately excluded because the same
text could be produced by deleting a frame from a longer same-case path. This is
an extra conservative choice, not a claim that the shorter paths cannot execute.
In particular **C05's initial view lookup within either swipe is UNKNOWN**;
the corresponding screenBounds MAIN and post-gesture IDLE paths remain covered.
Some other direct click lookups are likewise unknown. Pointer IPC, activity
startup/monitor waits, ordinary await-condition exhaustion, action-thread-only
exceptions, and all unlisted paths remain UNKNOWN rather than being mislabeled.

**Actual ART stack formatting and future-build synthetic-name stability have not
been verified.** Bridge renaming, omitted/inlined frames or other runtime differences
can yield UNKNOWN even for a covered source call. No next-run hit rate or UI success
is promised. A separately authorized device run could evaluate that coverage;
this candidate is not a reason to repeat a run blindly.

## Local verification and remaining limits

The local complete harness suite discovered **310 tests: 309 passed, one skipped**.
The skip is the existing native kernel-children enumeration capability test;
that production runtime path was not verified in this container. The original
295-test baseline has the same capability skip locally. Neither skip is described
as an Android pass.

The parser suite has 84 tests. Added checks exercise all 440 accepted paths with
all three supported get-failure hints and both failure codes, field/schema pairs,
all 19 identities, lifecycle/body distinctions, missing/duplicate/reordered frames,
bridge errors, source/file/class/method drift, cross-case tails, suppressed/cause
and stream lures, concatenated errors, partial/malformed terminals, privacy canaries,
32 KiB and official-truncation boundaries, and unchanged success/JUnit/hint bodies.

A short Java model reused the original UiTestDeadline and UiTestFailureRule,
actual JUnit 4.13.2 and the official AndroidX Test Runner 1.6.2 printer/StackTrimmer.
All 440 complete synthetic DEX-chain serializations retained the primary Throwable
and passed the new terminal/schema/privacy projection. Android APIs were explicit
boundary stubs and the stack frames were constructed inputs. These are transport
contract checks, **not captured ART stacks or Android UI test executions**.

The earlier local Android build and the latest remote build concern the unchanged
source, not this new parser's Android coverage. No device, CI, ADB server, emulator,
KVM action, security/permission change or remote write occurred in this integration.
Independent review and exact archive/reference verification are required before
any publication. There is no claim of a final accepted review in this README.

## Unchanged helper, collector and KVM safeguards

The process-wide guard is never reset after a timed-out/interrupted action.
Cancellation of a Future, isDone or isCancelled does not prove a running action
has stopped. Cleanup remains guarded and bounded. The original first-failure rule
preserves the first Throwable through JUnit while later errors remain secondary;
none of these source behaviors is changed here.

Logcat retains only complete exact fixed-tag markers after existing source/frame
validation. Ordinary messages are discarded in memory, not published. Invalid
progress clears observations, and tail completeness remains unverified. Missing
whole tails cannot be inferred from a valid prefix. The same 600-second shared
instrumentation budget, 18/20-second owned cleanup, 2 MiB/8192 retained-frame limit,
8 MiB source parsing and no post-timeout ADB rules remain. No frame reassembly or
collector shutdown behavior is changed to suppress BINARY_TRUNCATED.

The reviewed ACL diagnostic implies, at each latest refusal observation, an
additional mask::rw- over original group::rw- without named entries. That can be
DAC-equivalent at that instant, conditional on the source-constrained projection,
while still failing exact restoration. It does not identify the actor, actual
open result, intermediate state or later permissions. The extra mask is not
added to any restoration allowlist. Unknown ACL changes are refused without
writes; both failed restoration attempts remain failed and their receipt pending.

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

The prior GitHub content-write HTTP 403 is not retried or bypassed here. After
independent review and separate publication authorization, replace only the three
files listed above. Keep source.zip and LICENSE byte-for-byte unchanged, keep the
repository's five-file layout, and do not add another differently named workflow.
Verify exact file hashes, workflow pins and the new full commit after updating.

The earlier one-attempt authorization is consumed. A new single run and the same
narrow temporary current-UID KVM access, if required, need fresh user authorization.
Manual dispatch requires the exact reviewed full commit and
`RUN_ONCE_AFTER_PUBLICATION_REVIEW`. This README does not grant that authorization.
