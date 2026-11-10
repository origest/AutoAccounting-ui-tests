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
inside the temporary VM and are not printed. The five local evidence records
are schema-checked, cross-checked and reconstructed before small synthetic
JSON/XML results are printed and appended to the job summary (at most 1 MiB).
These logs and summaries are public. Failure messages use fixed status codes. Failed builds may additionally expose only a fixed diagnostic category and a bounded integer exit code; no matching log text is published.

Passing requires each exact test method to start and complete once in order,
with no unexpected method, failure, skip, duplicate or missing terminal result.
Successful adb process exit is not a passing suite. A published pass also
requires matching APK identities, sufficient recorded disk space, and either no
KVM permission change or verified restoration.

GitHub's standard hosted public-repository runner compute is free. This workflow
does not request paid/larger runners or billed artifact/cache storage. Public
job logs and step summaries are not artifact-storage usage under GitHub's
[Actions billing rules](https://docs.github.com/en/billing/concepts/product-billing/github-actions#examples-of-how-usage-is-measured).
This is a source-associated UI validation job, not a general-purpose compute service.

## Local repair status

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

The public failure's raw Gradle log is unavailable. This repair fixes a locally
reproduced missing-metadata failure; it does not prove that failure was the
original Actions run's exact cause. The harness now publishes only a fixed
build-failure category and integer exit code when available, never raw log text.

These files were prepared locally only and do not authorize a remote update
or another Actions run. The public file set remains source.zip, harness.zip,
README.md, LICENSE and .github/workflows/isolated-ui.yml. LICENSE is unchanged.
The repository owner must manually replace the workflow and review the resulting
full commit SHA before any separately authorized single manual attempt.
