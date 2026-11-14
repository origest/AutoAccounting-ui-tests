#!/usr/bin/env python3
"""Reviewed synthetic-only proof. Not an old shipped APK compatibility test."""
import hashlib, importlib.util, json, os, pathlib, re, shutil, stat, subprocess, sys, tempfile, zipfile

class Blocked(Exception): pass

def stage(name): print('STAGE_'+name,flush=True)

def read_reviewed_inputs(here):
    manifest=json.loads((here/'reviewed-inputs.json').read_text())
    if manifest.get('review_ready') is not True:raise Blocked('INPUT_REVIEW_PENDING')
    if manifest.get('scope')!='synthetic-baseline-substitute-only':raise Blocked('INPUT_SCOPE')
    files=manifest.get('files',{})
    expected={'parallel-source.zip','run-emulator.py','baseline/build.gradle.kts','baseline/settings.gradle.kts',
        'baseline/app/build.gradle.kts','baseline/app/src/main/AndroidManifest.xml',
        'baseline/app/src/main/java/proof/baseline/SyntheticApplication.java',
        'baseline/app/src/main/java/proof/baseline/SyntheticActivity.java',
        'baseline/app/src/main/java/proof/baseline/SyntheticStateProvider.java'}
    if set(files)!=expected:raise Blocked('INPUT_FILES')
    for name,info in files.items():
        p=here/name
        if p.is_symlink() or not p.is_file():raise Blocked('INPUT_PATH')
        data=p.read_bytes()
        if len(data)!=info['size'] or hashlib.sha256(data).hexdigest()!=info['sha256']:raise Blocked('INPUT_PIN')
    return manifest


def unpack(source,destination):
    with zipfile.ZipFile(source) as z:
        if sum(i.file_size for i in z.infolist())>150_000_000:raise Blocked('ARCHIVE_SIZE')
        seen=set()
        for i in z.infolist():
            p=pathlib.PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in i.filename or i.filename in seen or stat.S_ISLNK(i.external_attr>>16):
                raise Blocked('ARCHIVE_PATH')
            seen.add(i.filename)
        z.extractall(destination)


def preflight():
    """Read-only scope and input hash validation before any KVM permission change."""
    here=pathlib.Path(__file__).resolve().parent;repo=here.parent
    expected={'GITHUB_REPOSITORY':'origest/AutoAccounting-ui-tests','GITHUB_REF':'refs/heads/main',
        'GITHUB_REF_NAME':'main','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_RUN_ATTEMPT':'1','REPOSITORY_PRIVATE':'false'}
    if any(os.environ.get(k)!=v for k,v in expected.items()):raise Blocked('SCOPE')
    sha=os.environ.get('EXPECTED_COMMIT','')
    if not re.fullmatch('[0-9a-f]{40}',sha) or sha!=os.environ.get('GITHUB_SHA'):raise Blocked('COMMIT')
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=sha:raise Blocked('CHECKOUT')
    read_reviewed_inputs(here)
    return here


