package proof.baseline;
import android.app.Application;
import android.database.sqlite.SQLiteDatabase;
import java.net.*;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
/** Synthetic blank-device fixture, NOT the real legacy app. Stores no real data. */
public final class SyntheticApplication extends Application {
    static final AtomicInteger requests = new AtomicInteger();
    static final String epoch = UUID.randomUUID().toString();
    static volatile boolean ready;
    static SQLiteDatabase database;
    @Override public void onCreate() {
        super.onCreate();
        database = openOrCreateDatabase("synthetic-baseline.db", MODE_PRIVATE, null);
        database.execSQL("CREATE TABLE IF NOT EXISTS sentinel (id INTEGER PRIMARY KEY, value TEXT NOT NULL)");
        database.execSQL("INSERT OR IGNORE INTO sentinel VALUES(1, 'baseline-fixed-synthetic-v1')");
        Thread listener = new Thread(() -> {
            try (ServerSocket server = new ServerSocket()) {
                server.bind(new InetSocketAddress(InetAddress.getByName("127.0.0.1"),52045));
                ready = true;
                while (!Thread.currentThread().isInterrupted()) {
                    try (Socket connection = server.accept()) { requests.incrementAndGet(); }
                }
            } catch (Exception ignored) { ready = false; }
        }, "SyntheticBaselineOldPortGuard");
        listener.setDaemon(true); listener.start();
    }
}
