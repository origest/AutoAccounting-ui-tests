package net.ankio.auto.testing

import android.app.Application
import android.os.Build
import androidx.test.platform.app.InstrumentationRegistry
import io.ktor.application.install
import io.ktor.features.ContentNegotiation
import io.ktor.gson.gson
import io.ktor.routing.routing
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.ezbook.server.Server
import org.ezbook.server.constant.Setting
import org.ezbook.server.db.Db
import org.ezbook.server.db.model.RuleModel
import org.ezbook.server.server.jsRoutes
import org.ezbook.server.tools.BillService
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException
import java.net.ServerSocket
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

/** LOCAL DRAFT, requires disposable BillService test overlay and minimal no-external-service startup.
 * Real Ktor route + injected synthetic rule output (NO JS) + Room; blocked phase is an injected classification wait,
 * not a real AI provider. No accounts, provider requests, real notifications or old APK. */
class AnalysisPersistenceWithoutJsDeviceTest {
    @Test fun insertedBillSurvivesClientTimeoutWithoutReplay() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        fun progress(value: String) {
            check(value in setOf("APP_START", "APP_READY", "SYNTHETIC_RULE_OUTPUT_NO_JS", "ROOM_READY", "RULE_READY", "SERVER_READY", "REQUEST_RECEIVED", "BEFORE_SECOND_CATEGORY", "CLIENT_READ_TIMEOUT", "FINISHED"))
            instrumentation.sendStatus(1, android.os.Bundle().apply { putString("analysisProgress", value) })
        }
        fun clientOutcome(value: String) {
            check(value in setOf("HTTP_2XX", "HTTP_4XX", "HTTP_5XX", "HTTP_OTHER", "READ_TIMEOUT", "IO_OTHER"))
            instrumentation.sendStatus(1, android.os.Bundle().apply { putString("analysisClient", value) })
        }
        progress("APP_START")
        val app = instrumentation.targetContext.applicationContext as Application
        check(app.packageName == "net.ankio.auto.analysisfixture")
        check(Build.HARDWARE in setOf("ranchu", "goldfish"))
        check(InstrumentationRegistry.getArguments().getString("freshAnalysisFixture") == "true")
        check(!app.getDatabasePath("autoAccount.db").exists())
        progress("APP_READY")
        Server.application = app
        Db.init(app)
        val db = Db.get()
        progress("ROOM_READY")
        var service: BillService? = null
        var engine: io.ktor.server.netty.NettyApplicationEngine? = null
        var client: OkHttpClient? = null
        var pool: java.util.concurrent.ExecutorService? = null
        var call: Call? = null
        val entered = CompletableDeferred<Unit>()
        val release = CompletableDeferred<Unit>()
        val finished = CompletableDeferred<Unit>()
        val admissions = AtomicInteger()
        val panels = AtomicInteger()
        val extractionCalls = AtomicInteger()
        val categoryCalls = AtomicInteger()
        try {
        progress("SYNTHETIC_RULE_OUTPUT_NO_JS")
        fun rows(table: String): Int {
            check(table in setOf("BillInfoModel", "AppDataModel"))
            return db.openHelper.readableDatabase.query("SELECT COUNT(*) FROM $table").use {
                check(it.moveToFirst()); it.getInt(0)
            }
        }
        check(rows("BillInfoModel") == 0 && rows("AppDataModel") == 0)
        db.settingDao().set(Setting.FEATURE_AI_AVAILABLE, "false")
        db.settingDao().set(Setting.JS_COMMON, "")
        db.settingDao().set(Setting.JS_CATEGORY, "var category={get:function(){return {book:'默认账本',category:'其他'};}};")
        db.ruleDao().insert(RuleModel().apply {
            this.app = "synthetic.analysis.fixture"
            type = "NOTICE"; creator = "user"; enabled = true
            name = "synthetic-fixed-rule"; systemRuleName = "rule_90001"
            js = "var rule_90001={get:function(data){return {type:'Expend',money:1.25,shopName:'synthetic-only',time:1700000000000};}};"
        })
        progress("RULE_READY")
        val trace = "a".repeat(32)
        val actualService = BillService(analysisProbe = { phase, id ->
            check(id == trace)
            when (phase) {
                "RECEIVED" -> { admissions.incrementAndGet(); progress("REQUEST_RECEIVED") }
                "BEFORE_SECOND_CATEGORY" -> { progress("BEFORE_SECOND_CATEGORY"); entered.complete(Unit); release.await() }
                "FINISHED" -> { progress("FINISHED"); finished.complete(Unit) }
            }
        }, panelOverride = { panels.incrementAndGet(); Unit }, fixtureJsResult = { _, input ->
            // No code evaluation. Validate only known synthetic inputs; never real accounts/AI.
            if (input == "synthetic-one-event") {
                check(extractionCalls.incrementAndGet() == 1)
                """{"type":"Expend","money":1.25,"shopName":"synthetic-only","time":1700000000000,"ruleName":"rule_90001"}"""
            } else {
                val metadata = com.google.gson.Gson().fromJson(input, com.google.gson.JsonObject::class.java)
                check(metadata.get("shopName")?.asString == "synthetic-only")
                categoryCalls.incrementAndGet()
                """{"book":"默认账本","category":"其他"}"""
            }
        })
        service = actualService
        // Reserve intent only; bind race is fail-closed, not a fallback to an existing server.
        val port = ServerSocket(0, 1, java.net.InetAddress.getByName("127.0.0.1")).use { it.localPort }
        val actualEngine = embeddedServer(Netty, host = "127.0.0.1", port = port) {
            install(ContentNegotiation) { gson() }
            routing { jsRoutes(app, actualService) }
        }
        engine = actualEngine
        val actualClient = OkHttpClient.Builder().proxy(java.net.Proxy.NO_PROXY)
            .retryOnConnectionFailure(false).followRedirects(false).followSslRedirects(false)
            .readTimeout(15, TimeUnit.SECONDS).callTimeout(30, TimeUnit.SECONDS).build()
        client = actualClient
        val actualPool = Executors.newSingleThreadExecutor()
        pool = actualPool
            actualEngine.start(wait = false)
            progress("SERVER_READY")
            val request = Request.Builder()
                .url("http://127.0.0.1:$port/js/analysis?type=NOTICE&app=synthetic.analysis.fixture&traceId=$trace")
                .post("synthetic-one-event".toRequestBody("text/plain".toMediaType())).build()
            call = actualClient.newCall(request)
            val activeCall = requireNotNull(call)
            val response = actualPool.submit<Boolean> {
                try { activeCall.execute().use { response ->
                    clientOutcome(when (response.code) { in 200..299 -> "HTTP_2XX"; in 400..499 -> "HTTP_4XX"; in 500..599 -> "HTTP_5XX"; else -> "HTTP_OTHER" })
                    false
                } } catch (error: IOException) {
                    val readTimeout = error is java.net.SocketTimeoutException
                    clientOutcome(if (readTimeout) "READ_TIMEOUT" else "IO_OTHER")
                    readTimeout
                }
            }
            withTimeout(10_000) { entered.await() }
            assertEquals(1, rows("AppDataModel"))
            assertEquals(1, rows("BillInfoModel"))
            val insertedId = db.billInfoDao().highestId()
            val inserted = requireNotNull(db.billInfoDao().queryId(insertedId))
            assertEquals("synthetic-only", inserted.shopName)
            assertEquals(1.25, inserted.money, 0.0)
            assertEquals(1, admissions.get())
            assertTrue("expected injected short-timeout failure", response.get(25, TimeUnit.SECONDS))
            progress("CLIENT_READ_TIMEOUT")
            // Never replay an unknown result. Release only the synthetic classification gate.
            release.complete(Unit)
            withTimeout(10_000) { finished.await() }
            assertEquals(1, admissions.get())
            assertEquals(1, rows("BillInfoModel"))
            assertEquals(1, rows("AppDataModel"))
            val after = requireNotNull(db.billInfoDao().queryId(insertedId))
            assertEquals("synthetic-only", after.shopName)
            assertEquals(1.25, after.money, 0.0)
            assertEquals(insertedId, db.billInfoDao().highestId())
            assertEquals(1, extractionCalls.get())
            assertTrue(categoryCalls.get() >= 1)
            assertTrue(panels.get() in 0..1) // Cancellation timing may prevent later panel work.
            instrumentation.sendStatus(1, android.os.Bundle().apply {
                putString("analysisStage", "PERSISTENCE_NO_JS_POST_INSERT_TIMEOUT_NO_REPLAY")
            })
        } finally {
            release.complete(Unit)
            call?.cancel()
            var firstFailure: Throwable? = null
            fun record(error: Throwable) { if (firstFailure == null) firstFailure = error else firstFailure!!.addSuppressed(error) }
            var engineStopped = engine == null
            try { engine?.stop(0, 5_000); engineStopped = true } catch (error: Throwable) { record(error) }
            var requestFinished = admissions.get() == 0
            try {
                if (!requestFinished) withContext(NonCancellable) { withTimeout(10_000) { finished.await() } }
                requestFinished = true
            } catch (error: Throwable) { record(error) }
            if (engineStopped && requestFinished) {
                try { service?.close() } catch (error: Throwable) { record(error) }
            }
            try { client?.connectionPool?.evictAll(); client?.dispatcher?.executorService?.shutdown() }
            catch (error: Throwable) { record(error) }
            try { pool?.shutdownNow(); check(pool?.awaitTermination(5, TimeUnit.SECONDS) != false) }
            catch (error: Throwable) { record(error) }
            // Room stays app-owned until fresh-emulator process disposal; global log writers may still run.
            // Failure is retained, never converted into a pass or an unsafe DB/native close.
            firstFailure?.let { throw it }
        }
    }
}
