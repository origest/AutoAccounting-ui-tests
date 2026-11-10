# AutoAccounting isolated UI validation

This narrowly scoped UI test project is derived from
[AutoAccounting](https://github.com/AutoAccountingOrg/AutoAccounting). It builds
an isolated application from the reviewed public source bundle and runs 19
instrumentation tests on a fresh Android 13 / API 33 x86_64 emulator.

## Scope and status

The reviewed source-only snapshot may be published in
`origest/AutoAccounting-ui-tests`. This does not change the original private
repository. Source and dependency notices are included in source.zip; LICENSE
retains the upstream GPLv3 text. This repository does not distribute APKs or
third-party dependency binaries, and does not certify their redistribution rights.

Local compilation, lint, source review and harness unit tests are separate from
device execution. No device pass is implied by this repository's existence.
Only a workflow result showing all 19 exact methods passing establishes that
run's UI result. Cold-runner disk use and KVM availability are checked at runtime,
not assumed. The original saved APKs are not used or validated by this workflow.

## What the tests exercise

- DataPageIsolatedUiTest: 10 cases using the real DataFragment, view lifecycle,
  filtering, search, refresh, paging and restored scroll position.
- RefundIsolatedUiTest: 9 cases using the real bill editor, refund selection,
  provisional changes, confirmation, retries and local persistence.
- The isolated host and local backend use synthetic data. Unused OCR, back-tap
  and crash reporting boundaries have explicit unavailable test-only adapters.
  The UI code and tested MMKV persistence are retained.

This does not test OCR recognition, back-tap inference, crash reporting,
production startup, physical devices, Xposed/LSPosed hooks or real accounts.
A fresh build and signing certificate are recorded for each run; results do not
apply to previously built APK bytes.

## Published source and build identity

The full reviewed Gradle source is source.zip (1,807,463 bytes), SHA-256:

    3da6abbc130aa41bb7a14ac8e1a09e70c504318b9e74b43f93efeac3b0eb23df

Its canonical source-tree SHA-256 is:

    e4c3c23f36cba353b6fef2249238605f655efd719f15ccd864181d6766693a12

The tree digest hashes UTF-8 lines sorted by complete relative POSIX path:
six-digit octal permission mode, space, decimal byte size, space, lowercase
file SHA-256, space, relative path, then LF.

The root harness.zip contains readable Python scripts, unit tests,
runtime-lock.json and the expected 19-method list. The sole workflow pins its
exact archive hash and size before safely unpacking it. No repository script
runs before the exact dispatch commit and bundle checks. Extraction rejects
path traversal, NUL names, symlinks, unexpected/duplicate members and oversized
expansion, and refuses existing output paths. The source archive gets its own
hash and safe-extraction checks. Old automatic release workflows and Git history
are excluded.

The build uses Gradle 8.11.1, JDK 21, SDK 36 and Build Tools 35.0.0 with the
existing isolated tasks:

    bash gradlew --no-daemon --max-workers=2 --console=plain \
      --no-build-cache --no-configuration-cache --no-scan \
      --dependency-verification=strict -PisolatedUiTests=true \
      -Pandroid.builder.sdkDownload=false \
      -Dorg.gradle.java.installations.auto-download=false \
      -Pkotlin.compiler.execution.strategy=in-process \
      :app:assembleIsolatedUi :app:assembleIsolatedUiAndroidTest

The Gradle distribution and six official JDK/Android tool archives have fixed
URLs, sizes and SHA-256 digests. Dependency verification uses the reviewed
metadata without updating it or disabling verification. The initial hashes came
from the existing build cache, not an independent cryptographic provenance audit.
This repair adds seven missing POM/module descriptors, each checked byte-for-byte
against HTTPS Maven Central bytes and the available checksum sidecar. The
additions are Guava parent POMs 33.2.1-jre, 33.3.1-jre and 33.5.0-android,
JUnit BOM modules 5.9.2 and 5.10.2, and coroutines BOM POMs 1.7.3 and 1.8.0. Two
older Guava POMs have only SHA-1 sidecars; their SHA-256 pins were computed
from the official bytes. The earlier cache-derived hashes are unchanged.

Both APKs must match the dedicated package, manifest, SDK, signing and runner
contracts. The target has only the isolated non-exported host activity and no
permissions. Tests install with explicit test-only support and use
net.ankio.auto.isolated.IsolatedUiTestRunner.

## Execution boundaries

- Only manual workflow_dispatch is enabled, with an exact reviewed commit and
  explicit confirmation. No push, PR, fork, schedule, matrix or automatic retry.
- One standard ubuntu-24.04 job has a 30-minute limit. The main execution step
  has a 26-minute limit, leaving time for restoration and filtered publication.
- KVM is checked first. If access is already available, no permission change is
  made and the result is `not_needed`, not a claim of verified restoration.
- If necessary, the explicitly authorized temporary change adds read/write
  access only for this run's non-root UID on the verified character device
  /dev/kvm. A pre-existing ACL mask must already permit read/write; it is not
  expanded. Only fixed getfacl and sudo/setfacl commands are used, with no shell.
  A private receipt is saved before changing access. Restoring touches only this
  UID's entry and, if originally absent, the added mask. Other entries are not
  rewritten. Device identity, the full expected ACL and the restored ACL are
  checked. Unexpected ACL changes stop restoration rather than overwrite them.
- Normal completion, failure and handled cancellation attempt restoration;
  a separate always-step checks again. Receipt updates are atomic. SIGKILL,
  storage failure or runner destruction cannot guarantee recovery. In those
  cases the temporary hosted VM is disposed of; the workflow must not report
  restoration as verified without its readback check.
- The emulator never runs through sudo/root. No chmod-all, group changes, udev,
  firewall, Magisk, Google account or device network settings are changed.
- Free disk space must remain at least 8,804,682,957 bytes before/throughout the
  build and before the emulator starts. Only this run's newly created,
  receipt-verified build, private Gradle home and download directories may be
  reclaimed. No preinstalled SDK, .NET or other runner content is removed.
- No secrets, new credentials, account access, remote cache or build scan.

## Public results and cost boundary

The workflow creates no Actions artifacts, caches, Packages or releases. APKs,
dependency binaries, databases and full build/emulator/instrumentation logs stay
inside the temporary VM and are not printed. Up to seven local evidence records
are schema-checked, cross-checked and reconstructed before small synthetic
JSON/XML results are printed and appended to the job summary (at most 1 MiB).
These logs and summaries are public. Failure messages use fixed status codes. Failed builds may additionally expose only a fixed diagnostic category and a bounded integer exit code; no matching log text is published.

Passing requires each exact test method to start and complete once in order,
with no unexpected method, failure, skip, duplicate or missing terminal result.
Successful adb process exit is not a passing suite. A published pass also
requires matching APK identities, sufficient recorded disk space, and either no
KVM permission change or verified restoration. A pass additionally requires both
restore-attempt diagnostics, no cleanup/evidence errors, and explicit verified
termination of the owned runtime children. Partial observations never establish a pass.

GitHub's standard hosted public-repository runner compute is free. This workflow
does not request paid/larger runners or billed artifact/cache storage. Public
job logs and step summaries are not artifact-storage usage under GitHub's
[Actions billing rules](https://docs.github.com/en/billing/concepts/product-billing/github-actions#examples-of-how-usage-is-measured).
This is a source-associated UI validation job, not a general-purpose compute service.

## Previous source-build repair

The original metadata omitted seven descriptors encountered during local
fresh-cache build and subsequent lint checks, blocking strict verification. Only 31 lines were
added to gradle/verification-metadata.xml; all other 946 source files, including
all 545 protected Kotlin files and 19 UI tests, remain unchanged. No checksum
or dependency version was replaced, and no verification setting was relaxed.

The repaired source passed both APK assembly tasks using strict verification
and a new build directory with an empty Gradle dependency cache: exit 0 in
398.4 seconds, with all 137 tasks executed. The wrapper entry point ran with
its already hash-verified Gradle distribution preseeded. The distribution
download/redirect chain was not re-tested. Local home/network compatibility
settings differed from GitHub's runner and are not included in this candidate.
The 70 harness unit tests passed. Local lint also passed: 0 errors and 68 warnings.
No emulator or device test was run: **0 of 19 device tests executed**.

The earlier build failure's raw Gradle log is unavailable. This repair fixes a locally
reproduced missing-metadata failure; it does not prove that failure was the
original Actions run's exact cause. The harness now publishes only a fixed
build-failure category and integer exit code when available, never raw log text.

## Previous runtime preparation repair

The subsequent reviewed public attempt,
[42775351202](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42775351202),
built and audited both isolated APKs successfully, then stopped at
`prepare-runtime / ValueError`. Its original KVM ACL was verified restored.
The emulator never started and all 19 device UI cases were **not run**. The public
transcript does not contain a traceback or a more detailed exception message.

A separate local check downloaded only the already-pinned official AOSP 33 image
and verified its complete 694,005,732-byte size and SHA-256. Its 19 members expand
to 4,457,578,928 bytes; system.img alone is 4,306,501,632 bytes. The unchanged
harness deterministically rejected that exact archive at its generic 4 GiB ZIP
expansion limit before extracting any file. This proves a preparation blocker
consistent with the remote summary, rather than supplying the absent CI traceback.

That preparation repair added a narrowly scoped image extractor. It checks the fixed full
archive size and SHA-256 on one no-follow, owned regular-file handle, requires the
exact 19-member name/type/mode/expanded-size contract, and applies only that image's
measured 4,457,578,928-byte expansion budget. Hashing, metadata inspection and
extraction use the same open file. The generic 4 GiB ZIP limit, source-only 150 MiB
limit, path, symlink, duplicate, special-file and no-overwrite safeguards remain.
It did not change a tool version, URL, checksum, source file, KVM rule or UI assertion.

Before image extraction, free space must cover the full image expansion plus the
unchanged 8,804,682,957-byte free-space floor and 16 MiB of filesystem headroom.
Each write checks the reserved free space, and final checks verify free space
and that the opened archive's identity/size/timestamps stayed unchanged.

That preparation candidate passed 85 local unit/mock tests (the previous 70 plus 15 new
positive/negative checks). One local extraction of the full, verified official
image succeeded in 23.569 seconds. All 19 extracted files matched the pinned ZIP's
length and CRC, with 50,269,941,760 bytes of disk space still free afterward.
This only validates safe runtime-file preparation: no emulator was started and
**0 of 19 device UI tests executed** during this repair. No additional APK build,
remote update or Actions run was performed. No runtime binary is in this delivery.

## Cleanup and diagnostic repair candidate

The next reviewed public attempt,
[42781547268](https://github.com/origest/AutoAccounting-ui-tests/actions/runs/42781547268),
ran commit ec88168eab7e30edd7393c9afcca8b7db884170c. Its 85 harness tests passed;
both APK builds/audits and runtime-image preparation completed. The emulator
booted and execution reached instrumentation, where the command hit its unchanged
600-second timeout. No per-case output or JUnit was published: all 19 UI-case
outcomes from that attempt remain **unknown**, not all failed or all unstarted.
Both the main finally and independent always-step reported KVM restoration
unverified. The original internal restore error is not available in public logs,
so this candidate does not claim to identify or fix that run's actual ACL failure.
The job completed on a standard GitHub-hosted Ubuntu VM. GitHub documents automatic
VM decommissioning after a hosted job, but there is no independent destruction
telemetry here, and that lifecycle is not proof of ACL readback restoration.

This local candidate adds diagnostic and cleanup safeguards without changing
source.zip, LICENSE, the 19 UI assertions, tool pins, disk floor or ZIP limits:

- KVM restoration reports fixed phase/reason enums, whether the scoped restore
  command was attempted, whether the original ACL was reliably read back on the
  same device, and whether its receipt was committed. Receipt/evidence failure
  does not erase a successful readback, and cannot turn a failed readback into a
  verified result. Either kind of failure still fails the job. Receipt loading
  additionally rejects duplicate keys, unknown fields, wrong types, links and
  changed file identity. Unknown ACL/device/receipt states still fail closed.
- The first test/build failure stays in summary.json. cleanup.json independently
  retains both KVM attempt results, runtime cleanup and fixed evidence-record
  errors. No cleanup error replaces an earlier instrumentation TimeoutExpired.
  Atomic JSON replacement retains the previous complete record on write failure.
- instrumentation.json reports only the 19 allowlisted class/method identities
  and passed/failed/skipped/started/unknown observations, plus a protocol state.
  The bounded no-follow reader rejects unsafe or unstable files. Invalid input
  yields unknown outcomes; raw messages, stacks, logs and unexpected identities
  are never published. A complete partial protocol is not an alternative pass
  gate: the original strict parser and JUnit pass requirements are unchanged.
- Build, emulator, foreground adb server and adb clients run under dedicated
  Python supervisors. Each supervisor is a new session and a child subreaper;
  it reads only its own kernel children list, verifies kernel parentage using
  waitid on pidfds, then signals that same process handle. There is no name-based
  kill, arbitrary PID-tree scan or process-group signal. Verified cleanup requires
  no remaining kernel children, including adopted descendants. Ownership or
  capability uncertainty fails closed. Cleanup is bounded to 20 seconds.
- A separate Python-only capability preflight runs before any KVM grant or build.
  Missing Linux child-enumeration/pidfd/subreaper primitives stop early. The adb
  server receives a supervisor-owned, already-bound loopback listener via
  acceptfd; its port is never released and rebound. All clients use that explicit
  endpoint and the same pinned adb binary; the emulator receives the same server
  port. No default/global adb server is started or killed.

Business limits are unchanged: 600 seconds for instrumentation, 240 seconds for
boot, 900 seconds for build, 26 minutes for the main step and 30 minutes for the
job. There is no timeout increase, automatic retry or attempt to bypass unknown
ACL checks. New modules/tests are included in the exact bootstrap member list;
the embedded workflow bootstrap and harness hash/size lock are updated together.

Local integrated validation currently comprises 189 tests: 188 passed and one
production-path process-enumeration test is explicitly skipped because this local
execution environment lacks the required /proc thread children interface. Pure
mock negative cases and short controlled Python process tests cover pidfd ownership,
non-child rejection, adopted fixture descendants, signal resistance, interruption,
FD inheritance and endpoint retention. Fixture-based enumeration is not a test of
the unavailable production /proc discovery path. No adb server, emulator, Android
program, real KVM operation, new APK build, remote update or CI run was performed
for this candidate. Real Android/server integration and the full production
process-discovery path remain unverified here. The new preflight may expose a
missing runner capability, rather than proceed unsafely. No next-run success is
promised.

Only the public harness.zip, README.md and .github/workflows/isolated-ui.yml change.
The workflow changes include the exact bootstrap member list and hash/size lock;
its dispatch gate, runner, permissions and timeouts are unchanged. source.zip and
LICENSE remain byte-for-byte identical. No raw log/artifact upload, cache, external
credential, system permission change or automatic repository write is added.

An earlier GitHub content-write attempt returned HTTP 403. This repair does not
retry or work around that denial; publication remains an owner-performed manual
replacement followed by read-only verification.

The prior one-attempt authorization has already been consumed. Do not rerun the
unchanged failed commit. After independent review, the repository owner can
manually replace harness.zip and README.md at the repository root and
isolated-ui.yml under .github/workflows/. All five public files and the complete
resulting commit must then be read back and verified. A new exact-commit manual
attempt and the same narrowly scoped temporary current-UID KVM access, if needed,
require fresh authorization. Local preparation is not authorization to run it.
The public file set remains source.zip, harness.zip, README.md, LICENSE and
.github/workflows/isolated-ui.yml.
