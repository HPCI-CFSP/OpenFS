# Exceptions

Non-retryable failures and exhausted Work Items create structured exception
records here. Normal successful Runs should not require human review; exception
records are the input to targeted GitHub Issues and the Weekly Digest.

Run-level records also cover budget stops, kill-switch activation, and insufficient
independent Consensus capacity. These exceptions require targeted owner action;
they must not be cleared merely because a later agent retries the same inputs.
