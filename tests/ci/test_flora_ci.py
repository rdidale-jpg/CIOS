"""CI policy tests; never install FLORA authority fixtures or change production."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import sqlite3
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/ci'))
import flora_ci as ci


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.old={'tests/test_sample.py::test_ok':{'status':'passed'},
                  'tests/test_sample.py::test_old':{'status':'failed','signature':{'frame':['tests/test_sample.py','test_old','assert old'], 'headline_sha256':'known'}},
                  'tests/test_sample.py::test_skip':{'status':'skipped','reason':'Retained artifact unavailable: TEL-W6'}}

    def issue(self,mutate,kind):
        actual=copy.deepcopy(self.old);mutate(actual)
        self.assertIn(kind,{x['kind'] for x in ci.compare(self.old,actual)['issues']})

    def test_verified_inherited_failures_are_reported(self):
        result=ci.compare(self.old,self.old)
        self.assertFalse(result['issues']);self.assertEqual(result['inherited'],['tests/test_sample.py::test_old'])
        self.assertEqual(result['counts'],{'passed':1,'failed':1,'skipped':1})

    def test_new_failure_rejected(self):
        self.issue(lambda v:v['tests/test_sample.py::test_ok'].update(status='failed',signature={}), 'new_failure')

    def test_changed_failure_headline_rejected(self):
        self.issue(lambda v:v['tests/test_sample.py::test_old']['signature'].update(headline_sha256='different'), 'changed_failure_signature')

    def test_changed_failure_source_rejected(self):
        self.issue(lambda v:v['tests/test_sample.py::test_old']['signature'].update(frame=['new']), 'changed_failure_signature')

    def test_new_skip_rejected(self):
        self.issue(lambda v:v['tests/test_sample.py::test_ok'].update(status='skipped',reason='new'), 'unexpected_skip')

    def test_changed_skip_reason_rejected(self):
        self.issue(lambda v:v['tests/test_sample.py::test_skip'].update(reason='silently disabled'), 'unexpected_skip')

    def test_missing_identity_rejected(self):
        self.issue(lambda v:v.pop('tests/test_sample.py::test_ok'), 'identity_mismatch')

    def test_extra_identity_rejected(self):
        self.issue(lambda v:v.update({'new':{'status':'passed'}}), 'identity_mismatch')

    def test_fixed_failure_explicitly_reported(self):
        value=copy.deepcopy(self.old);value['tests/test_sample.py::test_old']={'status':'passed'}
        result=ci.compare(self.old,value)
        self.assertFalse(result['issues']);self.assertEqual(result['fixed'],['tests/test_sample.py::test_old'])

    def test_security_cannot_use_domain_exception(self):
        self.assertTrue(ci.compare(self.old,self.old,strict=True)['issues'])

    def test_changed_exception_message_changes_signature(self):
        trace='tests/test_a.py:2: in test_a\n    assert value == 1\n'
        self.assertNotEqual(ci.signature('AssertionError: assert 2 == 1',trace),ci.signature('AssertionError: assert 3 == 1',trace))

    def test_only_matching_checkout_revision_is_normalized(self):
        key='tests/test_flora_pilot_import_bypass.py::test_deployment_endpoint_identifies_canonical_import_runtime'
        trace='tests/test_flora_pilot_import_bypass.py:186: in test_deployment_endpoint_identifies_canonical_import_runtime\n    assert payload["commit_sha"] == "abc123deployed"\n'
        old='83aee1aaf5a49b36d8c5e397d75b99624422fac3'
        new='8046f31b7a8f9acc630be54e37042e97d1c6965f'
        before=ci.signature("AssertionError: assert '83aee1aaf5a4...b99624422fac3' == 'abc123deployed'",trace,test_id=key,checkout_sha=old)
        after=ci.signature("AssertionError: assert '8046f31b7a8f...42e97d1c6965f' == 'abc123deployed'",trace,test_id=key,checkout_sha=new)
        self.assertEqual(before,after)
        wrong=ci.signature("AssertionError: assert '83aee1aaf5a4...b99624422fac3' == 'abc123deployed'",trace,test_id=key,checkout_sha=new)
        self.assertNotEqual(wrong,after)

    def test_other_test_sha_failure_is_not_normalized(self):
        sha='8046f31b7a8f9acc630be54e37042e97d1c6965f'
        actual=ci.signature("AssertionError: assert '"+sha+"' == 'expected'",'tests/test_a.py:2: in test_a\n    assert value == expected\n',test_id='tests/test_a.py::test_a',checkout_sha=sha)
        other=ci.signature("AssertionError: assert '"+'a'*40+"' == 'expected'",'tests/test_a.py:2: in test_a\n    assert value == expected\n',test_id='tests/test_a.py::test_a',checkout_sha='a'*40)
        self.assertNotEqual(actual,other)

    def test_repository_path_normalization_only(self):
        trace='tests/test_a.py:2: in test_a\n    assert value == 1\n'
        self.assertEqual(ci.signature('OSError: /tmp/one/cios/file.py',trace),ci.signature('OSError: /home/runner/work/repo/cios/file.py',trace))


class ExecutionTests(unittest.TestCase):
    def test_duplicate_junit_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'result.xml';path.write_text('<testsuites><testsuite><testcase classname="tests.test_a" name="test_a"/><testcase classname="tests.test_a" name="test_a"/></testsuite></testsuites>')
            with self.assertRaises(ValueError):ci.read_junit([path])

    def test_collection_error_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'result.xml';path.write_text('<testsuites><testsuite errors="1"><testcase classname="tests.test_a" name="test_a"><error/></testcase></testsuite></testsuites>')
            with self.assertRaises(ValueError):ci.read_junit([path])

    def test_empty_results_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'result.xml';path.write_text('<testsuites/>')
            with self.assertRaises(ValueError):ci.read_junit([path])

    def test_missing_integrity_records_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):ci.integrity(Path(folder))

    def seed_integrity_records(self,root):
        for filename,amount in {'hash-comparison.json':52,'01c-integrity.json':9,'01d-integrity.json':62,'acceptance-integrity.json':5,'01e-integrity.json':18}.items():
            for i in range(amount):
                folder=root/(filename+str(i));folder.mkdir()
                (folder/filename).write_text(json.dumps({'unchanged':True,'before':{'data.json':'hash'},'after':{'data.json':'hash'}}))

    def test_changed_protected_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.seed_integrity_records(root)
            record=next(root.rglob('hash-comparison.json'))
            value=json.loads(record.read_text());value['after']['data.json']='changed';record.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'Protected-data integrity mismatch'):ci.integrity(root)

    def test_corrupted_audit_chain_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.seed_integrity_records(root)
            dbpath=root/'test_concurrent_feedback_appen0/runtime/security/authority.sqlite3';dbpath.parent.mkdir(parents=True)
            with sqlite3.connect(dbpath) as db:
                db.execute('CREATE TABLE audit(seq INTEGER,at REAL,event TEXT,payload TEXT,previous TEXT,digest TEXT)')
                db.execute("INSERT INTO audit VALUES(1,1,'synthetic','{}','','bad-digest')")
            with self.assertRaisesRegex(ValueError,'Audit chain mismatch'):ci.integrity(root)

    def test_retained_journal_does_not_hide_data_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.seed_integrity_records(root)
            record=next(root.rglob('01e-integrity.json'));value=json.loads(record.read_text())
            value.update(retained_journal=True,full_after={'data.json':'changed','security/protected-undo/manifest.json':'evidence'})
            record.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'Retained-journal protected data mismatch'):ci.integrity(root)

    def test_synthetic_regressions_fail_real_runner(self):
        # Real subprocess pytest, no application authority or private workspace.
        for fault in ['new-failure','unexpected-skip','changed-signature','collection-error']:
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);(root/'tests').mkdir();test=root/'tests/test_flora_security_synthetic.py'
                source='def test_case():\n    assert 1 == 2\n'
                if fault=='unexpected-skip':source='import pytest\n@pytest.mark.skip(reason="unapproved")\ndef test_case(): pass\n'
                if fault=='collection-error':source='this is invalid python ?\n'
                test.write_text(source)
                case={'status':'failed','signature':{'frame':['old'],'headline_sha256':'old'}} if fault=='changed-signature' else {'status':'passed'}
                suite_name = 'domain' if fault=='changed-signature' else 'security'
                baseline={'version':1,'profiles':{'01a':{'security_modules':['tests/test_flora_security_synthetic.py'],
                    'suites':{suite_name:{'selections':[['tests/test_flora_security_synthetic.py']],
                    'cases':{'tests/test_flora_security_synthetic.py::test_case':case}}}}}}
                path=root/'baseline.json';path.write_text(json.dumps(baseline))
                with patch.object(ci,'BASELINE',path),patch.object(ci.subprocess,'check_output',return_value='synthetic-sha\n'):
                    result=ci.run(root,root/'out')
                self.assertEqual(result,1)
                summary=json.loads((root/'out/artifacts/summary.json').read_text())
                self.assertFalse(summary['passed']);self.assertTrue(summary['issues'])
                expected = 'changed_failure_signature' if fault=='changed-signature' else 'validation_error' if fault=='collection-error' else 'strict_security_failure_or_skip'
                self.assertIn(expected,{row['kind'] for row in summary['issues']})
                self.assertEqual(set(p.name for p in (root/'out/artifacts').iterdir()),{'summary.json','summary.md','results.xml'})

    def test_01b_profile_cannot_be_forced_to_01a(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);e=root/'docs/flora-runtime/security-repair-01b/01E-Bounded-Remediation-Evidence.json';e.parent.mkdir(parents=True);e.write_text('{}')
            with self.assertRaises(ValueError):ci.run(root,root/'out',profile='01a')

    def test_missing_security_modules_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises(ValueError):ci.run(root,root/'out')

    def test_artifact_output_not_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'tests').mkdir();(root/'tests/test_flora_security_synthetic.py').write_text('')
            baseline={'version':1,'profiles':{'01a':{'security_modules':['tests/test_flora_security_synthetic.py']}}}
            path=root/'baseline.json';path.write_text(json.dumps(baseline));(root/'out').mkdir()
            with patch.object(ci,'BASELINE',path),self.assertRaises(ValueError):ci.run(root,root/'out')


if __name__=='__main__':unittest.main()
