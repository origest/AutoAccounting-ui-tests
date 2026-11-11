# AutoAccounting isolated UI validation

This source-only project builds a dedicated isolated application and runs 19 exact
instrumentation methods on one Android 13 / API 33 x86_64 emulator. It is derived
from [AutoAccounting](https://github.com/AutoAccountingOrg/AutoAccounting).

## Refund fixture and repeated-touch repair

This revision integrates the reviewed refund fixture repair with the public
five-file bundle at commit `558c9fce287a77bd650363e5befda039642edcb3`.
It retains the lifecycle/C05 safeguards described below. Local assembly and
regressions are not a new device pass. No device, emulator, ADB server, Xposed or
CI run was started while preparing this revision. Publication does not authorize
another run.

The latest completed public attempt remains
[42978720484, run #9](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42978720484),
on that baseline commit: **19 complete results, 14 passed and 5 failed**. All ten
DataPage cases, including C05, passed. Refund cases C11, C12, C13, C14 and C19 failed;
C15, C16, C17 and C18 passed. All five failures have UNKNOWN hint, phase and wait;
there was no HELPER_PRIOR_GUARD. C-numbers identify the fixed case list, not execution
order. The original failure stacks are unavailable. The new source is not a
reproduction or proof of the exact five device-side exceptions.

That run also reported `invalid / BINARY_TRUNCATED / binary` progress, with all
observations cleared and tail completeness unverified. Both KVM restoration
attempts refused an unrecognized ACL without writing and did not verify exact
restoration. Neither defect is suppressed or repaired by this revision.

## Exact source scope

The exact reviewed source ZIP contains **953 files**. Against the baseline above,
949 files are byte-identical, four are modified, and none are added or deleted:

- `IsolatedUiApplication.kt`: the already guarded synthetic settings reset now
  explicitly encodes `SETTING_ASSET_MANAGER=true` in its private MMKV store.
- `RefundIsolatedUiTest.kt`: C14 and C18 use the existing
  `screenBounds(onMain { ... })` helper for two repeated real touches.
- `docs/BOUNDARIES.md` and `verification/protected-source.json`: describe and bind
  those exact changes. The protected manifest still covers 553 file identities.

All production source, resources, defaults, backend/transport, dependencies and
build definitions are byte-identical. All 19 method names and every original
assertion remain. C05, its helper lifecycle, all gesture counts, request gates,
wait budgets and teardown guards are unchanged. All 953 members retain their
original order and non-derived ZIP metadata, including all 104 original 0755
entries, timestamps, comments, extra fields, creator fields and attributes.
CRC, changed-file lengths and recompression offsets/sizes are derived fields.
No two-arm probe variant is included.

### Why the synthetic setting is required

The old reset cleared settings without enabling asset management. The unchanged
real getter therefore used the unchanged production default `false`.
`PaymentInfoComponent.configureUIForBillType` hides the payment root in that
state, including the shared refund-picker entry. The five failed cases use that
entry; the four passing cases supply their links directly. This is a confirmed
source-level prerequisite defect consistent with the observed partition. It does
not establish that every observed exception, or all remaining runtime behavior,
has been explained or repaired.

The new value is written only after the existing isolated-package/component
checks and only in the synthetic app-private store. The production default and
visibility checks are untouched. It does not use the synchronizing preference
setter. Manual sync stays true, AI/history/ChatGPT stay disabled, and the synthetic
book still uses the local adapter. Existing `GET assets/list`, `GET assets/get`
and refund-candidate routes remain synthetic and unchanged. Unexpected requests
still fail teardown; no production fallback or new network endpoint is added.

### Why the repeated-touch coordinates change

The two old expressions passed root-view-relative visible rectangles to screen
input. The existing helper adds the root's screen origin and rejects hidden or
empty bounds. C14 now captures the visible retry bounds before the first touch
hides that button; C18 preserves the disabled-but-visible save button as the
second inert touch target. Both view lookups stay inside `onMain`.

The actual new DEX invokes `onMain` and then `screenBounds` at C14 line 135 and
C18 line 218. The real gestures and all counters/assertions remain. A zero root
origin can mask the old coordinate error, so C18's earlier pass is not proof its
second touch landed correctly. These independently found coordinate defects are
not claimed to explain all five earlier failures. Real layout and input dispatch
remain unverified for this new source.

**The README and NOTICE inside the frozen source ZIP contain historical baseline
statements.** Assertions about unchanged synthetic boundaries, earlier test bodies
or old lint warning counts do not describe the present integrated revision. The
scope and current validation here take precedence. Accepted source bytes were not
edited merely to refresh those historical documents.

### Retained owned-task lifecycle

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

### Retained C05 causal and identity checks

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
source size/SHA/canonical tree, refresh exact DEX call-site mappings and their
tests, and update the
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
UNKNOWN sites. The existing unrecognized cancellation error is not added to the hint
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
`924a9da951d7f3d99e573023b764ee41c4a2b3112163a9afb7d3ee150bbab214`,
the final source-built instrumentation APK SHA-256
`63b9a4527f430548d02b6c06b434252d1bd5cda46f0a43059c6c763db84296b8`,
and its classes4.dex SHA-256
`99eecd540b686180f746e2a7c08fec2e29858052a4793497d3fdfb17eea1e0de`.
APK/DEX hashes are evidence anchors, not a requirement that future signed APK
bytes match. The exact archive, all final extracted source files, both APKs and
all their DEX members were read back before generating the new table. No old
full APK or source-hash-only substitution is presented as new mapping evidence.

There are **441 exact expanded paths**, 333 literal rows and 14 actual D8 bridge
pairs, covering all 19 case identities and the six shared lifecycle stages.
The unchanged helper's fixed throw lines are 102 (deadline), 106 (interrupted),
19 (prior guard) and 119 (checked action). Six exact source-file hashes are bound
by parser tests. Every parser function body remains unchanged.

The new table derives literal invokes, positions, synchronous closure allocation
and exact bridges from the compiled DEX. Against the previous table, 315 paths
are unchanged and 126 stale paths are removed/replaced; all 126 removed chains
are rejected. Identical unchanged chains remain valid, so no claim is made that
every old trace is distinguishable. Changed later refund line numbers are also
refreshed, not only the two edited call sites. C05's existing false-idle branch
and all its causal/identity paths remain unchanged.

Complete local enumeration found **480 possible fixed expanded chains**. **39
shorter chains are deliberately excluded** because deleting frames from a longer
same-case chain could imitate them. This includes the new C14/C18 same-line
onMain-only lookups: the full screenBounds chain is recognized, but omission of
its screenBounds frame stays UNKNOWN. Missing-frame tests are not relaxed to
increase hit rate. File-only frames remain allowed only for the exact named
no-position $r8 bridge, paired with its exact D8$$SyntheticClass:0 frame.
Unknown Source and guessed bridge names or lines are never repaired.

Actual ART formatting, inlining and future-build synthetic-name stability are
not device-verified. Unrecognized runtime formatting remains UNKNOWN. Deliberately
excluded ambiguous shorter paths, pointer IPC, activity monitor/startup waits,
ordinary await exhaustion and all unlisted paths remain UNKNOWN. Coverage counts
refer to constructed exact call chains, not Android passes or an expected hit rate.

## Local validation of this revision

- The exact mode-preserving final source ZIP was freshly extracted and built:
  **BUILD SUCCESSFUL in 5 minutes 40 seconds, all 208 tasks executed**. Target and
  instrumentation APK assembly and lint completed. Lint reports **0 errors and
  64 warnings**; warnings are retained, not suppressed or reclassified. Integration
  independently read back those exact final outputs rather than repeating a build
  of identical source. Earlier drafts/builds are not final evidence.
- `:app:testIsolatedUiUnitTest` reports **NO-SOURCE**, not a passing unit suite.
- Exact extracted settings/getter/component JVM contracts: **12 groups passed**;
  exact screen-coordinate helper: **9 groups passed**. Storage, visibility and
  geometry use explicit boundary doubles, not native MMKV or Android views.
  Four mutation negatives (false prerequisite, omitted root origin, ignored
  hidden result and ignored empty bounds) each fail the JVM assertions.
- Actual compiled LocalRefunds/models/Gson and complete BillSelectionLoader:
  **12 groups passed**. Exact DAO SELECT statements: **8 local SQLite checks**.
  These establish local backend/loader/query contracts, not Android Room runtime,
  migrations, transactions or rendered picker behavior.
- Actual deadline-helper JVM regression: **18 groups passed**, including **2,000
  concurrent start-versus-timeout races**. The exact immutable original helper's
  defects are reproduced; Android teardown is explicitly a policy model.
- Exact four-file source/route checks: **9 passed**. C05 source-linked checks:
  **10 passed**. Protected-source verification: **553 identities and all 19
  original method names passed**. No device gesture execution is implied.
- Real final ZIP bootstrap and complete harness suite: **314 tests, 313 passed
  and one existing capability skip**. The skip is native kernel child-process
  enumeration, so that production supervision path remains unverified here.
  A local parent-process guard allows only controlled Python subprocess fixtures
  and local sockets, and recorded no prohibited operation. It is not part of the
  public harness.
- The parser's **86 tests** cover all 441 full paths, helper hints, source pins,
  missing/duplicate/reordered/changed frames, exact bridges, nested/cross-case
  lures, size limits, schema consistency, privacy and unchanged success handling.
  Additional finite-map adversarial checks passed **22,076 assertions**, including
  all 126 removed stale paths and multi-frame deletion ambiguity. Constructed
  traces and DEX inspection are not captured ART-stack tests.
- All 953 final source-file bytes match the accepted archive after its build.
  Both APK signatures and strict package/manifest/runner checks passed. Target
  APK: **43,517,380 bytes**, SHA-256
  `f5fc3cf61e44db8fbc151e68c7c3b7c8fec1e70c268327f1b40119b345f0d0c4`.
  Instrumentation APK: **1,005,427 bytes**, SHA-256
  `63b9a4527f430548d02b6c06b434252d1bd5cda46f0a43059c6c763db84296b8`.
  Both use the same public certificate SHA-256
  `fe88012d81d36765c33e9d8ce9bca8c6b32905107f8cab8531b7f2b6faceac73`.
  Neither APK nor a signing key is included in the publication.

To reproduce the deadline JVM comparison, extract the new ZIP into `source/` and
place the legacy baseline ZIP beside that directory as `source.zip`. Obtain that
legacy input from commit `d0daf017a95c8dfacaafc974ef51df0f89231376` and verify SHA-256
`a0352fcf35b668d1ff1cb41e14b5fe6320dde9054c70f861d2c8029e8e7419df`.
`python3 source/scripts/test-ui-deadline.py` rejects any other baseline. Neither
the current candidate nor the immediately preceding source ZIP is that legacy
input. Run `test-c05-source-contract.py` and `verify-source-boundaries.py` from
that same scripts directory for the included source checks. Additional integration
contracts and their local outputs are outside the source-only five-file layout.

The new source was extracted from the exact frozen ZIP into a separate directory.
Official pinned JDK 21, Gradle 8.11.1, SDK platform 36 and Build Tools 35.0.0 were
reused. Build outputs and project cache were separate from the earlier compile.
The existing dependency-download cache was reused, with strict Gradle dependency
verification, no build cache, no configuration cache, no scan and no SDK or Java
auto-download. No dependency checksum was altered or verification disabled.
Integration also byte-compared all consumed regular files in the pinned JDK,
Gradle, Build Tools and platform archives with their existing extracted toolchains.
Mapping dexlib2/Guava hashes match unchanged strict dependency metadata.
Cache-derived pins are not an independent upstream provenance audit.

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

source.zip: **1,824,328 bytes**, SHA-256:

    924a9da951d7f3d99e573023b764ee41c4a2b3112163a9afb7d3ee150bbab214

Canonical source-tree SHA-256 (953 files):

    b7dc9a3f5846c1d77639e5846eda270ad3e50022e733ea5d0dab32cb6d189e68

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
