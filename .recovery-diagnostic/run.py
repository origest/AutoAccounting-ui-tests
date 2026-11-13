#!/usr/bin/env python3
"""One owned ordinary AVD, six unsent-retry instrumentation methods, no artifact upload/retry."""
import hashlib, json, os, pathlib, re, shutil, socket, subprocess, tempfile, time, signal

HERE = pathlib.Path(__file__).resolve().parent
APK = [('app.apk', 77991914, '7aaaf6bfc74e0b885373b0803fd1c31d2b60986ee7e6994bc3979dca04c01ef6'), ('tests.apk', 951225, '6f46d6e19afbd4e45b022915ab2a6a16d7c2b01624b13c81848f4f099c03e4b0')]
TARGET = 'net.ankio.auto'
IMAGE = 'system-images;android-34;google_apis;x86_64'


DIAGNOSTIC_STAGES = frozenset({'BACKEND_WAIT_BEGIN', 'BACKEND_READY', 'BACKEND_WAIT_FAILED',
                               'POST_BEGIN', 'POST_RETURNED'})
BACKEND_KINDS = frozenset({'NONE', 'TRANSPORT_OR_PARSE_UNDISTINGUISHED', 'RESPONSE_MISSING',
                           'LIST_MISSING', 'BUSINESS_CODE', 'UNCLASSIFIED'})

def phase_diagnostic(text):
    """Only exact allowlisted status bundles; never evidence of test completion."""
    stages=[]; failures=[]; bundle={}; invalid=False
    for line in text.splitlines():
        m=re.fullmatch(r'INSTRUMENTATION_STATUS: (ordinaryStage|ordinaryBackendFailureKind|ordinaryBackendBusinessCode)=(.*)',line)
        if m:
            key,value=m.groups()
            if key in bundle and bundle[key] != value: invalid=True
            bundle[key]=value
        if re.fullmatch(r'INSTRUMENTATION_STATUS_CODE: -?\d+',line):
            if line == 'INSTRUMENTATION_STATUS_CODE: 0':
                stage=bundle.get('ordinaryStage')
                if stage is not None:
                    if stage in DIAGNOSTIC_STAGES:
                        if stage not in stages: stages.append(stage)
                    else: invalid=True
                if 'ordinaryBackendFailureKind' in bundle or 'ordinaryBackendBusinessCode' in bundle:
                    kind=bundle.get('ordinaryBackendFailureKind'); raw=bundle.get('ordinaryBackendBusinessCode','')
                    valid=kind in BACKEND_KINDS and (re.fullmatch(r'[1-5][0-9]{2}',raw) if kind=='BUSINESS_CODE' else raw=='0')
                    if valid:
                        item={'kind':kind,'code':int(raw)}
                        if item not in failures: failures.append(item)
                    else: invalid=True
            bundle={}
    result={'ordinary_stages':stages}
    # Multiple contradictory failure reports are not silently resolved.
    if len(failures)==1 and not invalid: result['ordinary_backend_failure']=failures[0]
    elif len(failures)>1 or invalid: result['ordinary_diagnostic_status']='INVALID_OR_CONFLICTING'
    return result


RECOVERY_STAGES = frozenset({
    'TEST_ENTER', 'SERVER_CONSTRUCT_BEGIN', 'SERVER_CONSTRUCT_DONE',
    'PORT_HOLD_BEGIN', 'FIRST_START_BEGIN', 'FIRST_HTTP_BEGIN', 'FIRST_HTTP_OK',
    'STOP_BEGIN', 'STOP_DONE', 'SECOND_START_BEGIN', 'SECOND_HTTP_BEGIN',
    'SECOND_HTTP_OK', 'TEST_CLEANUP_BEGIN', 'TEST_COMPLETE',
} | {prefix + state for prefix in ('OCCUPIED_', 'FIRST_', 'SECOND_')
     for state in ('NEW', 'STARTING', 'RUNNING', 'WAITING_PORT', 'RETRY_WAIT',
                   'CLEANUP_UNKNOWN', 'DISABLED', 'EXHAUSTED')})
RECOVERY_KINDS = frozenset({'ASSERTION', 'SOCKET_TIMEOUT', 'CONNECT', 'BIND',
    'CLASS_MISSING', 'METHOD_MISSING', 'NULL_VALUE', 'ILLEGAL_STATE', 'SECURITY', 'OTHER'})

def recovery_diagnostic(text):
    stages=[]; kinds=[]
    for line in text.splitlines():
        match=re.fullmatch(r'INSTRUMENTATION_STATUS: (recoveryStage|recoveryFailureKind)=(.*)',line)
        if not match: continue
        key,value=match.groups()
        allowed=RECOVERY_STAGES if key=='recoveryStage' else RECOVERY_KINDS
        target=stages if key=='recoveryStage' else kinds
        if value in allowed and value not in target: target.append(value)
    # Only exact fixed labels. No throwable messages, URLs, payloads, or raw stack.
    return {'recovery_stages':stages, 'recovery_failure_kinds':kinds}


