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

# Markdown File Structure

Donezenn tracks markdown files (by extension .md) to automate common actions such as state changes.
The structure of a TODO file is built around Markdown check boxes.

A task list can be defined by using a unnumbered list with check box:
```
- [ ] Task
```

Tasks can be grouped under headers:
```
# TODO
- [ ] Laundry
```

Tasks can have tags associated to them:
```
- [ ] Pay the bills [Home]
```

Some headers have special functionality. For example, TBD can have a relative date which will be normalized:
```
- [ ] Pay the bills [TBD:Tomorrow]
```

Will be converted to:
```
- [ ] Pay the bills [TBD:2024-11-25]
```

Task status can be used to move to a different group by creating headers with special start token in the format of a filled checkbox. For example:

```
# [+] Done
```

Changing a task to the status [+] such as:
```
- [+] Pay the bills [TBD:2024-11-25]
```

Will move it under the relevant header:
```
# [+] Done
- [+] Pay the bills [TBD:2024-11-25]
```

If a task was under a header, when moving to a section, the header will be added as a tag. For example:
```
# Home
- [ ] Pay the bills
```
Setting the status to [+] will:
```
# [+] Done
- [+] Pay the bills [Home]

Status changes without section headers will  not move the task
