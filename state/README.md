# Runtime State

`state/STOP` is the repository kill switch. The Run Controller checks it before
creating work, and production promotion must check it again before writing
canonical data.

`state/locks/` contains advisory lock files and is ignored by Git. Lock files may
remain after release; the operating-system lock, not file existence, determines
ownership. Run control mutations are serialized per Run while model or retrieval
work executes outside the lock.
