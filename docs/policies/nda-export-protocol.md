# NDA Export Protocol

The only supported private-to-public transfer is an approved Export Package.

An Export Package contains:

- a new public-safe statement without private identifiers;
- classification and publication labels;
- prohibited-field and DLP check results;
- transformation description without protected content;
- accountable human approver and approval time;
- public destination and expiry or review date;
- package hash and private audit reference stored only in the private plane.

The public package must not reveal private source names, private object IDs, vendor participation, access paths, or the existence of an NDA relationship unless publication is explicitly approved.

Agents may prepare a package, but only an authorized human can approve export. Failed or uncertain checks stop the transfer and create a private exception.
