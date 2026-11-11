# AutoAccounting isolated UI validation

This source-only project builds a dedicated isolated application and runs 19 exact
instrumentation methods on one Android 13 / API 33 x86_64 emulator. It is derived
from [AutoAccounting](https://github.com/AutoAccountingOrg/AutoAccounting).

## Lifecycle and C05 repair

This revision integrates the independently reviewed local lifecycle/C05 repair
with the public harness at commit
`d0daf017a95c8dfacaafc974ef51df0f89231376`. It changes test code rather than only
adding diagnostics. Local Android assembly and checks do not establish that the
19 device tests pass. No device, emulator, ADB server, Xposed or CI run was started
while preparing this revision. Publication does not authorize another run.

The latest completed public attempt remains
[42953936158](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42953936158):
**6 passed and 13 failed**. Execution ordinal 7 was C05,
`actualRepeatedSwipesDoNotDuplicateRowsOrLeaveSpinnerRunning`, with
`HELPER_DEADLINE`; the remaining 12 failures were `HELPER_PRIOR_GUARD`.
Its failure_phase/failure_wait were UNKNOWN. Those later failures do not establish
12 independent application bugs. The private terminal stack is unavailable, so this repair is not a reproduction of
the exact device-side stall or proof of its business root cause.

That run also reported `invalid / BINARY_TRUNCATED / binary` progress, with all
observations cleared and tail completeness unverified. Both KVM restoration
attempts refused an unrecognized ACL without writing and did not verify exact
restoration. Neither failure is suppressed or repaired by this revision.

## Exact source scope

The source ZIP is the frozen reviewed candidate: 953 files. Compared with the
950-file source at the public baseline, 943 files are byte-identical, seven are
modified and three verification files are added. Production application code,
build definitions and dependencies are unchanged. All 19 test method names and
all 18 non-C05 test bodies are byte-identical. C05's assertions are retained or
strengthened. There are 553 protected file identities.

The executable changes are limited to `UiTestDeadline.java`,
`IsolatedUiFixture.kt`, `DataPageIsolatedUiTest.kt` and `SyntheticUiBackend.kt`.
The other changes update protected identities and boundary descriptions, or add
local regression verification. The backend addition observes the real gate,
request ID and structured coroutine Job; it does not replace transport, Room or
production reload/poll behavior. No two-arm probe variant is included.

**The README and NOTICE inside the frozen source ZIP contain historical baseline
statements.** In particular, claims that all original assertions are byte-identical,
the synthetic boundary is unchanged, or an earlier build had 42 lint warnings do
not describe this revision. The exact scope and current validation below take
precedence. The accepted source bytes have deliberately not been edited merely
to refresh that historical text.

### Actual owned-task lifecycle

Owned tasks use monotonic `QUEUED -> RUNNING -> FINISHED` or
`QUEUED -> CANCELLED_BEFORE_START` transitions. FINISHED is published by the
Callable's actual finally block, never inferred from Future.isDone/isCancelled.
Only cancellation that wins before start prevents the callback from running.
A running task cannot be marked completed or interrupted by cancel(true/false).
Task admission shares the permanent poison lock.

Deadline expiry and interruption still fail the test. A provably unstarted or
finished owned task allows normal teardown; a RUNNING or unknown/foreign task
fails closed and permanently blocks further actions. Queued callbacks cannot
start after poison. The process guard is never reset. Every original host-destroy,
active-request-zero, unexpected-request/database, close/delete and transport
replacement check remains, and any cleanup failure poisons the process.
Callable completion alone is not proof that asynchronous descendants ended.

### C05 causal and identity checks

C05 still injects two real gestures. It now keeps both inserted database IDs,
requires exactly the initial row before refreshing, and checks that the first
gesture caused the synchronous adapter to become empty with the spinner active
and exactly one new active request blocked at its gate. A passive poll cannot
pass that condition merely by increasing a count.

Before and after the second gesture, C05 requires the same active blocked request
ID, empty adapter, active spinner and no error. A replacement reload cancels that
Job synchronously, so it cannot masquerade as the original pending refresh even
before replacement IO begins. Cancelled old-poll tails may increase the diagnostic
counter and are not treated as new active requests.

C05 alone opts out of unrelated global post-gesture idle while the backend gate
is deliberately closed. It waits for specific UI/request state and removal of
relevant child View animations. Other gesture callers keep their default idle
behavior. The gate is released in finally. Final success requires exactly two
rows with exactly the two inserted IDs, visible content, no error and no spinner.

Pointer injection keeps its off-main-thread check, 12-second inter-event budget,
event recycling and CANCEL on an incomplete sequence. Failed CANCEL poisons.
Android's synchronous sendPointerSync call itself is not preemptively timed out;
a platform block inside it remains a device/runtime limitation to investigate.

## Harness integration and privacy

The repository remains exactly five files: `source.zip`, `harness.zip`,
`README.md`, `LICENSE` and `.github/workflows/isolated-ui.yml`. LICENSE is unchanged.
The harness remains its exact original 28-member allowlist. Changes bind the new
source size/SHA/canonical tree, strengthen exact source byte-length checking,
refresh helper and DEX call-site mappings and their tests, and update the
workflow's exact harness hash/size pin. No new tool, dependency, permission,
archive member, output field, raw-log retention or automatic retry is added.

The strict original success parser and JUnit generator are unchanged. Every one
of the 19 exact methods must pass. Failed, skipped, missing, duplicate, unknown
or invalid terminals cannot become a pass. Diagnostics never grant success.

`instrumentation.json` exposes only fixed failure_hint, failure_phase and
failure_wait enums after validating the complete matching terminal bundle.
Known sites require an exact top-level allowlisted helper exception and the
complete ordered source/DEX caller chain. No line ranges, method prefixes,
wildcard bridges, arbitrary frame skipping or inferred missing frames are used.
Changed, omitted, duplicate, cross-case, nested or malformed frames remain
UNKNOWN or preserve the existing protocol rejection. Prior-guard failures have
UNKNOWN sites. The newly introduced cancellation error is not added to the hint
allowlist and remains UNKNOWN.

Primary stack matching is bounded to 32 KiB UTF-8 and 128 frames. Existing
instrumentation budgets remain 2 MiB, 16 KiB per line and 16384 lines. Suppressed
or caused-by content, stream prose and concatenated roots cannot supply missing
primary-chain evidence. No raw exception message, stack, path, URL, view text,
UID, PID or environment value is published. A fabricated exact trace cannot be
distinguished from an authentic one: these are diagnostic observations, not
execution attestation or root-cause conclusions.

## Exact mapping evidence

Mapping is bound to source SHA-256
`c8e9d02ba1e991114777e52d41432d6acbdfd8acf54d0b24f8a84b74565513c3`,
the newly assembled instrumentation APK SHA-256
`db9ddd889862c9e41835ce6474f659365d60d7855db8734dadf8f9fd8d668586`,
and its classes4.dex SHA-256
`9cb76a5ca8fdac65b9443935c47b2a71d8a3bde73dcab55e9c42bad6c5a4b182`.
APK/DEX hashes are evidence anchors, not a requirement that future signed APK
bytes match. No old full APK or old mapping is presented as new-build evidence.

There are **441 exact expanded paths**, 333 literal rows and 14 actual D8 bridge
pairs, covering all 19 case identities and the six shared lifecycle stages.
The helper's fixed throw lines are now 102 (deadline), 106 (interrupted),
19 (prior guard) and 119 (checked action). Six source-file hashes are independently
bound by parser tests. All parser function bodies remain unchanged.

The new gesture default-call frames and actual synthetic names/positions are
checked against the new DEX. C05's first/second post-gesture IDLE paths are removed
because the new false-idle branch cannot execute them. Its second-swipe MAIN and
POLL_MAIN checks and post-second observation at BODY_C05_L171 are represented.
Same-request observation and final ID/row checks remain separate.

Complete local enumeration found 478 possible fixed chains, but **37 shorter
chains are deliberately excluded** because deleting frames from a longer same-case
chain could imitate them. Missing-frame tests still require UNKNOWN; they were
not relaxed to increase hit rate. Initial view lookups within C05 swipes and some
direct click lookups remain conservatively UNKNOWN. File-only frames are allowed
only for each exact named no-position $r8 bridge, paired with its exact
D8$$SyntheticClass:0 frame. Unknown Source and guessed bridge names/lines are
never repaired.

Actual ART formatting, inlining and future-build synthetic-name stability are
not device-verified. Unrecognized runtime formatting remains UNKNOWN. Deliberately
excluded ambiguous shorter paths, pointer IPC, activity monitor/startup waits,
ordinary await exhaustion and all unlisted paths remain UNKNOWN. Coverage counts
refer to constructed exact call chains, not Android passes or an expected hit rate.

## Local validation of this revision

- Real Android target and instrumentation assembly plus lint: **BUILD SUCCESSFUL**
  in 5 minutes 50 seconds, 208 tasks executed. Lint reports **0 errors and 68
  warnings**; the warnings are retained, not suppressed or reclassified.
- `:app:testIsolatedUiUnitTest` reports **NO-SOURCE**, so it is not a passing unit
  test suite. The explicit JVM regression below supplies separate local coverage.
- Actual helper JVM regression: **18 groups passed**, including **2,000 concurrent
  start-versus-timeout races**, running the exact candidate and immutable original
  helper. The original completed-at-deadline and cancelled-running defects are
  reproduced. Android teardown in that test is explicitly a policy model.
- C05 source-linked checks: **10 passed**. They inspect real source relationships,
  not device gesture execution. Protected-source verification: **553 identities
  and all 19 original method names passed**.
- Final ZIP bootstrap and complete harness suite: **313 tests, 312 passed and
  one existing capability skip**. The skip is native kernel child-process
  enumeration, so that production supervision path remains unverified here.
  A local parent-process guard allowed only controlled Python subprocess fixtures,
  rejected device/nonlocal actions and recorded no prohibited attempt. The guard
  is local validation tooling, not part of the public harness.
- The parser's **85 tests** cover all 441 full paths, helper hints, source pins,
  missing/duplicate/reordered/changed frames, exact bridges, nested/cross-case
  lures, size limits, schema consistency, privacy and unchanged success handling.
  Local chain/DEX inspection is not a captured ART-stack test.
- All 953 source-file hashes still match the accepted frozen manifest after the
  build. Target and test package/manifest/signing/vendor-payload audits passed.

To reproduce the JVM comparison, extract the new ZIP into `source/` and place the
original baseline source ZIP beside that directory as `source.zip`. Obtain the
original only from the exact baseline commit above and verify SHA-256
`a0352fcf35b668d1ff1cb41e14b5fe6320dde9054c70f861d2c8029e8e7419df`.
`python3 source/scripts/test-ui-deadline.py` intentionally rejects any other
baseline. The current candidate ZIP must not be substituted for that old input.
Run `test-c05-source-contract.py` and `verify-source-boundaries.py` from the same
scripts directory for the other local source checks.

The new source was extracted from the exact frozen ZIP into a separate directory.
Official pinned JDK 21, Gradle 8.11.1, SDK platform 36 and Build Tools 35.0.0 were
reused. Build outputs and project cache were separate from the earlier compile.
The existing dependency-download cache was reused, with strict Gradle dependency
verification, no build cache, no configuration cache, no scan and no SDK or Java
auto-download. No dependency checksum was altered or verification disabled.
Cache-derived pins are not an independent cryptographic provenance audit.

The complete JDK used only process-local references to the existing system Java
truststore and credential-free environment proxy. TLS and hostname validation
remained enabled; certificates, truststore files and system/network settings were
not changed. These machine-specific settings are not in either public ZIP or
workflow. Platform-tools, emulator and system images were not installed or run.

No APK, signing key, cache, raw build log or local diagnostic file is included in
the five-file publication. Fresh local target and instrumentation APKs are only
verification outputs, not the user's old full application or a distributable
production build. They use the isolated package/runner, synthetic data and an
unexported host, with no requested permissions or production components.
The target is explicitly testOnly; both signatures are valid and use the same
debug certificate. Binary redistribution is outside this publication scope.

## Source and build identity

source.zip: **1,830,422 bytes**, SHA-256:

    c8e9d02ba1e991114777e52d41432d6acbdfd8acf54d0b24f8a84b74565513c3

Canonical source-tree SHA-256 (953 files):

    da083af5ddc7cb19c74369896ed493255071098b9f3788076d52e17493ab94f3

The tree digest hashes UTF-8 lines sorted by complete relative POSIX path:
six-digit octal permission mode, space, decimal byte size, space, lowercase file
SHA-256, space, relative path, then LF. File-type bits are excluded from mode.
No local build directory or machine-specific settings are included.

The workflow build retains:

    bash gradlew --no-daemon --max-workers=2 --console=plain \
      --no-build-cache --no-configuration-cache --no-scan \
      --dependency-verification=strict -PisolatedUiTests=true \
      -Pandroid.builder.sdkDownload=false \
      -Dorg.gradle.java.installations.auto-download=false \
      -Pkotlin.compiler.execution.strategy=in-process \
      :app:assembleIsolatedUi :app:assembleIsolatedUiAndroidTest

All six official tool URLs/sizes/SHA-256 pins, the pinned wrapper and strict
dependency metadata remain unchanged. Before an authorized device run, fresh APKs
must pass package, manifest, signing and runner checks; installed bytes must match
the audited hashes. Old saved APKs are never substituted.

## Unchanged runtime and permission boundaries

- Ten DataPage cases exercise real filtering/search, refresh, paging, lifecycle
  and scroll behavior. Nine Refund cases exercise the real editor, provisional
  selection, confirmation, retry and local persistence with synthetic data.
  This suite does not cover OCR, back-tap inference, crash reporting, production
  startup, physical devices, Xposed/LSPosed hooks or real accounts.
- Manual workflow_dispatch only, exact reviewed full commit, attempt 1 and explicit
  confirmation. No push/PR trigger, schedule, matrix or automatic retry. Standard
  ubuntu-24.04 job: 30 minutes; main step: 26 minutes; instrumentation: 600 seconds;
  boot: 240 seconds; build: 900 seconds. No timeout is increased.
- OwnedRuntime capability checks precede any KVM grant. The build, emulator,
  private foreground ADB server and clients are owned children. Cleanup verifies
  parentage with waitid on pidfds before signaling the same handles. No arbitrary
  PID/name scan or process-group kill is allowed. A bound loopback listener passes
  directly to ADB using acceptfd.
- If KVM is usable, no permission change occurs. When separately authorized and
  necessary, only the current non-root UID on the verified device may receive a
  temporary read/write ACL. The existing mask must already permit it and a
  private receipt precedes the grant. No mask expansion, broad chmod, group,
  udev, firewall or root-emulator changes. Exact ACL and device identities are
  checked before restoration. Unknown changes stop writes. Main and always
  cleanup both report; runner disposal is not restoration evidence.
- The previously inferred extra mask::rw- over group::rw- may preserve access
  decisions at that moment while still failing exact restoration. It identifies
  no actor or open result and is not added to the restoration allowlist.
- Disk floor remains 8,804,682,957 bytes (8.2 GiB). Only receipt-owned build,
  Gradle and download files can be reclaimed. No preinstalled runner content is
  deleted. Generic ZIP expansion stays 4 GiB and source expansion 150 MiB. The
  pinned AOSP archive alone retains its exact 19-member/4,457,578,928-byte budget,
  reservation and 16 MiB headroom.
- Flat bootstrap validates exact harness hash, size and member list before any
  repository code executes. Embedded and standalone bootstrap stay identical.
  Unexpected, duplicate, linked, special, oversized or escaping members and
  existing destinations are rejected. Source has independent exact size, hash
  and safe-extraction checks.
- Logcat retains only complete bounded exact-tag markers. Invalid progress clears
  all observations and tail completeness stays unverified. The shared 600-second
  instrumentation budget, 18/20-second owned cleanup, 2 MiB/8192 retained frames,
  8 MiB source parsing and no post-timeout ADB rule remain. Missing whole tails
  cannot be inferred and BINARY_TRUNCATED is not relaxed.

## Public evidence, licensing and authorization

Only up to eight schema-checked synthetic JSON/XML evidence records can appear
in the public job log/summary. Payload and summary caps remain 512 KiB and 1 MiB.
No raw logs, databases, APKs, credentials, caches, Actions artifacts, Packages or
releases are uploaded. A zero ADB exit is not a test pass. Success requires all
19 exact methods, audited APKs, sufficient disk, verified owned-process cleanup,
both KVM attempt records, no evidence errors, and no KVM change or verified exact
original-ACL restoration.

The public source scope is `origest/AutoAccounting-ui-tests`; the original private
repository is untouched. The archive audit found no stored credentials, private
keys, user bill database/export, personal capture or machine-specific settings.
Generic account-storage code is source code, not an exported account store. Built-in
category/asset/tag JSON contains catalogs, not user balances or transactions.
Pattern checks supplement source/file review; they are not proof that every
possible secret representation can be detected.

LICENSE retains upstream GPLv3 and source notices remain. Existing inconsistent
historical license headers are not silently relicensed. No third-party binary
redistribution clearance is claimed. Standard public-repository GitHub-hosted
runner compute follows [Actions billing rules](https://docs.github.com/en/billing/concepts/product-billing/github-actions#examples-of-how-usage-is-measured);
no paid/larger runner or artifact/cache storage is requested.

Independent final byte/reference review is required before publication. Publish
only the five-file layout and verify the exact resulting full commit, file hashes
and workflow pins. Prior one-attempt authorization is consumed. A new single run,
including narrow temporary current-UID KVM access if needed, requires separate
user authorization. Manual dispatch requires that reviewed full commit and
`RUN_ONCE_AFTER_PUBLICATION_REVIEW`. This document grants no permission to run.
