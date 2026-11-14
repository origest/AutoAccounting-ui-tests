package proof.baseline;
public final class SyntheticActivity extends android.app.Activity {
    @Override public void onCreate(android.os.Bundle state) {
        super.onCreate(state);
        android.widget.TextView label = new android.widget.TextView(this);
        label.setText("SYNTHETIC BASELINE ONLY - no real accounting or user data");
        setContentView(label);
    }
}
