#!/usr/bin/env python3
"""Read-only owner release preflight. This program cannot deploy to Render.

Runs trusted workflow code, never candidate code. No Render token/service ID,
HTTP mutation, environment change or production data access is supported.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request

REPOSITORY = 'rdidale-jpg/CIOS'
ENVIRONMENT = 'flora-production'
REQUIRED_STEPS = frozenset({
    'Test CI gate failure behaviour',
    'Run strict security and versioned regression comparison',
    'Test approved Technology owner journey',
    'Test controlled Offers pilot',
})


class NotReady(ValueError):
    """Bounded, non-sensitive reason why release eligibility was not established."""


def validate_inputs(sha, branch, repository, environment):
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise NotReady('Use one full lowercase 40-character commit SHA, never a branch or tag.')
    if (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{0,127}', branch)
            or any(x in branch for x in ('..', '//', '/.')) or branch.endswith(('/', '.'))):
        raise NotReady('Use a literal valid deployment branch name.')
    if repository != REPOSITORY or environment != ENVIRONMENT:
        raise NotReady('This helper is scoped to CIOS and the reviewed flora-production environment.')


class GitHub:
    def __init__(self, token):
        if not token:
            raise NotReady('A read-only GitHub token is required; provide it through the workflow environment.')
        self.token = token

    def get(self, path):
        # Only this fixed HTTPS origin is reachable. Redirects are refused so a
        # credential can never follow a response onto a different origin.
        from urllib.request import HTTPRedirectHandler, build_opener
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        request = Request('https://api.github.com' + path, headers={
            'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'flora-owner-release-preflight'})
        try:
            with build_opener(NoRedirect).open(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            raise NotReady('GitHub read verification failed (HTTP ' + str(exc.code) + ').') from None
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            raise NotReady('GitHub read verification unavailable; no release eligibility established.') from None


def check(api, sha, branch, repository=REPOSITORY, environment=ENVIRONMENT):
    validate_inputs(sha, branch, repository, environment)
    prefix = '/repos/' + repository
    current = api.get(prefix + '/commits/' + quote(branch, safe=''))
    if current.get('sha') != sha:
        raise NotReady('Deployment branch HEAD drifted or does not equal the typed SHA.')
    ancestry = api.get(prefix + '/compare/main...' + sha)
    if ancestry.get('status') not in {'ahead', 'identical'}:
        raise NotReady('Candidate must contain current main; revalidate after any base change.')
    policy = api.get(prefix + '/environments/' + quote(environment, safe=''))
    reviewers = next((r for r in policy.get('protection_rules', []) if r.get('type') == 'required_reviewers'), {})
    if not reviewers.get('reviewers') or reviewers.get('prevent_self_review') is not True:
        raise NotReady('Configure required human environment reviewers with self-review prevented first.')
    query = urlencode({'head_sha': sha, 'per_page': 100})
    runs = api.get(prefix + '/actions/workflows/flora-validation.yml/runs?' + query).get('workflow_runs', [])
    runs = [r for r in runs if r.get('head_sha') == sha and r.get('event') in {'push', 'pull_request', 'workflow_dispatch'}
            and r.get('head_repository', {}).get('full_name') == repository]
    if not runs:
        raise NotReady('No canonical FLORA validation run exists for the exact candidate SHA.')
    latest = max(runs, key=lambda r: r['id'])
    if latest.get('status') != 'completed' or latest.get('conclusion') != 'success':
        raise NotReady('Latest exact-SHA FLORA validation is not completed successfully.')
    jobs = api.get(prefix + '/actions/runs/' + str(latest['id']) + '/jobs?filter=latest&per_page=100').get('jobs', [])
    job = next((j for j in jobs if j.get('name') == 'FLORA security and regression gate'), {})
    passed = {s.get('name') for s in job.get('steps', []) if s.get('conclusion') == 'success'}
    if job.get('conclusion') != 'success' or not REQUIRED_STEPS <= passed:
        raise NotReady('The full security, baseline, Technology and Offers steps must all pass; skipped gates do not count.')
    # Read again after the network checks and again in the approved job. This
    # detects drift; it does not lock a branch or pin Render's latest-head action.
    if api.get(prefix + '/commits/' + quote(branch, safe='')).get('sha') != sha:
        raise NotReady('Deployment branch changed during preflight; stop and revalidate.')
    return {'candidate_sha': sha, 'branch': branch, 'validation_run_id': latest['id'],
        'environment': environment, 'repository': repository, 'read_only_preflight': 'passed',
        'production_readiness': 'UNVERIFIED — owner Render checks still required', 'render_deployed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sha', required=True)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--environment', default=ENVIRONMENT)
    args = parser.parse_args()
    try:
        result = check(GitHub(os.getenv('GITHUB_TOKEN', '')), args.sha, args.branch,
                       os.getenv('GITHUB_REPOSITORY', REPOSITORY), args.environment)
    except NotReady as exc:
        print('NO-GO: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as handle:
            handle.write('### Read-only FLORA release preflight\n\nCommit `' + result['candidate_sha']
                + '`; branch `' + result['branch'] + '`; validation run ' + str(result['validation_run_id'])
                + '.\n\n**No Render deployment occurred. Production readiness remains unverified by this helper.**\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
