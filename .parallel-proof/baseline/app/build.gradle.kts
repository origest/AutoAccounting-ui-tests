plugins { id("com.android.application") }
android {
    namespace = "proof.baseline"
    compileSdk = 36
    defaultConfig {
        applicationId = "net.ankio.auto"
        minSdk = 29
        targetSdk = 36
        versionCode = 1
        versionName = "SYNTHETIC_BASELINE_ONLY_1"
    }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
}