def safe_diagnostic(text):
    # Emit only fixed diagnostic labels and test-owned stack coordinates, never raw values.
    labels = {
        'PRECONDITION_PORT_OCCUPIED': 'PRECONDITION_PORT_OCCUPIED',
        'Fresh guest has existing AppData rows': 'PREPOST_NONEMPTY_DATABASE',
        'Real DataFragment navigation timed out': 'NAVIGATION_NOT_READY',
        'Production launcher did not reach HomeActivity': 'LAUNCHER_HOME_NOT_REACHED',
        'Posted synthetic marker absent': 'OS_NOTIFICATION_NOT_OBSERVED',
        'Production AppDataAPI did not expose': 'PRODUCTION_ROW_NOT_OBSERVED',
        'Already-open DataFragment did not display': 'UI_AUTO_REFRESH_NOT_OBSERVED',
        'Original row not preserved': 'COLD_RESTART_ROW_NOT_PRESERVED',
        'Duplicate synthetic rows': 'DUPLICATE_ROWS',
        'Marker must be absent': 'MARKER_ALREADY_PRESENT',
        'CoreService start rejected': 'CORE_SERVICE_START_REJECTED',
        'BLOCKED_PERMISSION': 'LISTENER_ACCESS_NOT_READY',
        'BLOCKED_HOST': 'HOST_OWNERSHIP_PRECONDITION',
        'BLOCKED_SOURCE': 'SOURCE_PRECONDITION',
        'TimeoutCancellationException': 'COROUTINE_READINESS_TIMEOUT',
        'BACKEND_READY_TIMEOUT': 'BACKEND_READY_TIMEOUT',
        'ConnectException': 'API_CONNECTION_FAILURE',
        'SecurityException': 'ANDROID_SECURITY_EXCEPTION',
        'AssertionError': 'ASSERTION_FAILED',
        'java.lang.IllegalStateException': 'JAVA_ILLEGAL_STATE',
        'java.lang.NoClassDefFoundError': 'JAVA_CLASS_MISSING',
        'java.lang.NoSuchMethodError': 'JAVA_METHOD_MISSING',
        'java.lang.NullPointerException': 'JAVA_NULL_VALUE',
        'java.net.SocketTimeoutException': 'SOCKET_TIMEOUT',
        'INSTRUMENTATION_FAILED:': 'INSTRUMENTATION_ABORTED',
        'Process crashed': 'APP_PROCESS_CRASH',
        'Unable to find instrumentation': 'RUNNER_NOT_INSTALLED',
    }
    result={'diagnostic_codes':sorted({v for k,v in labels.items() if k in text}) or ['UNCLASSIFIED_INSTRUMENTATION_FAILURE']}
    result['test_stack_frames']=[]  # No free-form stack values in this diagnostic candidate.
    result.update(phase_diagnostic(text))
    result.update(recovery_diagnostic(text))
    return result


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
    if not re.search(r'^INSTRUMENTATION_CODE: -1\s*$',text,re.M):
        raise RuntimeError('Missing terminal instrumentation success')
    bundle, completed = {}, 0
    fields = {}
    for line in text.splitlines():
        m = re.match(r'INSTRUMENTATION_STATUS: ([A-Za-z0-9_]+)=(.*)',line)
        if m:
            k,v=m.groups(); bundle[k]=v
            if k in ('ordinaryMarker','ordinaryLiveRowId'):
                if k in fields and fields[k]!=v: raise RuntimeError('Conflicting result fields')
                fields[k]=v
        m = re.match(r'INSTRUMENTATION_STATUS_CODE: (-?\d+)',line)
        if m:
            code=int(m.group(1))
            if code < 0: raise RuntimeError('Test failure/ignored/assumption failure')
            if code == 0 and bundle.get('test') == method and bundle.get('class') == test_class:
                completed += 1
            bundle={}
    if completed != 1 or not re.search(r'OK \(1 test\)',text):
        raise RuntimeError('Expected exactly one named passing test')
    return fields


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
            out=a('shell','am','instrument','-w','-r','-e','class',test_class+'#'+method,
                  TARGET+'.test/androidx.test.runner.AndroidJUnitRunner',timeout=180)
            try: parsed=parse_result(out,method,test_class)
            except Exception:
                print(json.dumps({'method':method,**safe_diagnostic(out)}),flush=True)
                raise
            print(json.dumps({'method':method,**recovery_diagnostic(out)}),flush=True)
            print(json.dumps({'method':method,'status':'PASS'}),flush=True)
            return parsed
        test('net.ankio.auto.http.UnsentHookRetryDeviceTest', 'typedUnsentFailureHasThreeAttemptBound')
        test('net.ankio.auto.http.UnsentHookRetryDeviceTest', 'ambiguousIoFailureDoesNotRetry')
        test('net.ankio.auto.http.UnsentHookRetryDeviceTest', 'cancellationDuringBackoffStopsFurtherAttempts')
        test('net.ankio.auto.http.UnsentHookRetryDeviceTest', 'serverRecoversAfterRefusedConnectionReceivesExactlyOnePost')
        test('net.ankio.auto.http.UnsentHookRetryDeviceTest', 'lostResponseAfterPostMustNotReplay')
        test('net.ankio.auto.http.UnsentHookRetryDeviceTest', 'retryAfterZeroMustNotTriggerHiddenPostReplay')
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


