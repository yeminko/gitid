import subprocess
import threading
import time
import os
from pathlib import Path
import argparse


def search_all_git_repositories(search_path=None):
    if search_path is None:
        search_path = Path.home()
    else:
        search_path = Path(search_path)

    repo_paths = []
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


def spinner(stop_event, start_time):
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


def run_git_config(repo_path, key, value=None):
    cmd = ["git", "-C", str(repo_path), "config", "--local", key]
    if value is not None:
        cmd.append(value)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if value is not None:
        return result.returncode == 0

    return result.stdout.strip() if result.returncode == 0 else None


def get_repo_identity(repo_path):
    username = run_git_config(repo_path, "user.name")
    email = run_git_config(repo_path, "user.email")
    return username, email


def display_repos(repo_paths):
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
    for repo_path in repo_paths:
        run_git_config(repo_path, "user.name", username)
        run_git_config(repo_path, "user.email", email)
    print(f"\nUpdated {len(repo_paths)} repositories.")


def update_specific_repo(repo_paths, index, username, email):
    if index < 1 or index > len(repo_paths):
        print("Invalid repository number.")
        return

    repo_path = repo_paths[index - 1]
    run_git_config(repo_path, "user.name", username)
    run_git_config(repo_path, "user.email", email)
    print(f"\nUpdated repository: {repo_path}")


def main():
    parser = argparse.ArgumentParser(description="Git Identity Manager")

    parser.add_argument("--path", type=str,
                        help="Specify a path to search for Git repositories (default: home directory)")

    args = parser.parse_args()

    if args.path:
        print(f"Searching for Git repositories in: {args.path}")
        repo_paths = search_all_git_repositories(args.path)
    else:
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
