#!/usr/bin/env python3
"""LOCAL PREPARATION ONLY: fresh synthetic baseline substitute + parallel prototype.
No real old APK, personal device, account, snapshot or user data is used.
"""
import os, pathlib, re, shutil, signal, socket, subprocess, tempfile, time

BASELINE = 'net.ankio.auto'
TARGET = 'net.ankio.auto.paralleltest'
TEST_CLASS = 'net.ankio.auto.testing.ParallelIsolationDeviceTest'
TEST_METHOD = 'syntheticDualPackageIsolationOnly'
EXPECTED_STAGES = ('TWO_DISTINCT_SYNTHETIC_UIDS','NEW_PORT_READY_OLD_PORT_ZERO',
    'NEW_SENTINEL_READ_BASELINE_UNCHANGED','NEW_MUTATION_ISOLATED_BASELINE_UNCHANGED',
    'OLD_PORT_ZERO_FINAL','NEW_HOST_STOPPED_BASELINE_UNCHANGED')
IMAGE = 'system-images;android-34;google_apis;x86_64'


def parse_result(text):
    if not EXPECTED_STAGES:
        raise RuntimeError('CONTRACT_NOT_FINAL')
    if re.search(r'INSTRUMENTATION_(?:FAILED|ABORTED)|FAILURES!!!|Process crashed', text):
        raise RuntimeError('INSTRUMENTATION_FAILED')
    if [x for x in text.splitlines() if x.startswith('INSTRUMENTATION_CODE:')] != ['INSTRUMENTATION_CODE: -1']:
        raise RuntimeError('TERMINAL_RESULT')
    stages, bundle, completed = [], {}, 0
    for line in text.splitlines():
        m = re.fullmatch(r'INSTRUMENTATION_STATUS: parallelStage=(.*)', line)
        if m: stages.append(m.group(1))
        m = re.fullmatch(r'INSTRUMENTATION_STATUS: ([A-Za-z0-9_]+)=(.*)', line)
        if m:
            key,value=m.groups()
            if key in bundle: raise RuntimeError('DUPLICATE_STATUS')
            bundle[key]=value
        m = re.fullmatch(r'INSTRUMENTATION_STATUS_CODE: (-?\d+)', line)
        if m:
            code=int(m.group(1))
            if code not in (0,1): raise RuntimeError('TEST_NOT_PASSED')
            if code==0:
                if bundle.get('class')!=TEST_CLASS or bundle.get('test')!=TEST_METHOD:
                    raise RuntimeError('UNEXPECTED_TEST')
                completed+=1
            bundle={}
    if completed!=1 or not re.search(r'^OK \(1 test\)\s*$',text,re.M): raise RuntimeError('TEST_COUNT')
    if tuple(stages)!=EXPECTED_STAGES: raise RuntimeError('STAGE_EVIDENCE')


def safe_evidence(text):
    """Only reviewed stage enums and fixed diagnostic labels, never exception contents."""
    for line in text.splitlines():
        m=re.fullmatch(r'INSTRUMENTATION_STATUS: parallelStage=(.*)',line)
        if m:
            print('STAGE_PARALLEL_'+(m.group(1) if m.group(1) in EXPECTED_STAGES else 'UNRECOGNIZED'),flush=True)
    codes={'AssertionError':'ASSERTION','IllegalStateException':'PRECONDITION','TimeoutException':'TIMEOUT',
        'SecurityException':'ANDROID_SECURITY','NoClassDefFoundError':'CLASS_MISSING',
        'INSTRUMENTATION_FAILED':'INSTRUMENTATION_FAILED','Process crashed':'APP_PROCESS_CRASH'}
    for label in sorted({code for key,code in codes.items() if key in text}):
        print('DIAGNOSTIC_'+label,flush=True)


def stop_owned(process):
    if process is None: return True
    for sig in (signal.SIGTERM,signal.SIGKILL):
        try: os.killpg(process.pid,sig)
        except ProcessLookupError: pass
        try: process.wait(timeout=8)
        except subprocess.TimeoutExpired: pass
    until=time.monotonic()+3
    while time.monotonic()<until:
        try: os.killpg(process.pid,0)
        except ProcessLookupError: return process.poll() is not None
        time.sleep(.1)
    return False


