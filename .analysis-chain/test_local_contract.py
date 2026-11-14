import importlib.util,pathlib,tempfile,unittest,zipfile,io,contextlib,os,json
from unittest import mock
HERE=pathlib.Path(__file__).parent

def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=module('runner','run-emulator.py');b=module('builder','build-and-test.py')
def good():
 out=''
 for stage in r.EXPECTED_STAGES:out+=f'INSTRUMENTATION_STATUS: analysisStage={stage}\nINSTRUMENTATION_STATUS_CODE: 1\n'
 return out+f'INSTRUMENTATION_STATUS: class={r.TEST_CLASS}\nINSTRUMENTATION_STATUS: test={r.TEST_METHOD}\nINSTRUMENTATION_STATUS_CODE: 0\nOK (1 test)\nINSTRUMENTATION_CODE: -1\n'
class Contract(unittest.TestCase):
 def test_valid(self):r.parse_result(good())
 def test_diagnostics_never_echo_free_text(self):
  out=io.StringIO()
  with contextlib.redirect_stdout(out):r.safe_evidence('AssertionError secret-account-number\nINSTRUMENTATION_STATUS: analysisStage=secret-token\n')
  self.assertEqual(out.getvalue(),'STAGE_ANALYSIS_UNRECOGNIZED\nDIAGNOSTIC_ASSERTION\n')
 def test_safe_known_stages(self):
  out=io.StringIO()
  with contextlib.redirect_stdout(out):r.safe_evidence(good())
  self.assertEqual(out.getvalue().splitlines(),['STAGE_ANALYSIS_'+s for s in r.EXPECTED_STAGES])
 def test_each_missing_milestone(self):
  for s in r.EXPECTED_STAGES:
   with self.subTest(s=s),self.assertRaises(RuntimeError):r.parse_result(good().replace(f'INSTRUMENTATION_STATUS: analysisStage={s}\n',''))
 def test_duplicate_stage(self):
  with self.assertRaises(RuntimeError):r.parse_result(f'INSTRUMENTATION_STATUS: analysisStage={r.EXPECTED_STAGES[0]}\nINSTRUMENTATION_STATUS_CODE: 1\n'+good())
 def test_unexpected_started_test(self):
  with self.assertRaises(RuntimeError):r.parse_result('INSTRUMENTATION_STATUS: class=OtherClass\nINSTRUMENTATION_STATUS_CODE: 1\n'+good())
 def test_test_only_install_is_restricted_to_owned_blank_avd(self):
  text=(HERE/'run-emulator.py').read_text()
  self.assertIn("a('install','-t','--no-streaming'",text)
  self.assertLess(text.index("raise RuntimeError('WRONG_AVD')"),text.index("a('install','-t'"))
  self.assertLess(text.index("raise RuntimeError('DEVICE_NOT_BLANK')"),text.index("a('install','-t'"))
  self.assertIn("('target.apk','tests.apk')",text)
 def test_extra_stage(self):
  with self.assertRaises(RuntimeError):r.parse_result('INSTRUMENTATION_STATUS: analysisStage=EXTRA\nINSTRUMENTATION_STATUS_CODE: 1\n'+good())
 def test_skipped(self):
  with self.assertRaises(RuntimeError):r.parse_result(good().replace('INSTRUMENTATION_STATUS_CODE: 0','INSTRUMENTATION_STATUS_CODE: -3'))
 def test_wrong_method(self):
  with self.assertRaises(RuntimeError):r.parse_result(good().replace(r.TEST_METHOD,'different'))
 def test_duplicate_terminal(self):
  with self.assertRaises(RuntimeError):r.parse_result(good()+'INSTRUMENTATION_CODE: -1\n')
 def test_missing_terminal(self):
  with self.assertRaises(RuntimeError):r.parse_result(good().replace('INSTRUMENTATION_CODE: -1\n',''))
 def test_failed(self):
  with self.assertRaises(RuntimeError):r.parse_result(good()+'FAILURES!!!\n')
 def test_duplicate_status_key(self):
  with self.assertRaises(RuntimeError):r.parse_result(good().replace(f'INSTRUMENTATION_STATUS: test={r.TEST_METHOD}',f'INSTRUMENTATION_STATUS: test={r.TEST_METHOD}\nINSTRUMENTATION_STATUS: test={r.TEST_METHOD}'))
 def test_two_tests(self):
  with self.assertRaises(RuntimeError):r.parse_result(good().replace('OK (1 test)','OK (2 tests)'))
 def test_draft_pins_fail_closed(self):
  manifest=json.loads((HERE/'reviewed-inputs.json').read_text());manifest['review_ready']=False
  with mock.patch.object(b.json,'loads',return_value=manifest):
   with self.assertRaises(b.Blocked):b.read_reviewed_inputs(HERE)
 def test_staged_inputs_match_pins_without_enabling(self):
  manifest=json.loads((HERE/'reviewed-inputs.json').read_text())
  self.assertIs(manifest['review_ready'],True)
  manifest['review_ready']=True
  with mock.patch.object(b.json,'loads',return_value=manifest):b.read_reviewed_inputs(HERE)
 def test_preflight_rejects_wrong_scope_without_git_or_write(self):
  with mock.patch.dict(os.environ,{},clear=True),mock.patch.object(b.subprocess,'check_output') as git:
   with self.assertRaises(b.Blocked):b.preflight()
   git.assert_not_called()
 def test_preflight_accepts_exact_scope_and_pins(self):
  env={'GITHUB_REPOSITORY':'origest/AutoAccounting-ui-tests','GITHUB_REF':'refs/heads/main',
    'GITHUB_REF_NAME':'main','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_RUN_ATTEMPT':'1','REPOSITORY_PRIVATE':'false',
    'EXPECTED_COMMIT':'a'*40,'GITHUB_SHA':'a'*40}
  with mock.patch.dict(os.environ,env,clear=True),mock.patch.object(b.subprocess,'check_output',return_value='a'*40+'\n'),mock.patch.object(b,'read_reviewed_inputs'):
   self.assertEqual(b.preflight(),HERE.resolve())
 def test_preflight_rejects_checkout_mismatch(self):
  env={'GITHUB_REPOSITORY':'origest/AutoAccounting-ui-tests','GITHUB_REF':'refs/heads/main',
    'GITHUB_REF_NAME':'main','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_RUN_ATTEMPT':'1','REPOSITORY_PRIVATE':'false',
    'EXPECTED_COMMIT':'a'*40,'GITHUB_SHA':'a'*40}
  with mock.patch.dict(os.environ,env,clear=True),mock.patch.object(b.subprocess,'check_output',return_value='b'*40+'\n'):
   with self.assertRaises(b.Blocked):b.preflight()
 def test_wrapper_preflights_before_any_acl_write_or_grant(self):
  text=(HERE/'with-kvm-acl.sh').read_text();pre=text.index('python3 .analysis-chain/build-and-test.py --preflight')
  self.assertLess(pre,text.index('getfacl -p /dev/kvm > "$acl"'))
  self.assertLess(pre,text.index('sudo -n setfacl -m'))
 def test_archive_traversal(self):
  with tempfile.TemporaryDirectory() as d:
   d=pathlib.Path(d)
   with zipfile.ZipFile(d/'bad.zip','w') as z:z.writestr('../escape','x')
   with self.assertRaises(b.Blocked):b.unpack(d/'bad.zip',d/'out')
 def test_archive_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   d=pathlib.Path(d)
   with zipfile.ZipFile(d/'bad.zip','w') as z:z.writestr('same','x');z.writestr('same','y')
   with self.assertRaises(b.Blocked):b.unpack(d/'bad.zip',d/'out')
if __name__=='__main__':unittest.main()