def execute():
    here=preflight()
    for key in list(os.environ):
        if any(word in key.upper() for word in ('TOKEN','SECRET','PASSWORD','CREDENTIAL','AUTHORIZATION')):os.environ.pop(key,None)
    read_reviewed_inputs(here)
    stage('REVIEWED_SYNTHETIC_SCOPE_OK')
    if not os.access('/dev/kvm',os.R_OK|os.W_OK):raise Blocked('KVM_ACCESS')
    sdk=pathlib.Path(os.environ.get('ANDROID_SDK_ROOT',os.environ.get('ANDROID_HOME','/missing')))
    java=pathlib.Path(os.environ.get('JAVA_HOME_21_X64','/missing'))
    if not (java/'bin/java').is_file():raise Blocked('JDK21')
    os.environ['ANDROID_SDK_ROOT']=str(sdk);os.environ['JAVA_HOME']=str(java)
    os.environ['PATH']=str(java/'bin')+os.pathsep+os.environ['PATH']
    with tempfile.TemporaryDirectory(prefix='synthetic-dual-build-',dir=os.environ.get('RUNNER_TEMP')) as tmp:
        root=pathlib.Path(tmp);parallel=root/'parallel';parallel.mkdir();baseline=root/'baseline';baseline.mkdir()
        raw=root/'raw-build.log'
        def command(args,timeout,cwd=None,input=None):
            with raw.open('ab') as out:
                r=subprocess.run([str(a) for a in args],cwd=cwd,stdin=subprocess.DEVNULL if input is None else None,
                    input=input,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
            if r.returncode:raise Blocked('BUILD_OR_SDK_COMMAND')
        unpack(here/'parallel-source.zip',parallel)
        for p in (here/'baseline').rglob('*'):
            if p.is_file():
                rel=p.relative_to(here).as_posix()
                # Never copy unreviewed build output or config, even if the tree has extra files.
                if rel not in json.loads((here/'reviewed-inputs.json').read_text())['files']:continue
                dst=baseline/p.relative_to(here/'baseline');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
        wrapper=parallel/'gradle/wrapper/gradle-wrapper.properties';s=wrapper.read_text()
        if 'distributionUrl=https\\://services.gradle.org/distributions/gradle-8.11.1-bin.zip' not in s or 'distributionSha256Sum=' in s:
            raise Blocked('GRADLE_PIN')
        wrapper.write_text(s+'\ndistributionSha256Sum=f397b287023acdba1e9f6fc5ea72d22dd63669d59ed4a289a29b1a76eee151c6\n')
        def licenses():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (sdk/'licenses').glob('*') if p.is_file()}
        before=licenses()
        if not before:raise Blocked('SDK_LICENSE_MISSING')
        manager=sdk/'cmdline-tools/latest/bin/sdkmanager'
        if not manager.is_file():raise Blocked('SDKMANAGER_MISSING')
        command([manager,'--install','platform-tools','emulator','platforms;android-36','build-tools;35.0.0',
            'system-images;android-34;google_apis;x86_64'],300,input=b'n\n'*20)
        if licenses()!=before:raise Blocked('SDK_LICENSE_CHANGED')
        stage('SDK_READY')
        os.environ['GRADLE_USER_HOME']=str(root/'gradle')
        options=['--no-daemon','--console=plain','--max-workers=2','--no-build-cache','--no-configuration-cache','--no-scan',
            '-Pandroid.builder.sdkDownload=false','-Dorg.gradle.java.installations.auto-download=false']
        command(['bash',parallel/'gradlew',*options,':app:assembleDebug',':app:assembleDebugAndroidTest'],1020,cwd=parallel)
        stage('PARALLEL_SOURCE_BUILD_OK')
        command(['bash',parallel/'gradlew','-p',baseline,*options,':app:assembleDebug'],300,cwd=baseline)
        stage('SYNTHETIC_BASELINE_BUILD_OK')
        built=root/'built';built.mkdir()
        for src,folder,name in [(parallel,'debug','parallel.apk'),(parallel,'androidTest/debug','tests.apk'),(baseline,'debug','baseline.apk')]:
            apks=list((src/'app/build/outputs/apk'/folder).glob('*.apk'))
            if len(apks)!=1:raise Blocked('APK_COUNT')
            shutil.copyfile(apks[0],built/name)
        spec=importlib.util.spec_from_file_location('dual_synthetic_runner',here/'run-emulator.py')
        runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
        stage('FRESH_DUAL_SYNTHETIC_EMULATOR_START')
        runner.execute(built,root/'raw-instrumentation.log')
        stage('DUAL_SYNTHETIC_ISOLATION_AND_CLEANUP_PASS')

if __name__=='__main__':
    try:
        if sys.argv[1:]==['--preflight']:
            preflight();print('STAGE_READ_ONLY_PREFLIGHT_OK',flush=True)
        elif not sys.argv[1:]:execute()
        else:raise Blocked('ARGUMENTS')
    except Blocked as error:
        allowed={'INPUT_REVIEW_PENDING','INPUT_SCOPE','INPUT_FILES','INPUT_PATH','INPUT_PIN','ARCHIVE_SIZE','ARCHIVE_PATH',
            'ARGUMENTS','SCOPE','COMMIT','CHECKOUT','KVM_ACCESS','JDK21','BUILD_OR_SDK_COMMAND','GRADLE_PIN','SDK_LICENSE_MISSING',
            'SDKMANAGER_MISSING','SDK_LICENSE_CHANGED','APK_COUNT'}
        print('SUMMARY_DUAL_BLOCKED_'+(str(error) if str(error) in allowed else 'PRECONDITION'),flush=True);sys.exit(1)
    except BaseException:
        print('SUMMARY_DUAL_SYNTHETIC_NOT_PASSED',flush=True);sys.exit(1)
    if not sys.argv[1:]:print('SUMMARY_DUAL_SYNTHETIC_PASSED',flush=True)
