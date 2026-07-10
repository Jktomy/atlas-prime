from __future__ import annotations
import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable
from oathbringer_core import GitHubApiError, _require

class GitHubClient:

    def __init__(self, token: str, repository: str, *, api_url: str='https://api.github.com') -> None:
        _require(bool(token), 'GitHub token is required')
        self.token = token
        self.repository = repository
        self.api_url = api_url.rstrip('/')

    def request(self, method: str, path: str, payload: dict[str, Any] | list[Any] | None=None, *, expected: Iterable[int]=(200,), allow_404: bool=False) -> Any:
        url = f'{self.api_url}{path}'
        data = None if payload is None else json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(url, data=data, method=method, headers={'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {self.token}', 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Atlas-Oathbringer/2.0', 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                if response.status not in set(expected):
                    raise GitHubApiError(f'unexpected GitHub status {response.status}: {method} {path}')
                return None if not body else json.loads(body.decode('utf-8'))
        except urllib.error.HTTPError as exc:
            if allow_404 and exc.code == 404:
                return None
            body = exc.read().decode('utf-8', errors='replace')
            raise GitHubApiError(f'GitHub API {exc.code} for {method} {path}: {body[:500]}') from exc
        except urllib.error.URLError as exc:
            raise GitHubApiError(f'GitHub transport failed for {method} {path}: {exc}') from exc

    @property
    def repo_path(self) -> str:
        return f'/repos/{self.repository}'

    def get_authenticated_user(self) -> dict[str, Any]:
        return self.request('GET', '/user')

    def get_ref(self, branch: str) -> dict[str, Any] | None:
        encoded = urllib.parse.quote(branch, safe='')
        return self.request('GET', f'{self.repo_path}/git/ref/heads/{encoded}', allow_404=True)

    def get_commit(self, sha: str) -> dict[str, Any]:
        return self.request('GET', f'{self.repo_path}/git/commits/{sha}')

    def get_tree(self, tree_sha: str) -> tuple[str, dict[str, dict[str, Any]]]:
        response = self.request('GET', f'{self.repo_path}/git/trees/{tree_sha}?recursive=1')
        _require(response.get('truncated') is not True, 'GitHub recursive tree response was truncated')
        entries = {str(item['path']): {'sha': item.get('sha'), 'mode': item.get('mode'), 'type': item.get('type')} for item in response.get('tree', []) if item.get('type') == 'blob'}
        return (str(response['sha']), entries)

    def get_tree_for_commit(self, commit_sha: str) -> tuple[str, dict[str, dict[str, Any]]]:
        commit = self.get_commit(commit_sha)
        return self.get_tree(str(commit['tree']['sha']))

    def create_blob(self, content: bytes) -> str:
        response = self.request('POST', f'{self.repo_path}/git/blobs', {'content': base64.b64encode(content).decode('ascii'), 'encoding': 'base64'}, expected=(201,))
        return str(response['sha'])

    def create_tree(self, base_tree_sha: str, elements: list[dict[str, Any]]) -> str:
        response = self.request('POST', f'{self.repo_path}/git/trees', {'base_tree': base_tree_sha, 'tree': elements}, expected=(201,))
        return str(response['sha'])

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        response = self.request('POST', f'{self.repo_path}/git/commits', {'message': message, 'tree': tree_sha, 'parents': [parent_sha]}, expected=(201,))
        return str(response['sha'])

    def create_ref(self, branch: str, sha: str) -> None:
        self.request('POST', f'{self.repo_path}/git/refs', {'ref': f'refs/heads/{branch}', 'sha': sha}, expected=(201,))

    def update_ref(self, branch: str, sha: str) -> None:
        encoded = urllib.parse.quote(branch, safe='')
        self.request('PATCH', f'{self.repo_path}/git/refs/heads/{encoded}', {'sha': sha, 'force': False}, expected=(200,))

    def find_open_pull_requests(self, branch: str, base_branch: str) -> list[dict[str, Any]]:
        owner = self.repository.split('/', 1)[0]
        query = urllib.parse.urlencode({'state': 'open', 'head': f'{owner}:{branch}', 'base': base_branch})
        return self.request('GET', f'{self.repo_path}/pulls?{query}')

    def create_pull_request(self, branch: str, base_branch: str, contract: dict[str, Any]) -> dict[str, Any]:
        return self.request('POST', f'{self.repo_path}/pulls', {'title': contract['title'], 'body': contract.get('body', ''), 'head': branch, 'base': base_branch, 'draft': True}, expected=(201,))

    def get_pull_request(self, number: int) -> dict[str, Any]:
        return self.request('GET', f'{self.repo_path}/pulls/{number}')

    def list_pull_request_files(self, number: int) -> list[dict[str, Any]]:
        page = 1
        result: list[dict[str, Any]] = []
        while True:
            batch = self.request('GET', f'{self.repo_path}/pulls/{number}/files?per_page=100&page={page}')
            result.extend(batch)
            if len(batch) < 100:
                return result
            page += 1

    def list_workflow_runs(self, head_sha: str) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode({'event': 'pull_request', 'head_sha': head_sha, 'per_page': 100})
        response = self.request('GET', f'{self.repo_path}/actions/runs?{query}')
        return list(response.get('workflow_runs', []))

    def mark_ready(self, node_id: str) -> None:
        response = self.request('POST', '/graphql', {'query': 'mutation($id:ID!){markPullRequestReadyForReview(input:{pullRequestId:$id}){pullRequest{isDraft}}}', 'variables': {'id': node_id}}, expected=(200,))
        _require(not response.get('errors'), f"GitHub GraphQL ready transition failed: {response.get('errors')}")

    def merge_pull_request(self, number: int, expected_head: str, method: str) -> dict[str, Any]:
        return self.request('PUT', f'{self.repo_path}/pulls/{number}/merge', {'sha': expected_head, 'merge_method': method}, expected=(200,))
