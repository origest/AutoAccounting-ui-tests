# LOCAL PREPARATION: synthetic dual-app isolation proof

Not published or run. A new concrete approval is required before any temporary KVM ACL grant or cloud workflow execution.

This test uses a **synthetic baseline substitute** under net.ankio.auto, not the previously shipped application. The counterpart is a deliberately minimized synthetic-only net.ankio.auto.paralleltest build. It has no normal payment-capture UI or real accounts.

Inputs are pinned in reviewed-inputs.json. Publish only the explicit PUBLIC-FILES.json allowlist, mapping parallel-proof-once.yml to .github/workflows/parallel-proof-once.yml and all other listed inputs under .parallel-proof/. Never publish local build outputs, logs, SDK/cache folders, signing keys or APKs.

The manual workflow pins the exact main commit, uses a standard Ubuntu runner and read-only repository permission. It builds both APKs and instrumentation from source, starts a new private AVD/ADB server, installs only onto that verified initially blank emulator, and demands exactly one named passing test and all six required milestones. No artifacts or releases are uploaded.

The synthetic baseline seeds one SQLite sentinel and a read-only provider. A listener on 52045 counts accepted TCP connections. The test checks zero counter readings during its observation window, unchanged baseline process/UID/sentinel, distinct app UID/data directories, and parallel ledger reads/mutations via 52145. This is **not proof of all possible zero accesses**, adversarial network isolation, real old APK compatibility, real Xposed hooks, OEM notification capture, or the reported timeout fix.

Only reviewed stage enum names and fixed diagnostic labels are printed. Raw output remains in temporary files and is not uploaded. Parser negative tests reject missing/extra/out-of-order stages, duplicate/missing terminal result, wrong/extra/ignored tests and failures. Owned emulator/ADB process groups and guest directory must be cleaned before success. Temporary KVM access is current runner user only, with exit restoration and always-step byte comparison; no global permission or persistent udev rule.

Read-only preflight validates repository/ref/event/attempt/exact checkout and all reviewed input hashes before saving or modifying ACL; execute repeats validation. ACL command failures emit fixed error codes only.

Local checks: 20 Python contract tests passed; Python compilation and bash syntax passed. No cloud test was dispatched from this preparation.
