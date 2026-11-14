#!/usr/bin/env python3
"""Fresh owned emulator synthetic analysis timeout test. No real accounts or external AI."""
import os, pathlib, re, shutil, signal, socket, subprocess, tempfile, time

TARGET = 'net.ankio.auto.analysisfixture'
TEST_CLASS = 'net.ankio.auto.testing.AnalysisCommitWaitDeviceTest'
TEST_METHOD = 'insertedBillSurvivesClientTimeoutWithoutReplay'
EXPECTED_STAGES = ('POST_INSERT_TIMEOUT_SINGLE_ROW_NO_REPLAY',)
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
        m = re.fullmatch(r'INSTRUMENTATION_STATUS: analysisStage=(.*)', line)
        if m: stages.append(m.group(1))
        m = re.fullmatch(r'INSTRUMENTATION_STATUS: ([A-Za-z0-9_]+)=(.*)', line)
        if m:
            key,value=m.groups()
            if key in bundle: raise RuntimeError('DUPLICATE_STATUS')
            bundle[key]=value
        m = re.fullmatch(r'INSTRUMENTATION_STATUS_CODE: (-?\d+)', line)
        if m:
            code=int(m.group(1))
            if ('class' in bundle and bundle['class']!=TEST_CLASS) or ('test' in bundle and bundle['test']!=TEST_METHOD):
                raise RuntimeError('UNEXPECTED_TEST')
            if code not in (0,1): raise RuntimeError('TEST_NOT_PASSED')
            if code==0:
                if bundle.get('class')!=TEST_CLASS or bundle.get('test')!=TEST_METHOD:
                    raise RuntimeError('UNEXPECTED_TEST')
                completed+=1
            bundle={}
    if completed!=1 or not re.search(r'^OK \(1 test\)\s*$',text,re.M): raise RuntimeError('TEST_COUNT')
    if tuple(stages)!=EXPECTED_STAGES: raise RuntimeError('STAGE_EVIDENCE')


# These describe transcript signals, not which business assertion failed.
FAILURE_SIGNALS = {
 'INSTRUMENTATION_FAILED': 'LAUNCH_FAILED_MARKER',
 'INSTRUMENTATION_ABORTED': 'ABORTED_MARKER',
 'FAILURES!!!': 'JUNIT_FAILURE_BANNER',
 'Process crashed': 'PROCESS_CRASH_MARKER',
}

def failure_signals(text):
    return tuple(sorted(label for marker,label in FAILURE_SIGNALS.items() if marker in text))


PROGRESS = frozenset(('APP_START','APP_READY','ROOM_READY','JS_NATIVE_INIT','JS_SANITY_OK',
 'RULE_READY','SERVER_READY','REQUEST_RECEIVED','BEFORE_SECOND_CATEGORY','CLIENT_READ_TIMEOUT','FINISHED'))
CLIENT_OUTCOMES = frozenset(('HTTP_2XX','HTTP_4XX','HTTP_5XX','HTTP_OTHER','READ_TIMEOUT','IO_OTHER'))

