"""Release eligibility fails closed; no Render connection or token is simulated."""
from copy import deepcopy
import unittest
from tools.ci.flora_release_preflight import check, validate_inputs, NotReady, REQUIRED_STEPS

SHA = 'a' * 40
PREFIX = '/repos/rdidale-jpg/CIOS'


def fixture():
    return {
        'head': {'sha': SHA}, 'comparison': {'status': 'ahead'},
        'policy': {'protection_rules': [{'type': 'required_reviewers', 'prevent_self_review': True,
                                       'reviewers': [{'type': 'User', 'reviewer': {'id': 1}}]}]},
        'runs': {'workflow_runs': [{'id': 42, 'head_sha': SHA, 'head_repository': {'full_name': 'rdidale-jpg/CIOS'},
                                   'event': 'pull_request', 'status': 'completed', 'conclusion': 'success'}]},
        'jobs': {'jobs': [{'name': 'FLORA security and regression gate', 'conclusion': 'success',
                          'steps': [{'name': name, 'conclusion': 'success'} for name in sorted(REQUIRED_STEPS)]}]}}


class API:
    def __init__(self, data): self.data = data; self.paths = []; self.heads = 0
    def get(self, path):
        self.paths.append(path)
        if '/commits/' in path:
            self.heads += 1
            return self.data.get('second_head', self.data['head']) if self.heads > 1 else self.data['head']
        if '/compare/' in path: return self.data['comparison']
        if '/environments/' in path: return self.data['policy']
        if '/workflows/' in path: return self.data['runs']
        if '/jobs?' in path: return self.data['jobs']
        raise AssertionError('Unexpected read: ' + path)


class ReleasePreflight(unittest.TestCase):
    def assert_not_ready(self, data):
        with self.assertRaises(NotReady): check(API(data), SHA, 'main')

    def test_success_is_read_only_not_a_production_go_or_deploy(self):
        api = API(fixture()); result = check(api, SHA, 'main')
        self.assertEqual(result['validation_run_id'], 42)
        self.assertFalse(result['render_deployed'])
        self.assertIn('UNVERIFIED', result['production_readiness'])
        self.assertTrue(all(p.startswith(PREFIX + '/') for p in api.paths))
        self.assertEqual(api.heads, 2)

    def test_ambiguous_commit_or_injection_rejected_before_network(self):
        for sha in ['main', SHA[:12], SHA + '\n', 'A' * 40, '$(secret)']:
            api = API(fixture())
            with self.assertRaises(NotReady): check(api, sha, 'main')
            self.assertEqual(api.paths, [])

    def test_invalid_branch_or_cross_repository_scope_denied(self):
        for branch in ['../main', 'main;whoami', 'a//b', 'main\n', 'x/.git']:
            with self.assertRaises(NotReady): validate_inputs(SHA, branch, 'rdidale-jpg/CIOS', 'flora-production')
        with self.assertRaises(NotReady): validate_inputs(SHA, 'main', 'someone/else', 'flora-production')
        with self.assertRaises(NotReady): validate_inputs(SHA, 'main', 'rdidale-jpg/CIOS', 'unprotected')

    def test_head_must_be_the_exact_typed_commit(self):
        data = fixture(); data['head']['sha'] = 'b' * 40; self.assert_not_ready(data)

    def test_branch_drift_after_checks_denied(self):
        data = fixture(); data['second_head'] = {'sha': 'b' * 40}; self.assert_not_ready(data)

    def test_old_or_diverged_main_cannot_be_released_as_new_candidate(self):
        for status in ['behind', 'diverged', None]:
            data = fixture(); data['comparison']['status'] = status; self.assert_not_ready(data)

    def test_environment_without_required_independent_review_is_denied(self):
        for policy in [{}, {'protection_rules': []}, {'protection_rules': [{'type': 'required_reviewers', 'reviewers': []}]}]:
            data = fixture(); data['policy'] = policy; self.assert_not_ready(data)
        data = fixture(); data['policy']['protection_rules'][0]['prevent_self_review'] = False; self.assert_not_ready(data)

    def test_missing_wrong_sha_or_foreign_repo_validation_cannot_authorise_release(self):
        for change in ['missing', 'sha', 'repository']:
            data = fixture()
            if change == 'missing': data['runs']['workflow_runs'] = []
            elif change == 'sha': data['runs']['workflow_runs'][0]['head_sha'] = 'b' * 40
            else: data['runs']['workflow_runs'][0]['head_repository']['full_name'] = 'elsewhere/repo'
            self.assert_not_ready(data)

    def test_latest_failure_cannot_fall_back_to_old_green_run(self):
        data = fixture(); newer = deepcopy(data['runs']['workflow_runs'][0]); newer.update(id=43, conclusion='failure')
        data['runs']['workflow_runs'].append(newer); self.assert_not_ready(data)

    def test_pending_cancelled_and_incomplete_runs_denied(self):
        for status, conclusion in [('in_progress', None), ('completed', 'cancelled'), ('queued', None)]:
            data = fixture(); data['runs']['workflow_runs'][0].update(status=status, conclusion=conclusion); self.assert_not_ready(data)

    def test_skipped_or_absent_security_technology_or_offers_gate_denied(self):
        for name in REQUIRED_STEPS:
            data = fixture()
            for step in data['jobs']['jobs'][0]['steps']:
                if step['name'] == name: step['conclusion'] = 'skipped'
            self.assert_not_ready(data)
        data = fixture(); data['jobs']['jobs'] = []; self.assert_not_ready(data)

    def test_github_read_failure_propagates_without_any_deploy(self):
        class Unavailable:
            def get(self, path): raise NotReady('GitHub read unavailable')
        with self.assertRaises(NotReady): check(Unavailable(), SHA, 'main')


class ReleaseTransport(unittest.TestCase):
    def test_transport_only_reads_fixed_github_origin_and_refuses_redirects(self):
        import io
        from unittest.mock import patch
        from tools.ci.flora_release_preflight import GitHub
        with patch('urllib.request.build_opener') as build:
            build.return_value.open.return_value.__enter__.return_value = io.StringIO('{}')
            GitHub('synthetic-fixture-token').get(PREFIX + '/commits/main')
            request = build.return_value.open.call_args.args[0]
            self.assertEqual(request.get_method(), 'GET')
            self.assertEqual(request.full_url, 'https://api.github.com' + PREFIX + '/commits/main')
            handler = build.call_args.args[0]
            self.assertIsNone(handler.redirect_request(None, None, 302, '', {}, 'https://another-host.invalid'))

    def test_transport_failure_never_prints_token_or_response_body(self):
        from urllib.error import HTTPError
        from unittest.mock import patch
        from tools.ci.flora_release_preflight import GitHub
        with patch('urllib.request.build_opener') as build:
            build.return_value.open.side_effect = HTTPError('https://api.github.com', 403, 'sensitive response', {}, None)
            with self.assertRaises(NotReady) as error:
                GitHub('synthetic-fixture-token').get(PREFIX + '/commits/main')
            self.assertEqual(str(error.exception), 'GitHub read verification failed (HTTP 403).')
