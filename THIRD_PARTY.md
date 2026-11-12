# Third-party material

Code copied from other projects, with its origin and license.

## cleanyourtv: Android core regexes

- **What:** the `CORE_RE` and `CORE_OK` constants in `scripts/plan_android.py` are
  copied **verbatim**, including the origin note in the comment.
- **Origin:** [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv),
  file `tools/disable.sh`, lines 68-69, pinned commit
  `6e8615eb0be0e843ceeebedae246d69f3e0a88d7` (verified with `git rev-parse HEAD`).
- **License:** MIT, Copyright (c) 2026 Gathin.
- **Why it matters:** this is the only part where the call on "what is core" is not
  mine. If cleanyourtv fixes its regexes, check them again against that commit
  before changing them here.

## free-my-tv: factory menu pattern

- **What:** `FACTORY_RE` in `scripts/plan_android.py`, taken from the `FACTORY` pattern.
- **Origin:** [simbasjungles/free-my-tv](https://github.com/simbasjungles/free-my-tv),
  file `app/src/io/freemytv/HomeMode.java`.
- **License:** MIT, Copyright (c) 2026 Free My TV contributors.

The full text of each MIT license is in the LICENSE file of its repository.
