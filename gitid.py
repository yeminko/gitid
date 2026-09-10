#!/usr/bin/env python3

from typing import Literal
import time
import subprocess
import threading
import os
import sys
import argparse
from argparse import ArgumentParser
from pathlib import Path


def spinner(stop_event, start_time) -> None:
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    index = 0
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        frame = frames[index]

        print(f"\r{frame} Searching... {elapsed:.1f}s", end="", flush=True)
        index += 1

        if index >= len(frames):
            index = 0

        time.sleep(0.1)


def search_git_repositories(search_path) -> list[Path]:
    repo_paths: list[Path] = []
    start_time = time.time()
    stop_event = threading.Event()

    spinner_thread = threading.Thread(
        target=spinner, args=(stop_event, start_time), daemon=True)
    spinner_thread.start()

    try:
        IGNORED: set[str] = {"node_modules", "venv", ".venv", "env",
                             "__pycache__", ".Trash", "Library", ".cache"}

        for root, dirs, files in os.walk(search_path):
            dirs[:] = [d for d in dirs if d not in IGNORED]
            if ".git" in dirs:
                repo_paths.append(Path(root))
                # Remove the ".git" directory from the list to prevent descending into it
                dirs.remove(".git")
    finally:
        stop_event.set()
        spinner_thread.join(timeout=0.5)
        # Clean up the spinner line output
        print("\r" + " " * 40 + "\r", end="", flush=True)
        elapsed = time.time() - start_time
        print(f"Total elapsed time: {elapsed:.1f}s")

    return sorted(repo_paths)


def get_git_info(repo_path: Path, key: str) -> str:
    command = ["git", "-C", str(repo_path), "config", "--local", key]
    result = subprocess.run(command, capture_output=True, text=True)

    value = result.stdout.strip() if result.returncode == 0 else "(not set)"
    return value


def get_git_username(repo_path: Path) -> str:
    return get_git_info(repo_path, "user.name")


def get_git_email(repo_path: Path) -> str:
    return get_git_info(repo_path, "user.email")


def update_git_info(repo_path: Path, key: str, value: str) -> None:
    command = ["git", "-C", str(repo_path), "config", "--local", key, value]
    subprocess.run(command, capture_output=True, text=True)


def update_git_username(repo_path: Path, username: str) -> None:
    update_git_info(repo_path, "user.name", username)


def update_git_email(repo_path: Path, email: str) -> None:
    update_git_info(repo_path, "user.email", email)


def update_all_repos(repo_paths: list[Path], username: str, email: str) -> None:
    for repo_path in repo_paths:
        update_git_username(repo_path, username)
        update_git_email(repo_path, email)
    print(f"\nUpdated {len(repo_paths)} repositories.")


def update_specific_repo(repo_path: Path, username: str, email: str) -> None:
    update_git_username(repo_path, username)
    update_git_email(repo_path, email)
    print(f"\nUpdated repository: {repo_path}")


def display_repos(repo_paths: list[Path]) -> None:
    print(f"Found {len(repo_paths)} Git repository(ies).")
    print(f"\n{'#':<4} {'Path':<60} {'Username':<25} {'Email'}")
    print("-" * 120)

    for idx, repo_path in enumerate(repo_paths, start=1):
        username = get_git_username(repo_path)
        email = get_git_email(repo_path)

        path_str = str(repo_path)
        if len(path_str) > 58:
            path_str = "..." + path_str[-55:]
        print(f"{idx:<4} {path_str:<60} {username:<25} {email}")


def create_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(description="Git Identity Manager")

    parser.add_argument("path", type=str, nargs="?", default=str(Path.home()),
                        help="Specify a path to search for Git repositories (default: home directory)")

    return parser


def search_repos(path: str) -> list[Path]:
    print(f"Searching for Git repositories in: {path}")
    repo_paths = search_git_repositories(path)
    return repo_paths


def get_update_scope() -> Literal["ALL", "SPECIFIC"]:
    print("\nOptions:")
    print("  [1] Update username and email for ALL repositories")
    print("  [2] Update username and email for a SPECIFIC repository")
    print("  [q] Quit")

    choice = input("\nEnter your choice: ").strip().lower()

    if choice == "q":
        sys.exit(0)

    if choice not in ("1", "2"):
        print("Invalid choice.")
        sys.exit(1)

    if choice == "1":
        choice = "ALL"
    elif choice == "2":
        choice = "SPECIFIC"
    else:
        print("Invalid choice.")
        sys.exit(1)


def get_username_email() -> tuple[str, str]:
    username = input("Enter new username: ").strip()
    email = input("Enter new email: ").strip()

    if not username or not email:
        print("Username and email cannot be empty.")
        sys.exit(1)

    return username, email


def get_update_target():
    print("\nWhat would you like to update?")
    print("  [1] Username")
    print("  [2] Email")
    print("  [3] Both")

    choice = input("\nEnter your choice: ").strip()

    if choice not in ("1", "2", "3"):
        print("Invalid choice.")
        sys.exit(1)

    if choice == "1":
        return "USERNAME"
    elif choice == "2":
        return "EMAIL"
    elif choice == "3":
        return "BOTH"
    else:
        print("Invalid choice.")
        sys.exit(1)


def update_all_repos_interactive(repo_paths: list[Path]) -> None:
    choice = get_update_target()

    if choice == "USERNAME":
        username, _ = get_username_email()
        update_all_repos(repo_paths, username, None)
    elif choice == "EMAIL":
        _, email = get_username_email()
        update_all_repos(repo_paths, None, email)
    elif choice == "BOTH":
        update_all_repos(repo_paths, username, email)


def main():
    parser = create_parser()
    args = parser.parse_args()
    args_path = args.path

    repo_paths = search_repos(args_path)

    if not repo_paths:
        print("No Git repositories found.")
        return

    display_repos(repo_paths)
    scope = get_update_scope()

    if scope == "ALL":
        update_all_repos_interactive(repo_paths)
    elif scope == "SPECIFIC":
        try:
            repo_number = int(
                input(f"Enter repository number (1-{len(repo_paths)}): ").strip())

            if repo_number < 1 or repo_number > len(repo_paths):
                print("Invalid repository number.")
                return

        except ValueError:
            print("Invalid number.")
            return

        index = repo_number - 1
        update_specific_repo(repo_paths[index], username, email)

    username = input("Enter new username: ").strip()
    email = input("Enter new email: ").strip()

    if not username or not email:
        print("Username and email cannot be empty.")
        return

    print("\nUpdated repository list:")
    display_repos(repo_paths)


if __name__ == "__main__":
    main()
