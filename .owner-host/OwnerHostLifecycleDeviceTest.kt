package net.ankio.auto.service

import android.app.Activity
import android.app.ActivityManager
import android.content.Intent
import android.os.Bundle
import android.os.SystemClock
import androidx.test.platform.app.InstrumentationRegistry
import com.google.gson.Gson
import kotlinx.coroutines.runBlocking
import net.ankio.auto.classification.OwnerQueueStore
import net.ankio.auto.constant.WorkMode
import net.ankio.auto.service.host.OwnerHttpRuntime
import net.ankio.auto.utils.PrefManager
import net.ankio.chatgpt.ChatGptAccounts
import okhttp3.OkHttpClient
import okhttp3.Request
import org.ezbook.server.Server
import org.ezbook.server.db.Db
import org.ezbook.server.db.model.BillInfoModel
import org.ezbook.server.server.ownerQueueAuthorization
import org.junit.Assert.*
import org.junit.Test
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.util.concurrent.TimeUnit

/** One-shot on a NEW blank ordinary emulator only. Never enables Xposed/accessibility/notification access. */
class OwnerHostLifecycleDeviceTest {
    private val i = InstrumentationRegistry.getInstrumentation()
    private val app get() = i.targetContext.applicationContext
    private val http = OkHttpClient.Builder().callTimeout(2,TimeUnit.SECONDS).retryOnConnectionFailure(false).build()
    private fun stage(name:String) { i.sendStatus(1,Bundle().apply { putString("ownerHostStage",name) }) }
    private fun waitFor(timeout:Long=20_000, condition:()->Boolean) {
        val until=SystemClock.elapsedRealtime()+timeout
        while (!condition() && SystemClock.elapsedRealtime()<until) SystemClock.sleep(50)
        assertTrue("SAFE_WAIT_TIMEOUT",condition())
    }
    private fun responds():Boolean = runCatching {
        http.newCall(Request.Builder().url("http://127.0.0.1:52045/").build()).execute().use { it.code==200 }
    }.getOrDefault(false)
    private fun ownServiceListed():Boolean = app.getSystemService(ActivityManager::class.java).getRunningServices(100)
        .any { it.service.className==OwnerHostForegroundService::class.java.name && it.foreground }

    /** Test-only read on the runtime executor; no production diagnostics or lifecycle bypass. */
    private fun leaseCount():Int {
        val type=OwnerHttpRuntime::class.java
        val worker=type.getDeclaredField("worker").apply { isAccessible=true }.get(OwnerHttpRuntime) as java.util.concurrent.Executor
        val result=java.util.concurrent.CompletableFuture<Int>()
        worker.execute {
            try {
                val owner=type.getDeclaredField("leases").apply { isAccessible=true }.get(OwnerHttpRuntime)
                val tokens=owner.javaClass.getDeclaredField("leases").apply { isAccessible=true }.get(owner) as Set<*>
                result.complete(tokens.size)
            } catch (error:Throwable) { result.completeExceptionally(error) }
        }
        return result.get(3,TimeUnit.SECONDS)
    }

