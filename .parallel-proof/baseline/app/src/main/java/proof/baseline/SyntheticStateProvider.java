package proof.baseline;
import android.content.*;
import android.database.*;
import android.net.Uri;
/** Read-only constants and synthetic sentinel metrics. No command or write API. */
public final class SyntheticStateProvider extends ContentProvider {
    @Override public boolean onCreate() { return true; }
    @Override public Cursor query(Uri uri,String[] projection,String selection,String[] args,String sort) {
        if (!"/state".equals(uri.getPath())) throw new IllegalArgumentException("SYNTHETIC_STATE_ONLY");
        String value=""; int count=0;
        try(Cursor c=SyntheticApplication.database.rawQuery("SELECT value FROM sentinel ORDER BY id",null)) {
            while(c.moveToNext()) { count++; value=c.getString(0); }
        }
        MatrixCursor out = new MatrixCursor(new String[]{"ready","requests","epoch","uid","pid","rows","sentinel"});
        out.addRow(new Object[]{SyntheticApplication.ready?1:0,SyntheticApplication.requests.get(),SyntheticApplication.epoch,
            android.os.Process.myUid(),android.os.Process.myPid(),count,value});
        return out;
    }
    @Override public String getType(Uri uri) { return "vnd.android.cursor.item/synthetic-baseline"; }
    @Override public Uri insert(Uri uri,ContentValues v) { throw new UnsupportedOperationException("READ_ONLY"); }
    @Override public int delete(Uri uri,String s,String[] a) { throw new UnsupportedOperationException("READ_ONLY"); }
    @Override public int update(Uri uri,ContentValues v,String s,String[] a) { throw new UnsupportedOperationException("READ_ONLY"); }
}
