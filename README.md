# GitID

GitID is a small command-line program that helps you manage Git username and email settings across your local repositories.

It scans your home directory, finds Git repositories, shows each repository's local identity, and lets you update identity values quickly.

## What this program does

- Finds all Git repositories under your home folder.
- Shows the local `user.name` and `user.email` for each repository.
- Lets you update username and email for all repositories at once.
- Lets you update username and email for one selected repository.

## Important behavior

GitID updates only local repository settings using `git config --local`.

It does not change your global Git config.

## Requirements

- Python 3.7 or newer
- Homebrew installed
- Git installed

## Installation

Install with Homebrew:

```bash
brew install yeminko/tap/gitid
```

## How to use

Run GitID:

```bash
gitid
```

By default, GitID searches your home directory. To search a different folder, use `--path`:

```bash
gitid --path /path/to/folder
```

For example:

```bash
gitid --path ~/Projects
```

The path can be absolute or relative to your current directory.

Then:

1. The program searches for Git repositories in your home directory.
2. It prints a numbered table of repositories.
3. Choose one option:
   - `1` to update all repositories
   - `2` to update one repository
   - `q` to quit
4. Enter the username and email when prompted.

## Example flow

```text
gitid

Searching for all Git repositories in your home directory...
Found 3 Git repository(ies).

Options:
  [1] Update username and email for ALL repositories
  [2] Update username and email for a SPECIFIC repository
  [q] Quit

Enter your choice: 2
Enter repository number: 1
Enter new username: Alice
Enter new email: alice@example.com
```

## License

MIT
