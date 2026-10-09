import subprocess

import gitid


def test_search_git_repositories_skips_ignored_directories(tmp_path):
    repository = tmp_path / "repo"
    nested_repository = repository / "nested"
    ignored_repository = tmp_path / "node_modules" / "ignored"

    (repository / ".git").mkdir(parents=True)
    (nested_repository / ".git").mkdir(parents=True)
    (ignored_repository / ".git").mkdir(parents=True)

    assert gitid.search_git_repositories(
        tmp_path) == [repository, nested_repository]


def test_update_git_repository_sets_local_identity(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)

    gitid.update_git_repository(repository, "Ada Lovelace", "ada@example.com")

    assert gitid.get_git_username(repository) == "Ada Lovelace"
    assert gitid.get_git_email(repository) == "ada@example.com"


def test_update_git_repository_preserves_unspecified_identity(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
    gitid.update_git_email(repository, "old@example.com")

    gitid.update_git_repository(repository, "Ada Lovelace", None)

    assert gitid.get_git_username(repository) == "Ada Lovelace"
    assert gitid.get_git_email(repository) == "old@example.com"
