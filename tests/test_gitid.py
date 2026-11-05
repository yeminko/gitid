import subprocess
import threading
from pathlib import Path

import gitid
import pytest


def test_spinner_prints_frame_and_elapsed_time(monkeypatch, capsys):
    stop_event = threading.Event()
    times = iter([0.0, 1.0])
    monkeypatch.setattr(gitid.time, "time", lambda: next(times))
    monkeypatch.setattr(gitid.time, "sleep", lambda _: stop_event.set())

    gitid.spinner(stop_event)

    assert capsys.readouterr().out == "\r⠋ Searching... 1.0s"


def test_search_git_repositories_skips_ignored_directories(tmp_path):
    repository = tmp_path / "repo"
    nested_repository = repository / "nested"
    ignored_repository = tmp_path / "node_modules" / "ignored"

    (repository / ".git").mkdir(parents=True)
    (nested_repository / ".git").mkdir(parents=True)
    (ignored_repository / ".git").mkdir(parents=True)

    assert gitid.search_git_repositories(
        tmp_path) == [repository, nested_repository]


def test_get_git_info_reads_repository_local_config(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "--local",
                   "user.name", "Ada Lovelace"], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "--local",
                   "user.email", "ada@example.com"], check=True)

    assert gitid.get_git_info(repository, 'user.name') == "Ada Lovelace"
    assert gitid.get_git_info(repository, 'user.email') == "ada@example.com"


def test_get_git_info_reads_repository_with_no_local_config(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)

    assert gitid.get_git_info(repository, 'user.name') == "(not set)"
    assert gitid.get_git_info(repository, 'user.email') == "(not set)"


def test_get_git_username_reads_repository_local_config(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "--local",
                   "user.name", "Ada Lovelace"], check=True)

    assert gitid.get_git_username(repository) == "Ada Lovelace"


def test_get_git_email_reads_repository_local_config(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "config", "--local",
                   "user.email", "ada@example.com"], check=True)

    assert gitid.get_git_email(repository) == "ada@example.com"


def test_display_git_repositories_formats_and_truncates_paths(monkeypatch, capsys):
    repositories = [Path("/repos/one"), Path("/" + "a" * 60)]
    monkeypatch.setattr(gitid, "get_git_username", lambda _: "Ada Lovelace")
    monkeypatch.setattr(gitid, "get_git_email", lambda _: "ada@example.com")

    gitid.display_git_repositories(repositories)

    output_lines = capsys.readouterr().out.splitlines()
    assert output_lines == [
        "",
        f"{'#':<4} {'Path':<60} {'Username':<25} {'Email'}",
        "-" * 120,
        f"{1:<4} {'/repos/one':<60} {'Ada Lovelace':<25} ada@example.com",
        f"{2:<4} {'...' + 'a' * 55:<60} {'Ada Lovelace':<25} ada@example.com",
    ]


def test_update_git_info_sets_local_config(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)

    gitid.update_git_info(repository, "user.name", "Ada Lovelace")
    gitid.update_git_info(repository, "user.email", "ada@example.com")

    username = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.name"],
                              check=True, capture_output=True, text=True).stdout.strip()
    email = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.email"],
                           check=True, capture_output=True, text=True).stdout.strip()

    assert username == "Ada Lovelace"
    assert email == "ada@example.com"


def test_update_git_username_sets_local_config(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)

    gitid.update_git_username(repository, "Ada Lovelace")

    username = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.name"],
                              check=True, capture_output=True, text=True).stdout.strip()

    assert username == "Ada Lovelace"


def test_update_git_email_sets_local_config(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)

    gitid.update_git_email(repository, "ada@example.com")

    email = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.email"],
                           check=True, capture_output=True, text=True).stdout.strip()

    assert email == "ada@example.com"


def test_update_git_repository_sets_local_identity(tmp_path):
    repository = tmp_path / "repo"
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)

    gitid.update_git_repository(repository, "Ada Lovelace", "ada@example.com")

    username = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.name"],
                              check=True, capture_output=True, text=True).stdout.strip()
    email = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.email"],
                           check=True, capture_output=True, text=True).stdout.strip()

    assert username == "Ada Lovelace"
    assert email == "ada@example.com"


def test_update_git_repositories_sets_local_identities(tmp_path):

    repository1 = tmp_path / "repo1"
    repository2 = tmp_path / "repo2"
    subprocess.run(["git", "init", "--quiet", str(repository1)], check=True)
    subprocess.run(["git", "init", "--quiet", str(repository2)], check=True)

    gitid.update_git_repositories(
        [repository1, repository2], "Ada Lovelace", "ada@example.com")

    for repository in [repository1, repository2]:
        username = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.name"],
                                  check=True, capture_output=True, text=True).stdout.strip()
        email = subprocess.run(["git", "-C", str(repository), "config", "--local", "user.email"],
                               check=True, capture_output=True, text=True).stdout.strip()

        assert username == "Ada Lovelace"
        assert email == "ada@example.com"