def execute(built, rawlog):
    if not EXPECTED_STAGES: raise RuntimeError('CONTRACT_NOT_FINAL')
    sdk=pathlib.Path(os.environ['ANDROID_SDK_ROOT'])
    adb=sdk/'platform-tools/adb'; emulator=sdk/'emulator/emulator'; manager=sdk/'cmdline-tools/latest/bin/avdmanager'
    if not all(x.is_file() for x in (adb,emulator,manager)): raise RuntimeError('SDK_MISSING')
    if not os.access('/dev/kvm',os.R_OK|os.W_OK): raise RuntimeError('KVM_ACCESS')
    root=pathlib.Path(tempfile.mkdtemp(prefix='synthetic-dual-owned-',dir=os.environ.get('RUNNER_TEMP')))
    env=os.environ.copy()
    for k in ('ANDROID_SERIAL','ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ANDROID_AVD_HOME','ANDROID_USER_HOME','ANDROID_EMULATOR_HOME'):
        env.pop(k,None)
    for k,v in [('ANDROID_AVD_HOME','avd'),('ANDROID_USER_HOME','android'),('ANDROID_EMULATOR_HOME','emulator')]:
        env[k]=str(root/v); (root/v).mkdir()
    with socket.socket() as s: s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    env['ANDROID_ADB_SERVER_PORT']=str(port)
    deadline=time.monotonic()+8*60
    proc=adbproc=None
    def interrupted(_sig,_frame): raise RuntimeError('CANCELLED')
    previous={s:signal.signal(s,interrupted) for s in (signal.SIGTERM,signal.SIGINT)}
    def cmd(args, timeout=60, input=None):
        remaining=deadline-time.monotonic()
        if remaining<=0: raise RuntimeError('DEADLINE')
        result=subprocess.run([str(a) for a in args],env=env,input=input,text=True,stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,timeout=min(timeout,remaining))
        with open(rawlog,'a') as f: f.write(result.stdout)
        if result.returncode:
            if 'instrument' in args:safe_evidence(result.stdout)
            raise RuntimeError('DEVICE_COMMAND')
        return result.stdout
    def a(*args,timeout=60):return cmd([adb,'-P',str(port),'-s','emulator-5580',*args],timeout)
    try:
        adbproc=subprocess.Popen([str(adb),'-P',str(port),'nodaemon','server'],env=env,stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,start_new_session=True)
        time.sleep(1)
        if adbproc.poll() is not None: raise RuntimeError('ADB_START')
        cmd([manager,'create','avd','--name','synthetic_dual_owned','--package',IMAGE,'--device','pixel_2'],input='no\n')
        for p in (5580,5581):
            with socket.socket() as s:s.bind(('127.0.0.1',p))
        proc=subprocess.Popen([str(emulator),'-avd','synthetic_dual_owned','-port','5580','-no-window','-no-audio',
             '-no-boot-anim','-no-snapshot','-no-snapshot-save','-gpu','swiftshader_indirect','-accel','on','-memory','2048'],
             env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        a('wait-for-device',timeout=240)
        bootend=time.monotonic()+180
        while a('shell','getprop','sys.boot_completed').strip()!='1':
            if time.monotonic()>bootend or proc.poll() is not None: raise RuntimeError('BOOT_FAILED')
            time.sleep(2)
        if 'synthetic_dual_owned' not in a('emu','avd','name'): raise RuntimeError('WRONG_AVD')
        if a('shell','pm','list','packages',BASELINE).strip():raise RuntimeError('DEVICE_NOT_BLANK')
        for name in ('baseline.apk','parallel.apk','tests.apk'):
            result=a('install','--no-streaming',str(built/name),timeout=120)
            if not re.search(r'^Success\s*$',result,re.M):raise RuntimeError('INSTALL_NOT_CONFIRMED')
        result=a('shell','am','start','-W','-n',BASELINE+'/proof.baseline.SyntheticActivity')
        if not re.search(r'^Status: ok\s*$',result,re.M):raise RuntimeError('BASELINE_START')
        readyend=time.monotonic()+10
        while True:
            state=a('shell','content','query','--uri','content://net.ankio.auto.syntheticproof/state')
            if re.search(r'\bready=1\b',state) and re.search(r'\brequests=0\b',state):break
            if time.monotonic()>readyend:raise RuntimeError('BASELINE_NOT_READY')
            time.sleep(.2)
        out=a('shell','am','instrument','-w','-r','-e','parallelBlankDevice','true','-e','class',
              TEST_CLASS+'#'+TEST_METHOD,TARGET+'.test/androidx.test.runner.AndroidJUnitRunner',timeout=180)
        safe_evidence(out)
        parse_result(out)
    finally:
        for s in previous:signal.signal(s,signal.SIG_IGN)
        stopped=[]
        for process in (proc,adbproc):
            try:stopped.append(stop_owned(process))
            except Exception:stopped.append(False)
        if all(stopped):shutil.rmtree(root)
        clean=all(stopped) and not root.exists()
        for s,handler in previous.items():signal.signal(s,handler)
        if not clean:raise RuntimeError('OWNED_CLEANUP_INCOMPLETE')
