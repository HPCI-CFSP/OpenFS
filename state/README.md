# Runtime State

`state/STOP` is the repository kill switch. The Run Controller checks it before
creating work, and production promotion must check it again before writing
canonical data.

`state/locks/` contains short-lived exclusive lease locks and is ignored by Git.