def safe_evidence(text):
    """Only reviewed stage enums and fixed diagnostic labels, never exception contents."""
    for line in text.splitlines():
        for key,allowed,prefix in [('analysisProgress',PROGRESS,'DIAGNOSTIC_TEST_PROGRESS_'),('analysisClient',CLIENT_OUTCOMES,'DIAGNOSTIC_CLIENT_')]:
            m=re.fullmatch('INSTRUMENTATION_STATUS: '+key+'=(.*)',line)
            if m:print(prefix+(m.group(1) if m.group(1) in allowed else 'UNRECOGNIZED'),flush=True)
    for label in failure_signals(text):print('DIAGNOSTIC_TRANSCRIPT_'+label,flush=True)
    for line in text.splitlines():
        m=re.fullmatch(r'INSTRUMENTATION_STATUS: analysisStage=(.*)',line)
        if m:
            print('STAGE_ANALYSIS_'+(m.group(1) if m.group(1) in EXPECTED_STAGES else 'UNRECOGNIZED'),flush=True)
    codes={'UnsatisfiedLinkError':'NATIVE_LINK','AssertionError':'ASSERTION','IllegalStateException':'PRECONDITION','TimeoutException':'TIMEOUT',
        'TimeoutCancellationException':'COROUTINE_TIMEOUT','SecurityException':'ANDROID_SECURITY','NoClassDefFoundError':'CLASS_MISSING',
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


# Closed diagnostic vocabulary. Never print exception text, command output or paths.
PHASES = frozenset(('PREFLIGHT','PRIVATE_ADB_START','AVD_CREATE','EMULATOR_START',
 'DEVICE_CONNECT','DEVICE_BOOT','VERIFY_OWNED_BLANK','INSTALL_TARGET','INSTALL_TEST',
 'INSTRUMENTATION','RESULT_VALIDATION','COMPLETE'))
REASONS = frozenset(('CONTRACT_NOT_FINAL','SDK_MISSING','KVM_ACCESS','DEADLINE',
 'DEVICE_COMMAND','ADB_START','BOOT_FAILED','WRONG_AVD','DEVICE_NOT_BLANK',
 'INSTALL_NOT_CONFIRMED','CANCELLED','OWNED_CLEANUP_INCOMPLETE',
 'INSTRUMENTATION_FAILED','TERMINAL_RESULT','DUPLICATE_STATUS','UNEXPECTED_TEST',
 'TEST_NOT_PASSED','TEST_COUNT','STAGE_EVIDENCE'))

def diagnostic_failure(phase,error):
    phase=phase if isinstance(phase,str) and phase in PHASES else 'UNKNOWN'
    if type(error) is RuntimeError and len(error.args)==1 and isinstance(error.args[0],str) and error.args[0] in REASONS:
        reason=error.args[0]
    elif isinstance(error,subprocess.TimeoutExpired):reason='COMMAND_TIMEOUT'
    elif isinstance(error,FileNotFoundError):reason='FILE_MISSING'
    elif isinstance(error,PermissionError):reason='PERMISSION_DENIED'
    elif isinstance(error,OSError):reason='OS_ERROR'
    else:reason='UNCLASSIFIED'
    print('DIAGNOSTIC_DEVICE_PHASE_'+phase,flush=True)
    print('DIAGNOSTIC_DEVICE_REASON_'+reason,flush=True)

def execute(built,rawlog):
    state={'phase':'PREFLIGHT','reported':False}
    def mark(phase):
        if phase not in PHASES:raise RuntimeError('CONTRACT_NOT_FINAL')
        state['phase']=phase
        print('STAGE_DEVICE_'+phase,flush=True)
    def report(error):
        if not state['reported']:
            diagnostic_failure(state['phase'],error);state['reported']=True
    try:return _execute(built,rawlog,mark,report)
    except BaseException as error:
        report(error);raise


def _execute(built, rawlog, mark, report):
    if not EXPECTED_STAGES: raise RuntimeError('CONTRACT_NOT_FINAL')
    sdk=pathlib.Path(os.environ['ANDROID_SDK_ROOT'])
    adb=sdk/'platform-tools/adb'; emulator=sdk/'emulator/emulator'; manager=sdk/'cmdline-tools/latest/bin/avdmanager'
    if not all(x.is_file() for x in (adb,emulator,manager)): raise RuntimeError('SDK_MISSING')
    if not os.access('/dev/kvm',os.R_OK|os.W_OK): raise RuntimeError('KVM_ACCESS')
    root=pathlib.Path(tempfile.mkdtemp(prefix='analysis-chain-owned-',dir=os.environ.get('RUNNER_TEMP')))
    previous={}
    try:
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
        for sig in (signal.SIGTERM,signal.SIGINT):previous[sig]=signal.signal(sig,interrupted)
    except BaseException as error:
        report(error)
        clean=False
        try:
            shutil.rmtree(root);clean=not root.exists()
        finally:
            for sig,handler in previous.items():signal.signal(sig,handler)
            print('STAGE_DEVICE_CLEANUP_'+('OK' if clean else 'FAILED'),flush=True)
        raise
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
        mark('PRIVATE_ADB_START')
        adbproc=subprocess.Popen([str(adb),'-P',str(port),'nodaemon','server'],env=env,stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,start_new_session=True)
        time.sleep(1)
        if adbproc.poll() is not None: raise RuntimeError('ADB_START')
        mark('AVD_CREATE')
        cmd([manager,'create','avd','--name','analysis_chain_owned','--package',IMAGE,'--device','pixel_2'],input='no\n')
        mark('EMULATOR_START')
        for p in (5580,5581):
            with socket.socket() as s:s.bind(('127.0.0.1',p))
        proc=subprocess.Popen([str(emulator),'-avd','analysis_chain_owned','-port','5580','-no-window','-no-audio',
             '-no-boot-anim','-no-snapshot','-no-snapshot-save','-gpu','swiftshader_indirect','-accel','on','-memory','2048'],
             env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        mark('DEVICE_CONNECT')
        a('wait-for-device',timeout=240)
        mark('DEVICE_BOOT')
        bootend=time.monotonic()+180
        while a('shell','getprop','sys.boot_completed').strip()!='1':
            if time.monotonic()>bootend or proc.poll() is not None: raise RuntimeError('BOOT_FAILED')
            time.sleep(2)
        mark('VERIFY_OWNED_BLANK')
        if 'analysis_chain_owned' not in a('emu','avd','name'): raise RuntimeError('WRONG_AVD')
        if a('shell','pm','list','packages','net.ankio.auto').strip():raise RuntimeError('DEVICE_NOT_BLANK')
        for name in ('target.apk','tests.apk'):
            mark('INSTALL_TARGET' if name=='target.apk' else 'INSTALL_TEST')
            result=a('install','-t','--no-streaming',str(built/name),timeout=120)
            if not re.search(r'^Success\s*$',result,re.M):raise RuntimeError('INSTALL_NOT_CONFIRMED')
        mark('INSTRUMENTATION')
        out=a('shell','am','instrument','-w','-r','-e','freshAnalysisFixture','true','-e','class',
              TEST_CLASS+'#'+TEST_METHOD,TARGET+'.test/androidx.test.runner.AndroidJUnitRunner',timeout=180)
        safe_evidence(out)
        mark('RESULT_VALIDATION')
        parse_result(out)
        mark('COMPLETE')
    except BaseException as error:
        report(error);raise
    finally:
        for s in previous:signal.signal(s,signal.SIG_IGN)
        stopped=[]
        for process in (proc,adbproc):
            try:stopped.append(stop_owned(process))
            except Exception:stopped.append(False)
        clean=False
        try:
            if all(stopped):shutil.rmtree(root)
            clean=all(stopped) and not root.exists()
        except OSError:
            clean=False
        finally:
            for s,handler in previous.items():signal.signal(s,handler)
        print('STAGE_DEVICE_CLEANUP_'+('OK' if clean else 'FAILED'),flush=True)
        if not clean:raise RuntimeError('OWNED_CLEANUP_INCOMPLETE')
