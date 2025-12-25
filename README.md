# donezenn
A simple Markdown + git hooks driven TODO

## Installation

First, clone the code. e.g.
```
git clone https://github.com/achayun/donezenn.git
```

Next up, create your TODO repo (skip if already exists)
```
mkdir todo
cd todo
git init
touch todo.md
```

Install the git hooks into the todo repo
```
cd todo
python3 ../donezenn/install_hooks.py
```

## Usage
Donezenn will track any Markdown files about to be committed (looking at extension.md). Tracking any item with checkbox in a bullet list e.g.

```
# Home
- [ ] Some house chore
- [ ] Another task

# [+] Done

```

Changing status will be moved to sections with appropriate decorator. For example, setting the task as [+] will move to the section Done
```
# Home
- [ ] Another task

# [+] Done
- [+] Some house chore [Home]

```

Each header with decorator describes a state of an item, which is defined by its symbol in the prefix. More details are in spec.md

Templates with examples can be found in the templates folder
