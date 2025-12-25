# Markdown File Structure

Donezenn tracks markdown files (by extension .md) to automate common actions such as state changes.
The structure of a TODO file is built around Markdown check boxes.

A task list can be defined by using a bullet with check box:
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
