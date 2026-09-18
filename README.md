# GitID

GitID is a small command-line program that helps you manage Git username and email settings across your local repositories.

It scans your home directory by default, or an optional custom directory, finds Git repositories, shows each repository's local identity, and lets you update identity values quickly.

## What this program does

- Finds all Git repositories under the selected search directory.
- Shows the local `user.name` and `user.email` for each repository.
- Lets you update the username, email, or both values for all repositories at once.
- Lets you update the username, email, or both values for one selected repository.

The search skips common dependency, virtual-environment, cache, and system directories:
`node_modules`, `venv`, `.venv`, `env`, `__pycache__`, `.Trash`, `Library`, and `.cache`.

## Important behavior

GitID updates only local repository settings using `git config --local`.

It does not change your global Git config.

## Requirements

- Homebrew installed
- Git installed

## Installation

Install with Homebrew:

```bash
brew install yeminko/tap/gitid
```

## How to update

To update GitID installed via Homebrew, run:

```bash
brew update && brew upgrade gitid
```

## How to use

Run GitID:

```bash
gitid
```

By default, GitID searches your home directory. To search a different folder, pass it as a positional argument:

```bash
gitid /path/to/folder
```

For example:

```bash
gitid ~/Projects
```

The path can be absolute or relative to your current directory.

To display command-line help:

```bash
gitid --help
```

Then:

1. The program searches for Git repositories in the selected path.
2. It prints a numbered table of repositories.
3. Choose one option:
   - `1` to update all repositories
   - `2` to update one repository
   - `q` to quit
4. If updating, choose `Username`, `Email`, or `Both`.
5. Enter the new value or values when prompted.

## Example flow

```text
gitid

Searching for Git repositories in: /Users/alice
Total elapsed time: 0.4s
Found 3 Git repository(ies).

Options:
  [1] Update Git username and/or email for ALL repositories
  [2] Update Git username and/or email for a SPECIFIC repository
  [q] Quit

Enter your choice: 2
Enter repository number (1-3): 1
What would you like to update?
  [1] Username
  [2] Email
  [3] Both

Enter your choice: 3
Enter new username: Alice
Enter new email: alice@example.com
```

## License

MIT