def test_create_parser_defaults_path_to_home(monkeypatch, tmp_path):
    monkeypatch.setattr(gitid.Path, "home", lambda: tmp_path)

    args = gitid.create_parser().parse_args([])

    assert args.path == str(tmp_path)


def test_create_parser_accepts_path_argument(tmp_path):
    args = gitid.create_parser().parse_args([str(tmp_path)])

    assert args.path == str(tmp_path)


def test_create_parser_displays_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        gitid.create_parser().parse_args(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr(
    ).out == f"Git Identity Manager {gitid.__version__}\n"


@pytest.mark.parametrize("choice, expected", [("1", "ALL"), ("2", "SPECIFIC")])
def test_prompt_options_returns_selected_scope(monkeypatch, choice, expected):
    monkeypatch.setattr("builtins.input", lambda _: choice)

    assert gitid.prompt_options() == expected


def test_prompt_options_quits_on_q(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "q")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_options()

    assert exc_info.value.code == 0


def test_prompt_options_exits_on_invalid_choice(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "invalid")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_options()

    assert exc_info.value.code == 1
    assert capsys.readouterr().out.endswith("Invalid choice.\n")


def test_prompt_user_returns_entered_value(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "John Doe")

    assert gitid.prompt_username() == "John Doe"


def test_prompt_user_exits_on_empty_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_username()

    assert exc_info.value.code == 1


def test_prompt_email_returns_entered_value(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "john@example.com")

    assert gitid.prompt_email() == "john@example.com"


def test_prompt_email_exits_on_empty_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_email()

    assert exc_info.value.code == 1


def test_prompt_repo_index_returns_index_value(tmp_path, monkeypatch):
    repo1 = tmp_path / "repo1"
    repo2 = tmp_path / "repo2"

    monkeypatch.setattr("builtins.input", lambda _: "2")

    assert gitid.prompt_repo_index([repo1, repo2]) == 1


def test_prompt_repo_index_exits_on_invalid_repo_number(tmp_path, monkeypatch):
    repo1 = tmp_path / "repo1"
    repo2 = tmp_path / "repo2"

    monkeypatch.setattr("builtins.input", lambda _: "3")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_repo_index([repo1, repo2])

    assert exc_info.value.code == 1


def test_prompt_repo_index_exits_on_non_numeric_input(tmp_path, monkeypatch):
    repo1 = tmp_path / "repo1"
    repo2 = tmp_path / "repo2"

    monkeypatch.setattr("builtins.input", lambda _: "abc")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_repo_index([repo1, repo2])

    assert exc_info.value.code == 1


@pytest.mark.parametrize("choice, expected", [("1", "USERNAME"), ("2", "EMAIL"), ("3", "BOTH")])
def test_prompt_update_options_returns_selected_choice(monkeypatch, choice, expected):
    monkeypatch.setattr("builtins.input", lambda _: choice)

    assert gitid.prompt_update_options() == expected


def test_prompt_update_options_exits_on_invalid_choice(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "invalid")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_update_options()

    assert exc_info.value.code == 1
    assert capsys.readouterr().out.endswith("Invalid choice.\n")


def test_prompt_update_values_returns_username(monkeypatch):
    monkeypatch.setattr(gitid, "prompt_update_options", lambda: "USERNAME")
    monkeypatch.setattr("builtins.input", lambda _: "John Doe")

    assert gitid.prompt_update_values() == ("John Doe", None)


def test_prompt_update_values_returns_email(monkeypatch):
    monkeypatch.setattr(gitid, "prompt_update_options", lambda: "EMAIL")
    monkeypatch.setattr("builtins.input", lambda _: "john@example.com")

    assert gitid.prompt_update_values() == (None, "john@example.com")


def test_prompt_update_values_returns_both(monkeypatch):
    monkeypatch.setattr(gitid, "prompt_update_options", lambda: "BOTH")
    inputs = iter(["John Doe", "john@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    assert gitid.prompt_update_values() == ("John Doe", "john@example.com")


def test_prompt_update_values_exits_on_invalid_choice(monkeypatch):
    monkeypatch.setattr(gitid, "prompt_update_options", lambda: "INVALID")

    with pytest.raises(SystemExit) as exc_info:
        gitid.prompt_update_values()

    assert exc_info.value.code == 1

# def test_update_all_interactive
