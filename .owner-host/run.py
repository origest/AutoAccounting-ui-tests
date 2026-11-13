#!/usr/bin/env python3
"""One new ordinary emulator, exact owner lifecycle test, safe fixed evidence, no reruns/artifacts."""
import hashlib, json, os, pathlib, re, shutil, socket, subprocess, tempfile, time, signal
HERE = pathlib.Path(__file__).resolve().parent
TARGET = 'net.ankio.auto'
IMAGE = 'system-images;android-34;google_apis;x86_64'
APK = [('app.apk', 77409046, 'ccff159a34dc68629471429315b03b70453dc43aac69bf143d4089896a2c2e4b'), ('tests.apk', 990876, 'c697811c25c7475b1c55ce923925dd07d53e6dc2cdf89392edc09fad2714a9b9')]
EXPECTED_STAGES = (
 'FRESH_PRECONDITIONS_OK','FOREGROUND_HTTP_READY','DUPLICATE_START_SINGLE_OWNER',
 'LAST_LEASE_STOPPED','FOREIGN_PORT_NOT_READY','BOUNDED_RECOVERY_READY',
 'OCR_MODE_SHARED_LEASE_PRESERVED','XPOSED_MODE_RETURN_PRESERVED',
 'SYNTHETIC_LEDGER_VERIFIED','CLEANUP_PORT_FREE')

def owner_diagnostic(text):
    stages=[]; metrics=[]; invalid=False
    for line in text.splitlines():
        m=re.fullmatch(r'INSTRUMENTATION_STATUS: ownerHost(Stage|Metrics)=(.*)',line)
        if not m: continue
        kind,value=m.groups()
        if kind=='Stage':
            if value in EXPECTED_STAGES or value=='CLEANUP_UNKNOWN': stages.append(value)
            else: invalid=True
        else:
            if not re.fullmatch(r'(?:0|[1-9][0-9]{0,7})(?:\|(?:0|[1-9][0-9]{0,7})){4}',value):
                invalid=True;continue
            wall,cpu,before,after,workers=map(int,value.split('|'))
            if not (30000<=wall<=180000 and 0<=cpu<=10000000 and 0<before<=10000000 and 0<after<=10000000 and workers==1):
                invalid=True;continue
            metrics.append({'wall_ms':wall,'process_cpu_ms':cpu,'pss_before_kb':before,'pss_after_kb':after,'owner_worker_count':workers})
    result={'owner_host_stages':stages}
    if len(metrics)==1: result['idle_observation']=metrics[0]
    if invalid or len(metrics)>1: result['diagnostic_invalid']=True
    return result

def safe_diagnostic(text):
    labels={'AssertionError':'ASSERTION','IllegalStateException':'STATE_OR_PRECONDITION',
      'TimeoutException':'TIMEOUT','SecurityException':'ANDROID_SECURITY','NoClassDefFoundError':'CLASS_MISSING',
      'UnsatisfiedLinkError':'NATIVE_LIBRARY','Process crashed':'APP_PROCESS_CRASH',
      'INSTRUMENTATION_FAILED':'INSTRUMENTATION_FAILED','SAFE_CLEANUP_INCOMPLETE':'GUEST_CLEANUP_INCOMPLETE'}
    return {**owner_diagnostic(text),'diagnostic_codes':sorted({v for k,v in labels.items() if k in text}) or ['UNCLASSIFIED']}

def stop_owned(owned):
    """Best effort for one direct child session; every step attempted independently."""
    if owned is None: return True, []
    errors=[]
    for sig,label in ((signal.SIGTERM,'TERM'),(signal.SIGKILL,'KILL')):
        try: os.killpg(owned.pid,sig)
        except ProcessLookupError: pass
        except Exception: errors.append(label+'_ERROR')
        try: owned.wait(timeout=8)
        except Exception: errors.append(label+'_WAIT_ERROR')
    # Process-group absence, not just launcher exit, is necessary before deleting AVD files.
    absent=False
    end=time.monotonic()+3
    while time.monotonic()<end:
        try: os.killpg(owned.pid,0)
        except ProcessLookupError: absent=True; break
        except Exception: errors.append('GROUP_PROBE_ERROR'); break
        time.sleep(.1)
    try: exited=owned.poll() is not None
    except Exception: exited=False; errors.append('POLL_ERROR')
    return exited and absent, errors