    @Test fun freshBlankOwnerLifecycleKeepsSyntheticLedger() {
        // No assumptions/skips: a missing prerequisite is a failed safety precondition.
        check(InstrumentationRegistry.getArguments().getString("ownerHostBlankDevice")=="true")
        check(android.os.Build.HARDWARE in setOf("ranchu","goldfish"))
        check(ChatGptAccounts.get(app).view().accounts.isEmpty())
        check(!app.getDatabasePath("autoAccount.db").exists())
        check(!Server.isPortOccupied())
        OwnerQueueStore(app).use { store ->
            for (table in listOf("task","attempt")) store.readableDatabase.rawQuery("SELECT COUNT(*) FROM $table",null).use {
                check(it.moveToFirst() && it.getLong(0)==0L)
            }
        }
        var activity:Activity?=null
        var blocker:ServerSocket?=null
        val ocrLease=Any()
        try {
            stage("FRESH_PRECONDITIONS_OK")
            PrefManager.workMode=WorkMode.Xposed
            activity=i.startActivitySync(Intent().setClassName(app.packageName,"net.ankio.auto.testing.OwnerHostFixtureActivity")
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
            fun start() { i.runOnMainSync { OwnerHostForegroundService.reconcile(activity!!) } }
            start()
            waitFor { OwnerHttpRuntime.status.value=="RUNNING" && ownServiceListed() && responds() }
            stage("FOREGROUND_HTTP_READY")
            check(app.getSystemService(ActivityManager::class.java).getRunningServices(100)
                .none { it.service.className==CoreService::class.java.name })
            val id=runBlocking {
                check(Db.get().billInfoDao().highestId()==0L)
                Db.get().billInfoDao().insert(BillInfoModel(shopName="synthetic-owner-host",money=1.25,time=System.currentTimeMillis()))
            }
            val source=runBlocking { ownerQueueAuthorization().source }
            val bill=runBlocking { Gson().toJson(Db.get().billInfoDao().queryId(id)) }
            val key="$source:$id"
            OwnerQueueStore(app).use { store ->
                store.writableDatabase.execSQL("INSERT INTO attempt(key,sent) VALUES(?,?)",arrayOf<Any>(key,1L))
                store.writableDatabase.execSQL("INSERT INTO task(key,payload,legacy,epoch,state,response,mode,generation) VALUES(?,'',0,0,'UNKNOWN','','Xposed',NULL)",arrayOf(key))
            }
            fun preserved() {
                assertEquals(source,runBlocking { ownerQueueAuthorization().source })
                assertEquals(bill,runBlocking { Gson().toJson(Db.get().billInfoDao().queryId(id)) })
                OwnerQueueStore(app).use { store ->
                    store.readableDatabase.rawQuery("SELECT sent FROM attempt WHERE key=?",arrayOf(key)).use {
                        assertTrue(it.moveToFirst());assertEquals(1L,it.getLong(0));assertFalse(it.moveToNext())
                    }
                    store.readableDatabase.rawQuery("SELECT state,payload,response FROM task WHERE key=?",arrayOf(key)).use {
                        assertTrue(it.moveToFirst());assertEquals("UNKNOWN",it.getString(0))
                        assertEquals("",it.getString(1));assertEquals("",it.getString(2));assertFalse(it.moveToNext())
                    }
                }
            }
            repeat(5) { start() };i.waitForIdleSync();assertTrue(responds());assertEquals(1,leaseCount());preserved()
            stage("DUPLICATE_START_SINGLE_OWNER")
            app.stopService(Intent(app,OwnerHostForegroundService::class.java))
            waitFor { OwnerHttpRuntime.status.value=="STOPPED" && !Server.isPortOccupied() }
            stage("LAST_LEASE_STOPPED")
            blocker=ServerSocket().apply { bind(InetSocketAddress("127.0.0.1",Server.PORT)) }
            start();waitFor { OwnerHttpRuntime.status.value=="WAITING_PORT" }
            stage("FOREIGN_PORT_NOT_READY")
            blocker.close();blocker=null
            waitFor { OwnerHttpRuntime.status.value=="RUNNING" && responds() };preserved()
            stage("BOUNDED_RECOVERY_READY")
            // Exercise actual mode storage + runtime lease (not BackgroundHttpService lifecycle), NOT OCR UI/native recognition.
            OwnerHttpRuntime.acquire(ocrLease)
            check(runBlocking { OwnerHttpRuntime.awaitReady() })
            PrefManager.workMode=WorkMode.Ocr;start()
            waitFor { !ownServiceListed() };check(runBlocking { OwnerHttpRuntime.awaitReady() });preserved()
            stage("OCR_MODE_SHARED_LEASE_PRESERVED")
            PrefManager.workMode=WorkMode.Xposed;start();waitFor { ownServiceListed() && leaseCount()==2 }
            OwnerHttpRuntime.release(ocrLease)
            waitFor { OwnerHttpRuntime.status.value=="RUNNING" && responds() && leaseCount()==1 };preserved()
            stage("XPOSED_MODE_RETURN_PRESERVED")
            val cpu=android.os.Process.getElapsedCpuTime();val pss=android.os.Debug.getPss();val wall=SystemClock.elapsedRealtime()
            SystemClock.sleep(30_000)
            val workers=Thread.getAllStackTraces().keys.count { it.name=="AutoAccounting-owner-http" && it.isAlive }
            assertEquals(1,workers);assertTrue(responds());preserved()
            i.sendStatus(1,Bundle().apply {
                putString("ownerHostMetrics","${SystemClock.elapsedRealtime()-wall}|${android.os.Process.getElapsedCpuTime()-cpu}|$pss|${android.os.Debug.getPss()}|$workers")
            })
            stage("SYNTHETIC_LEDGER_VERIFIED")
        } finally {
            blocker?.close()
            OwnerHttpRuntime.release(ocrLease)
            app.stopService(Intent(app,OwnerHostForegroundService::class.java))
            activity?.let { a -> i.runOnMainSync { a.finish() } }
            val until=SystemClock.elapsedRealtime()+10_000
            while ((Server.isPortOccupied() || ownServiceListed()) && SystemClock.elapsedRealtime()<until) SystemClock.sleep(50)
            val clean = !Server.isPortOccupied() && !ownServiceListed()
            stage(if (clean) "CLEANUP_PORT_FREE" else "CLEANUP_UNKNOWN")
            http.connectionPool.evictAll();http.dispatcher.executorService.shutdown()
            check(clean && leaseCount()==0) { "SAFE_CLEANUP_INCOMPLETE" }
        }
    }
}
