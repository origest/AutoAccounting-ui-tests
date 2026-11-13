# Source-built blank-device lifecycle test

This independently added workflow uses:
- `.github/workflows/source-owner-once.yml`
- `.source-owner/run-source.py`
- `.source-owner/public-source.zip`

Keep existing `.owner-host/run.py` and the two Kotlin fixture files unchanged. They are Git-blob pinned. Do not upload the `reference-*` local review copies or substitute older payload APKs.

Dispatch this NEW workflow on main with the exact final publication commit as `expected_commit`. Both GitHub's SHA and checkout HEAD must match. A repeated attempt fails scope checks; no push trigger exists. Contents read only, no persisted checkout credential, no artifacts or APK publication. Maximum job time 30 minutes. Authentication/token/secret/password/credential environment fields are removed before starting dependency tools or emulator processes. The runtime only uses blank synthetic ledger entries; no user account is logged in.

SDK downloads use official sdkmanager and only already accepted runner licenses (`n` to any new agreement). KVM permissions are checked as-is: no sudo, chmod, udev, group or permission changes. Lack of access is a blocked result. JDK 21 must already be present as JAVA_HOME_21_X64. Network/dependency/native build success remains unverified. The source wrapper is Gradle 8.11.1; no system software configuration is changed.

The runner extracts the pinned audited source into a temporary directory. It replaces ONLY extracted app debug/androidTest source sets with the two reviewed fixtures, builds both packages locally, hashes those newly generated files, and adapts the pinned existing bounded emulator runner to those files. It does not read `.owner-host/payload`. Existing source tree and old workflows are untouched.

All build output goes to a runner temporary file. Existing emulator runner output is redirected to another runner temporary file; its instrumentation parser requires one named passing test and all ten lifecycle stages plus cleanup evidence. Public output contains fixed phase and summary constants only. Nothing uploads logs, APKs, screenshots, databases or caches. Ordinary completion removes the temporary build directory; the original runner owns emulator/adb process-group cleanup. Hard runner termination cannot promise Python cleanup, so this requires an ephemeral GitHub-hosted runner, not self-hosted.

Scope: ordinary API 34 lifecycle, not real Xposed capture, Android 17 OEM background survival, OCR correctness, or proof that the reported 15:27:55 timeout is fixed.

The source archive is reviewed and hash-bound. Nonessential documentation/screenshots and unverified sample transaction resources are excluded. The Gradle distribution is SHA256-pinned; this workflow does not claim full independent dependency-supply-chain verification. The source is a reconstructed integration, not a byte-identical recovery of the previous released APK.