def cleanup_owned(proc, adbproc, root):
    results={}; errors=[]
    for label,owned in (('emulator',proc),('adb',adbproc)):
        try:
            results[label], details=stop_owned(owned)
            errors.extend(label+':'+d for d in details)
        except Exception:
            results[label]=False; errors.append(label+':UNEXPECTED_CLEANUP_ERROR')
    stopped=all(results.values()); removed=False
    if stopped:
        try: shutil.rmtree(root); removed=not root.exists()
        except Exception: errors.append('OWNED_DIRECTORY_DELETE_ERROR')
    return {'processes_stopped':stopped,'guest_removed':removed,'resources':results,'errors':errors}


def parse_result(text, method, test_class):
    """Require named test completion, terminal success, no error. Exit code is insufficient."""
    if re.search(r'INSTRUMENTATION_(?:FAILED|ABORTED)|FAILURES!!!|Process crashed',text):
        raise RuntimeError('Instrumentation failure')
    terminal_lines=[line for line in text.splitlines() if line.startswith('INSTRUMENTATION_CODE:')]
    if terminal_lines != ['INSTRUMENTATION_CODE: -1']:
        raise RuntimeError('Missing/duplicate/conflicting terminal instrumentation result')
    bundle, completed = {}, 0
    fields = {}
    for line in text.splitlines():
        m = re.match(r'INSTRUMENTATION_STATUS: ([A-Za-z0-9_]+)=(.*)',line)
        if m:
            k,v=m.groups()
            if k in bundle: raise RuntimeError("Duplicate status field")
            bundle[k]=v
            if False: # No free-form result fields are returned.
                if k in fields and fields[k]!=v: raise RuntimeError('Conflicting result fields')
                fields[k]=v
        m = re.match(r'INSTRUMENTATION_STATUS_CODE: (-?\d+)',line)
        if m:
            code=int(m.group(1))
            if code < 0: raise RuntimeError('Test failure/ignored/assumption failure')
            if code not in (0,1): raise RuntimeError('Unexpected status code')
            if code == 0:
                if bundle.get('test') != method or bundle.get('class') != test_class:
                    raise RuntimeError('Unexpected test completion')
                completed += 1
            bundle={}
    if completed != 1 or not re.search(r'^OK \(1 test\)\s*$',text,re.M):
        raise RuntimeError('Expected exactly one named passing test')
    diagnostic=owner_diagnostic(text)
    if tuple(diagnostic['owner_host_stages']) != EXPECTED_STAGES or diagnostic.get('diagnostic_invalid') or 'idle_observation' not in diagnostic:
        raise RuntimeError('Missing/invalid owner lifecycle or cleanup evidence')
    return diagnostic


def validate_scope(env):
    expected = {'GITHUB_REPOSITORY': 'origest/AutoAccounting-ui-tests',
                'GITHUB_REF': 'refs/heads/main', 'GITHUB_REF_NAME': 'main',
                'GITHUB_EVENT_NAME': 'workflow_dispatch', 'REPOSITORY_PRIVATE': 'false',
                'GITHUB_RUN_ATTEMPT': '1'}
    if any(env.get(k) != v for k, v in expected.items()):
        raise RuntimeError('Wrong one-shot public scope')
    if not re.fullmatch(r'[0-9a-f]{40}', env.get('EXPECTED_COMMIT', '')):
        raise RuntimeError('Full expected commit required')
    if env['EXPECTED_COMMIT'] != env.get('GITHUB_SHA'):
        raise RuntimeError('Commit mismatch')


