package net.ankio.auto.testing
/** Debug-only visible fixture, no onboarding, account login, OCR or permission requests. */
class OwnerHostFixtureActivity : android.app.Activity() {
    override fun onCreate(state: android.os.Bundle?) {
        super.onCreate(state)
        setContentView(android.widget.TextView(this).apply { text = "Blank-device host lifecycle fixture" })
    }
}
