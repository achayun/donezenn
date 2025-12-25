# TODO
- [ ] Create a planner.md view from todo.md:
      If tasks have TBD with date and range say:
      ```
      -[ ] Dentist appointment [TBD:2025-11-30T11:15/12:30]
      ```
      Generate a planner.md:
      ```
      # Sun 30 Nov
      - Mom's birthday
      - Call plumber

      11:00–11:30 |Standup     |
      11:30–12:00 |(…)         |Dentist (11:15)
      12:00-12:30 |            |(…)
      15:00–15:30 |Deep Work   |
      15:30–16:00 |(…)         |
      ```

      * Day schedule breaks time between given parametric range (say 8:00AM to 21:00PM) to single range lines of specific resolution (1/2 hour in the above example)
      * Tasks starting within time range (i.e. not on the time marker) are noted with exact start time. Example "Dentist (11:15)"
      * Tasks ending within time range  (i.e. not on the time marker) are noted with exact end time
      * Tasks taking more than a single time span are marked with (…) in the following time ranges
      * Titles are always 20 characters (monospaced) wide. Longer names are trimmed to 19 and get …
      * Full day tasks are above time range in a list of bullets
      * Tasks starting on the same time are horizontally stacked with single pipe, a task that starts at stacking position will remain in that position until it ends even if no other task exists before it.