def execute():
    validate_scope(os.environ)
    for name,size,digest in APK:
        data=(HERE/'payload'/name).read_bytes()
        if len(data)!=size or hashlib.sha256(data).hexdigest()!=digest:
            raise RuntimeError('APK pair mismatch')
    sdk=pathlib.Path(os.environ['ANDROID_SDK_ROOT'])
    adb=sdk/'platform-tools/adb'; emulator=sdk/'emulator/emulator'
    manager=sdk/'cmdline-tools/latest/bin/avdmanager'
    if not all(p.is_file() for p in (adb,emulator,manager)): raise RuntimeError('SDK missing')
    if not os.access('/dev/kvm',os.R_OK|os.W_OK): raise RuntimeError('KVM process access missing')
    def interrupted(signum, frame): raise RuntimeError("Runner cancellation signal")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    deadline=time.monotonic()+6*60
    root=pathlib.Path(tempfile.mkdtemp(prefix='ordinary-owned-'))
    env=os.environ.copy()
    for key in ('ANDROID_SERIAL','ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ANDROID_AVD_HOME','ANDROID_USER_HOME','ANDROID_EMULATOR_HOME'):
        env.pop(key,None)
    env.update(ANDROID_AVD_HOME=str(root/'avd'),ANDROID_USER_HOME=str(root/'android'),ANDROID_EMULATOR_HOME=str(root/'emulator'))
    for key in ('ANDROID_AVD_HOME','ANDROID_USER_HOME','ANDROID_EMULATOR_HOME'):
        pathlib.Path(env[key]).mkdir()
    # Dedicated free port; fail rather than attach if our server cannot start. Runner is single-job.
    with socket.socket() as s:
        s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    env['ANDROID_ADB_SERVER_PORT']=str(port)
    proc=None; adbproc=None; success=False; failure=None
    def cmd(argv, timeout=60, input=None):
        remaining=deadline-time.monotonic()
        if remaining<=0: raise TimeoutError('Run deadline')
        r=subprocess.run([str(x) for x in argv],env=env,input=input,text=True,
                         stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=min(timeout,remaining))
        if r.returncode:
            if 'instrument' in argv: print(json.dumps(safe_diagnostic(r.stdout)),flush=True)
            raise RuntimeError('Command failed: '+str(argv[0]))
        return r.stdout
    def a(*args,timeout=60): return cmd([adb,'-P',str(port),'-s','emulator-5580',*args],timeout)
    try:
        print('STAGE_OWNED_ADB_AND_AVD',flush=True)
        # Own the foreground server process; never connect to the runner default server.
        adbproc=subprocess.Popen([str(adb),'-P',str(port),'nodaemon','server'],env=env,
                                  stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        time.sleep(1)
        if adbproc.poll() is not None: raise RuntimeError('Dedicated adb server failed')
        cmd([manager,'create','avd','--name','ordinary_owned','--package',IMAGE,'--device','pixel_2'],input='no\n')
        # Fixed console pair also checked unused; no fallback to a discovered device.
        for p in (5580,5581):
            with socket.socket() as s: s.bind(('127.0.0.1',p))
        proc=subprocess.Popen([str(emulator),'-avd','ordinary_owned','-port','5580','-no-window',
             '-no-audio','-no-boot-anim','-no-snapshot','-no-snapshot-save','-gpu','swiftshader_indirect',
             '-accel','on','-memory','2048'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        print('STAGE_EMULATOR_BOOT',flush=True)
        a('wait-for-device',timeout=240)
        boot_end=time.monotonic()+180
        while a('shell','getprop','sys.boot_completed').strip()!='1':
            if proc.poll() is not None or time.monotonic()>boot_end: raise RuntimeError('Boot failed')
            time.sleep(2)
        if proc.poll() is not None or adbproc.poll() is not None: raise RuntimeError('Owned process exited')
        if 'ordinary_owned' not in a('emu','avd','name'): raise RuntimeError('Wrong AVD')
        if a('shell','pm','list','packages',TARGET).strip(): raise RuntimeError('Target already present')
        print('STAGE_INSTALL_VERIFIED_PAIR',flush=True)
        for name,_,_ in APK: a('install','--no-streaming',str(HERE/'payload'/name),timeout=120)
        def test(test_class, method):
            print(json.dumps({'method':method,'status':'START'}),flush=True)
            if proc.poll() is not None: raise RuntimeError('Owned emulator exited')
            out=a('shell','am','instrument','-w','-r','-e','ownerHostBlankDevice','true','-e','class',test_class+'#'+method,
                  TARGET+'.test/androidx.test.runner.AndroidJUnitRunner',timeout=180)
            try: parsed=parse_result(out,method,test_class)
            except Exception:
                print(json.dumps({'method':method,**safe_diagnostic(out)}),flush=True)
                raise
            print(json.dumps({'method':method,**parsed}),flush=True)
            print(json.dumps({'method':method,'status':'PASS'}),flush=True)
            return parsed
        test('net.ankio.auto.service.OwnerHostLifecycleDeviceTest', 'freshBlankOwnerLifecycleKeepsSyntheticLedger')
        success=True
    except Exception as e:
        failure=type(e).__name__+': '+str(e)
    finally:
        # Finish bounded cleanup even if a second graceful cancellation arrives.
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        summary=cleanup_owned(proc,adbproc,root)
        print(json.dumps({'cleanup':summary,'ordinary_tests_passed':success}),flush=True)
        if not summary['processes_stopped'] or not summary['guest_removed']:
            failure=(failure+'; ' if failure else '')+'Owned resource cleanup incomplete'
    if failure: raise RuntimeError(failure)

if __name__=='__main__': execute()


