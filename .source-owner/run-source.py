#!/usr/bin/env python3
"""No artifacts, accounts, secret env injection, old APKs, or host permission changes."""
import ast, contextlib, hashlib, importlib.util, json, os, pathlib, re, shutil
import stat, subprocess, sys, tempfile, zipfile

SOURCE_SIZE = 13770233
SOURCE_SHA = '1be7c70b5782f5a3d83359ac8e709e87576cc397d60fb629fe9f139cef2e6605'
REFERENCE_BLOBS = {
    'run.py': 'bd5ff2b43848cac6cd5522addc74bd416ffc22b8',
    'OwnerHostFixtureActivity.kt': '96dc39c7c64a8bc3e01a817c241ad1a1155d5099',
    'OwnerHostLifecycleDeviceTest.kt': '1939290b1edcb6824e64aa54ec365befbded96d1',
}
class Blocked(Exception): pass

def stage(name):
    print('STAGE_' + name, flush=True)

def checked_reference(repo, name):
    raw = (repo / '.owner-host' / name).read_bytes()
    digest = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if digest != REFERENCE_BLOBS[name]: raise Blocked('REFERENCE_PIN')
    return raw.decode('utf-8')

def unpack(source, destination):
    raw = source.read_bytes()
    if len(raw) != SOURCE_SIZE or hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise Blocked('SOURCE_PIN')
    seen = set()
    with zipfile.ZipFile(source) as archive:
        if sum(x.file_size for x in archive.infolist()) > 150_000_000: raise Blocked('ARCHIVE_SIZE')
        for info in archive.infolist():
            p = pathlib.PurePosixPath(info.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in info.filename or info.filename in seen:
                raise Blocked('ARCHIVE_PATH')
            if stat.S_ISLNK(info.external_attr >> 16): raise Blocked('ARCHIVE_LINK')
            seen.add(info.filename)
        archive.extractall(destination)

def overlay(src, fixture, test):
    # Fresh extracted source only. Exclude ALL prior debug/androidTest fixtures from this build.
    for part in ('androidTest', 'debug'):
        target = src / 'app/src' / part
        if target.exists(): shutil.rmtree(target)
    p = src / 'app/src/debug/java/net/ankio/auto/testing/OwnerHostFixtureActivity.kt'
    p.parent.mkdir(parents=True); p.write_text(fixture)
    (src / 'app/src/debug/AndroidManifest.xml').write_text(
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application>'
        '<activity android:name="net.ankio.auto.testing.OwnerHostFixtureActivity" android:exported="false" />'
        '</application></manifest>')
    p = src / 'app/src/androidTest/java/net/ankio/auto/service/OwnerHostLifecycleDeviceTest.kt'
    p.parent.mkdir(parents=True); p.write_text(test)

def adapt_runner(original, destination, built):
    # Reuse the reviewed bounded emulator/cleanup/result parser without ANY old payload read.
    tree = ast.parse(original)
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('HERE', 'APK') for t in node.targets))]
    text = ast.unparse(tree)
    text = text.replace("HERE / 'payload' / name", 'BUILT / name')
    if 'payload' in text or '77409046' in text or 'ccff159a' in text:
        raise Blocked('OLD_PAYLOAD_REFERENCE')
    destination.write_text(text)
    spec = importlib.util.spec_from_file_location('source_owner_runner', destination)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.BUILT = built
    module.APK = [(name, (built / name).stat().st_size, hashlib.sha256((built / name).read_bytes()).hexdigest())
                  for name in ('app.apk', 'tests.apk')]
    return module

