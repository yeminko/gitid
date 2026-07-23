import os
import subprocess
import sys
import threading
import time
from pathlib import Path


def search_all_git_repositories():
    """
    Search for all Git repositories in the current user's home directory
    and return a sorted list of their parent directory paths.
    Shows an animated progress indicator with elapsed seconds.
    """
    home = Path.home()
    repo_paths = []
    stop_event = threading.Event()
    start_time = time.time()

    def spinner():
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while not stop_event.is_set():
            elapsed = time.time() - start_time
            frame = frames[idx % len(frames)]
            sys.stdout.write(f"\r{frame} Searching... {elapsed:.1f}s")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)

    spinner_thread = threading.Thread(target=spinner, daemon=True)
    spinner_thread.start()

    try:
        for git_dir in home.rglob(".git"):
            if not git_dir.is_dir():
                continue
            repo_paths.append(git_dir.parent)
    finally:
        stop_event.set()
        spinner_thread.join(timeout=0.5)
        # Clean up the spinner line output
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()

    return sorted(repo_paths)


def run_git_config(repo_path, key, value=None):
    """
    Get or set a git config value for a specific repository.
    If value is None, returns the current value.
    If value is provided, sets the config value.
    """
    cmd = ["git", "-C", str(repo_path), "config", "--local", key]
    if value is not None:
        cmd.append(value)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if value is not None:
        return result.returncode == 0

    return result.stdout.strip() if result.returncode == 0 else None


def get_repo_identity(repo_path):
    """
    Return (username, email) for a repository, or None values if not set.
    """
    username = run_git_config(repo_path, "user.name")
    email = run_git_config(repo_path, "user.email")
    return username, email


def display_repos(repo_paths):
    """
    Display repositories with their index, path, username, and email.
    """
    print(f"\n{'#':<4} {'Path':<60} {'Username':<25} {'Email'}")
    print("-" * 120)

    for idx, repo_path in enumerate(repo_paths, start=1):
        username, email = get_repo_identity(repo_path)
        username = username or "(not set)"
        email = email or "(not set)"
        path_str = str(repo_path)
        if len(path_str) > 58:
            path_str = "..." + path_str[-55:]
        print(f"{idx:<4} {path_str:<60} {username:<25} {email}")


def update_all_repos(repo_paths, username, email):
    """
    Update username and email for all repositories.
    """
    for repo_path in repo_paths:
        run_git_config(repo_path, "user.name", username)
        run_git_config(repo_path, "user.email", email)
    print(f"\nUpdated {len(repo_paths)} repositories.")


def update_specific_repo(repo_paths, index, username, email):
    """
    Update username and email for a specific repository by index.
    """
    if index < 1 or index > len(repo_paths):
        print("Invalid repository number.")
        return

    repo_path = repo_paths[index - 1]
    run_git_config(repo_path, "user.name", username)
    run_git_config(repo_path, "user.email", email)
    print(f"\nUpdated repository: {repo_path}")


def main():
    print("Searching for all Git repositories in your home directory...")
    repo_paths = search_all_git_repositories()

    if not repo_paths:
        print("No Git repositories found.")
        return

    print(f"Found {len(repo_paths)} Git repository(ies).")
    display_repos(repo_paths)

    print("\nOptions:")
    print("  [1] Update username and email for ALL repositories")
    print("  [2] Update username and email for a SPECIFIC repository")
    print("  [q] Quit")

    choice = input("\nEnter your choice: ").strip().lower()

    if choice == "q":
        return

    if choice not in ("1", "2"):
        print("Invalid choice.")
        return

    username = input("Enter new username: ").strip()
    email = input("Enter new email: ").strip()

    if not username or not email:
        print("Username and email cannot be empty.")
        return

    if choice == "1":
        update_all_repos(repo_paths, username, email)
    elif choice == "2":
        try:
            index = int(
                input(f"Enter repository number (1-{len(repo_paths)}): ").strip())
        except ValueError:
            print("Invalid number.")
            return
        update_specific_repo(repo_paths, index, username, email)

    print("\nUpdated repository list:")
    display_repos(repo_paths)


if __name__ == "__main__":
    main()
