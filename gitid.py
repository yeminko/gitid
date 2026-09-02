#!/usr/bin/env python3

import subprocess
import threading
import time
import os
import argparse
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
    print(f"\n{'#':<4} {'Path':<60} {'Username':<25} {'Email'}")
    print("-" * 120)

    for idx, repo_path in enumerate(repo_paths, start=1):
        username = get_git_username(repo_path)
        email = get_git_email(repo_path)

        path_str = str(repo_path)
        if len(path_str) > 58:
            path_str = "..." + path_str[-55:]
        print(f"{idx:<4} {path_str:<60} {username:<25} {email}")


def show_options():
    print("\nOptions:")
    print("  [1] Update username and email for ALL repositories")
    print("  [2] Update username and email for a SPECIFIC repository")
    print("  [q] Quit")


def main():
    parser = argparse.ArgumentParser(description="Git Identity Manager")

    parser.add_argument("path", type=str, nargs="?", default=str(Path.home()),
                        help="Specify a path to search for Git repositories (default: home directory)")

    args = parser.parse_args()

    print(f"Searching for Git repositories in: {args.path}")
    repo_paths = search_git_repositories(args.path)

    if not repo_paths:
        print("No Git repositories found.")
        return

    print(f"Found {len(repo_paths)} Git repository(ies).")
    display_repos(repo_paths)

    show_options()

    choice = input("\nEnter your choice: ").strip().lower()

    if choice == "q":
        return

    if choice not in ("1", "2"):
        print("Invalid choice.")
        return

    if choice == "1":
        update_all_repos(repo_paths, username, email)
    elif choice == "2":
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
