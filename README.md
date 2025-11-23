# donezenn
A simple Markdown + git hooks driven TODO

## Configuration
The repo comes preconfigured with default section headers and actions, feel free to override and set your own

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
python3 ../donezenn/install_hooks.py
```

## Usage
The todo.md file is expected to have the following structure dictated by the config.yaml file which can be customized.

```
# TODO
- [ ] Something I should not forget [TBD:tomorrow]

# + Done
- [+] Done already

# -> Delegated
- [->] Do something really hard
```

Each header describes a state of an item, which is defined by its symbol in the prefix. Take a look at config.yaml at the default states. The system automates some common tasks using git hooks:
1. When a state is changed by setting the symbol in the checkbox, a pre-commit hook will move it to the relevant section (if one exists)
2. If a relative date is detected, it will change to normalized ISO date
3. A commit message with the actions will be prepared