def execute():
    repo = pathlib.Path(__file__).resolve().parent.parent
    expected = {'GITHUB_REPOSITORY':'origest/AutoAccounting-ui-tests', 'GITHUB_REF':'refs/heads/main',
                'GITHUB_REF_NAME':'main', 'GITHUB_EVENT_NAME':'workflow_dispatch',
                'GITHUB_RUN_ATTEMPT':'1', 'REPOSITORY_PRIVATE':'false'}
    if any(os.environ.get(k) != v for k,v in expected.items()): raise Blocked('SCOPE')
    sha = os.environ.get('EXPECTED_COMMIT','')
    if not re.fullmatch('[0-9a-f]{40}', sha) or sha != os.environ.get('GITHUB_SHA'): raise Blocked('COMMIT')
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip() != sha: raise Blocked('CHECKOUT')
    stage('SCOPE_OK')
    # The child build/emulator must not inherit Actions authentication material.
    for key in list(os.environ):
        if any(word in key.upper() for word in ('TOKEN', 'SECRET', 'PASSWORD', 'CREDENTIAL', 'AUTHORIZATION')):
            os.environ.pop(key, None)
    # Never sudo/chmod/setfacl, create udev rules, or use a discovered physical device.
    if not os.access('/dev/kvm', os.R_OK | os.W_OK): raise Blocked('KVM_ACCESS')
    sdk = pathlib.Path(os.environ.get('ANDROID_SDK_ROOT', os.environ.get('ANDROID_HOME','/missing')))
    java = pathlib.Path(os.environ.get('JAVA_HOME_21_X64','/missing'))
    if not (java/'bin/java').is_file(): raise Blocked('JDK21')
    os.environ['ANDROID_SDK_ROOT'] = str(sdk)
    os.environ['JAVA_HOME'] = str(java)
    os.environ['PATH'] = str(java/'bin') + os.pathsep + os.environ['PATH']
    with tempfile.TemporaryDirectory(prefix='source-owner-',dir=os.environ.get('RUNNER_TEMP')) as tmp:
        root = pathlib.Path(tmp); src = root/'source'; src.mkdir()
        rawlog = root/'raw-build.log'
        def command(argv, timeout, cwd=None, input=None):
            with rawlog.open('ab') as output:
                result = subprocess.run(argv,cwd=cwd,stdin=subprocess.DEVNULL if input is None else None,
                    input=input,stdout=output,stderr=subprocess.STDOUT,timeout=timeout)
                if result.returncode: raise Blocked('COMMAND_FAILED')
        unpack(repo/'.source-owner/public-source.zip',src)
        fixture = checked_reference(repo,'OwnerHostFixtureActivity.kt')
        test = checked_reference(repo,'OwnerHostLifecycleDeviceTest.kt')
        original = checked_reference(repo,'run.py')
        stage('SOURCE_PIN_OK')
        overlay(src,fixture,test)
        wrapper = src/'gradle/wrapper/gradle-wrapper.properties'
        wrapper_text = wrapper.read_text()
        if 'distributionUrl=https\\://services.gradle.org/distributions/gradle-8.11.1-bin.zip' not in wrapper_text:
            raise Blocked('GRADLE_PIN')
        if 'distributionSha256Sum=' in wrapper_text: raise Blocked('GRADLE_PIN')
        wrapper.write_text(wrapper_text + '\ndistributionSha256Sum=f397b287023acdba1e9f6fc5ea72d22dd63669d59ed4a289a29b1a76eee151c6\n')
        licenses = sdk/'licenses'
        def license_snapshot():
            return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in licenses.glob('*') if p.is_file()}
        before = license_snapshot()
        if not before: raise Blocked('SDK_LICENSES_MISSING')
        manager = sdk/'cmdline-tools/latest/bin/sdkmanager'
        if not manager.is_file(): raise Blocked('SDKMANAGER_MISSING')
        # Existing accepted licenses only. "n" is never authorization for new SDK agreements.
        command([str(manager),'--install','platform-tools','emulator','platforms;android-36',
                 'build-tools;35.0.0','system-images;android-34;google_apis;x86_64'],300,input=b'n\n'*20)
        if license_snapshot() != before: raise Blocked('SDK_LICENSES_CHANGED')
        stage('SDK_READY')
        os.environ['GRADLE_USER_HOME'] = str(root/'gradle')
        command(['bash','gradlew','--no-daemon','--console=plain','--max-workers=2',
                 '--no-build-cache','--no-configuration-cache','--no-scan',
                 '-Pandroid.builder.sdkDownload=false','-Dorg.gradle.java.installations.auto-download=false',
                 ':app:assembleDebug',
                 ':app:assembleDebugAndroidTest'],1020,cwd=src)
        stage('BUILD_OK')
        built = root/'built'; built.mkdir()
        for folder,name in [('debug','app.apk'),('androidTest/debug','tests.apk')]:
            files = list((src/'app/build/outputs/apk'/folder).glob('*.apk'))
            if len(files)!=1: raise Blocked('APK_COUNT')
            shutil.copyfile(files[0],built/name)
        runner = adapt_runner(original,root/'runner.py',built)
        stage('BLANK_EMULATOR_START')
        # Suppress even runner-safe diagnostics; expose only fixed final stage and summary.
        with (root/'raw-instrumentation.log').open('w') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            runner.execute()
        stage('OWNER_LIFECYCLE_PASS')

if __name__ == '__main__':
    try:
        execute()
    except Blocked as error:
        allowed = {'REFERENCE_PIN','SOURCE_PIN','ARCHIVE_SIZE','ARCHIVE_PATH','ARCHIVE_LINK',
            'OLD_PAYLOAD_REFERENCE','GRADLE_PIN','SCOPE','COMMIT','CHECKOUT','KVM_ACCESS','JDK21',
            'SDK_LICENSES_MISSING','SDKMANAGER_MISSING','SDK_LICENSES_CHANGED','COMMAND_FAILED','APK_COUNT'}
        code = str(error) if str(error) in allowed else 'PRECONDITION'
        print('SUMMARY_BLOCKED_' + code,flush=True)
        sys.exit(1)
    except BaseException:
        print('SUMMARY_SOURCE_OWNER_NOT_PASSED',flush=True)
        sys.exit(1)
    print('SUMMARY_SOURCE_OWNER_PASSED',flush=True)
