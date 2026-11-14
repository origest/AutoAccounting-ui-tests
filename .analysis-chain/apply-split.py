"""Reviewed disposable fixture overlay; never modifies production repository."""
import hashlib,pathlib,shutil
def apply(root,here):
    service=root/'server/src/main/java/org/ezbook/server/tools/BillService.kt'
    original=service.read_bytes()
    if hashlib.sha256(original).hexdigest() != 'aa94e3ad709792f5a06c2591717a6ed9ffc107514035478095b3659ad6cbfe6a':raise RuntimeError('OVERLAY_BASE')
    updated=original.decode().replace('private val panelOverride: (suspend () -> Unit)? = null,','private val panelOverride: (suspend () -> Unit)? = null,\n    // Disposable test overlay only; absent from production source/archive.\n    private val fixtureJsResult: (suspend (String, String) -> String)? = null,').replace('suspend fun executeJs(code: String, data: String = ""): String = jsExecutor.run(code, data)','suspend fun executeJs(code: String, data: String = ""): String {\n        fixtureJsResult?.let { synthetic ->\n            check(Server.application.packageName == "net.ankio.auto.analysisfixture")\n            return synthetic(code, data)\n        }\n        return jsExecutor.run(code, data)\n    }')
    if hashlib.sha256(updated.encode()).hexdigest() != 'a8dbb709dc4bcacf125c5df78fad59e44686a13eea8703bf2c36d51f859503cd':raise RuntimeError('OVERLAY_RESULT')
    service.write_text(updated)
    tests=root/'app/src/analysisFixtureAndroidTest/java/net/ankio/auto/testing'
    (tests/'AnalysisCommitWaitDeviceTest.kt').unlink()
    shutil.copyfile(here/'AnalysisPersistenceWithoutJsDeviceTest.kt',tests/'AnalysisPersistenceWithoutJsDeviceTest.kt')
