# GitID

A simple Python CLI tool to discover all Git repositories under your home directory and manage their local `user.name` and `user.email` settings.

## Features

- Automatically finds all Git repositories under the user's home directory.
- Displays each repository with its current local Git identity.
- Update the username and email for **all** repositories at once.
- Update the username and email for a **specific** repository.
- Only modifies repository-local Git config (`git config --local`), leaving global settings untouched.

## Requirements

- Python 3.7+
- Git installed and available in your `PATH`

## Usage

Run the script from your terminal:

```bash
python3 gitid.py
```

The tool will:

1. Search your home directory for Git repositories.
2. Display a numbered list of repositories with their current username and email.
3. Prompt you to choose an action:
   - `[1]` Update identity for **all** repositories.
   - `[2]` Update identity for a **specific** repository.
   - `[q]` Quit without making changes.

### Example

```text
Searching for all Git repositories in your home directory...
Found 3 Git repository(ies).

#    Path                                                         Username                  Email
------------------------------------------------------------------------------------------------------------------------
1    .../projects/alpha                                           Alice                     alice@example.com
2    .../projects/beta                                            Bob                       bob@example.com
3    .../projects/gamma                                           (not set)                 (not set)

Options:
  [1] Update username and email for ALL repositories
  [2] Update username and email for a SPECIFIC repository
  [q] Quit

Enter your choice: 1
Enter new username: Alice
Enter new email: alice@example.com

Updated 3 repositories.

Updated repository list:
...
```

## How it works

- `search_all_git_repositories()` walks your home directory looking for `.git` folders.
- `run_git_config()` calls `git config --local` to read or write values.
- `display_repos()` prints a formatted table of repositories and their identities.

## Safety notes

- This tool only changes local repository config. It does **not** modify your global or system Git settings.
- Make sure you have backups or version control in place before bulk-updating many repositories.

## License

MIT
