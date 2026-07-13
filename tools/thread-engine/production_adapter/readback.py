from __future__ import annotations

from typing import Any

REVIEW_THREAD_QUERY = """query($owner:String!,$name:String!,$head:String!){
  repository(owner:$owner,name:$name){
    pullRequests(first:2,states:OPEN,headRefName:$head){
      nodes{
        number
        headRefName
        reviewThreads(first:1){
          totalCount
        }
      }
    }
  }
}"""


class ReadbackError(Exception):
    def __init__(self, message: str, code: str = "READBACK_MISMATCH") -> None:
        super().__init__(message)
        self.code = code


def _commit_oid(commit: dict[str, Any]) -> str | None:
    return commit.get("oid") or commit.get("sha")


def verify_pr_readback(
    readback: dict[str, Any],
    *,
    mission_branch: str,
    base_sha: str,
    head_sha: str,
    title: str,
    body: str,
    declared_paths: tuple[str, ...],
    expected_commit_count: int = 1,
) -> int:
    number = readback.get("number")
    url = readback.get("url")
    if not isinstance(number, int) or number <= 0 or not isinstance(url, str) or not url.startswith("https://github.com/Jktomy/atlas-prime/pull/"):
        raise ReadbackError("PR number or URL is absent")
    if readback.get("state") != "OPEN":
        raise ReadbackError("PR state is not OPEN")
    if readback.get("isDraft") is not True:
        raise ReadbackError("PR is not draft")
    if readback.get("baseRefName") != "main":
        raise ReadbackError("PR base branch is not main")
    if readback.get("baseRefOid") != base_sha:
        raise ReadbackError("PR base SHA mismatch")
    if readback.get("headRefName") != mission_branch:
        raise ReadbackError("PR head branch mismatch")
    if readback.get("headRefOid") != head_sha:
        raise ReadbackError("PR head SHA mismatch")
    if readback.get("title") != title:
        raise ReadbackError("PR title mismatch")
    if readback.get("body") != body:
        raise ReadbackError("PR body mismatch")
    commits = readback.get("commits")
    if not isinstance(commits, list) or len(commits) != expected_commit_count:
        raise ReadbackError("PR commit count mismatch")
    if commits and _commit_oid(commits[-1]) != head_sha:
        raise ReadbackError("PR commit head mismatch")
    files = readback.get("files")
    if not isinstance(files, list):
        raise ReadbackError("PR files missing")
    observed_paths = sorted(item.get("path") for item in files)
    if observed_paths != sorted(declared_paths):
        raise ReadbackError("PR changed-file set mismatch")
    if readback.get("comments") not in ([], None):
        raise ReadbackError("unexpected PR comments")
    if readback.get("reviews") not in ([], None):
        raise ReadbackError("unexpected PR reviews")
    return number


def verify_review_thread_readback(readback: dict[str, Any], *, expected_pr_number: int, mission_branch: str) -> int:
    if readback.get("errors"):
        raise ReadbackError("GraphQL review-thread readback returned errors")
    data = readback.get("data")
    if not isinstance(data, dict):
        raise ReadbackError("GraphQL data missing")
    repository = data.get("repository")
    if not isinstance(repository, dict):
        raise ReadbackError("GraphQL repository data missing")
    pull_requests = repository.get("pullRequests")
    if not isinstance(pull_requests, dict):
        raise ReadbackError("GraphQL pullRequests data missing")
    nodes = pull_requests.get("nodes")
    if not isinstance(nodes, list):
        raise ReadbackError("GraphQL PR nodes missing")
    if len(nodes) != 1:
        raise ReadbackError("GraphQL PR match count mismatch")
    node = nodes[0]
    if not isinstance(node, dict):
        raise ReadbackError("GraphQL PR node malformed")
    if node.get("number") != expected_pr_number:
        raise ReadbackError("GraphQL PR number mismatch")
    if node.get("headRefName") != mission_branch:
        raise ReadbackError("GraphQL PR head branch mismatch")
    review_threads = node.get("reviewThreads")
    if not isinstance(review_threads, dict):
        raise ReadbackError("GraphQL reviewThreads data missing")
    count = review_threads.get("totalCount")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ReadbackError("GraphQL review-thread count invalid")
    if count != 0:
        raise ReadbackError("unexpected PR review threads")
    return count
