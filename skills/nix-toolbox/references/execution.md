# Execution contracts

## Scope before execution

Apply the user's already granted scope. Do not ask again for routine actions
inside it. Before running a command, identify its source, working directory,
output, and side effects. File inspection, Nix evaluation, builds, environment
hooks, publication, activation, disk changes, and reboot have different effects.

When the user requires an unchanged checkout, use an export/scratch directory
for tools that write files. `git archive HEAD` omits uncommitted and untracked
work: use it only if that is the desired input. Do not indiscriminately copy
ignored files, deployment state, credentials, or secrets into scratch.

Use `--no-write-lock-file` to avoid lock edits and `--no-link` for builds that
must avoid a result symlink. These flags do not prevent arbitrary tool/script
writes. Review shell hooks, test caches, `tofu init`, `packer init`, direnv, and
other init commands. Keep test cwd/import context explicit.

Nix evaluation may fetch inputs and create store/cache entries. A build may
invoke configured remote builders and post-build hooks. Inspect only the needed
non-secret settings, e.g. `nix config show builders` and
`nix config show post-build-hook`; do not dump all config or environment variables.
Resolve indirections to relevant configuration without reading unrelated secrets.
When the test must stay local, use `--option builders ''` for that invocation.
This does not suppress every daemon-side effect; check hooks and context too.
Use `--offline` only when needed inputs and dependencies are already available.

## Platforms and store locality

For a remote task, record:

| Role | Required fact |
| --- | --- |
| Controller/evaluator | Host and exact Nix output selected |
| Builder | Native architecture, connection, allowed cost/concurrency |
| Source store | Where the realized output and closure actually exist |
| Target store | Where the consumer/installer requires the closure |
| Activation host | Host whose running system will change |

Check the derivation's `.system`. A wrapper's `--system` flag may select only a
builder. It does not prove that an implicit `.#default` selects the right output.
Evaluation on x86_64 of an ARM derivation is not an ARM runtime test.

Check path validity on the store that will consume it. A derivation path is not
the realized output; a realized output alone does not prove its entire closure
is available on a target. Use explicit store URLs and transfer/verify closures
when the workflow requires it. Do not infer locality from an identical-looking
`/nix/store` path string.

## Cache and CI

Separate cache consumer and publisher roles. Consumers normally require a
cache URL and public signature keys, not AWS credentials or private signing
keys. Respect the daemon's trust owner; avoid broad `trusted-users` changes.
On NixOS use the existing declarative configuration when host changes are in
scope; on other Linux inspect who manages the Nix daemon's configuration.

Inspect existing workflows before adding a service. Keep fork/untrusted code
away from privileged runners, secrets, publication, and paid builders. Maintain
cleanup on failure/cancellation, bounded timeouts/concurrency, and cost controls.
Separate build validation from deployment and cache publication when assessing
what a passing check proves.

## NixOS installation and activation

Build, closure transfer, activation, boot and reboot are separate steps. Verify
the actual installed wrapper/tool version and local preconditions before a
remote install. New installation and existing-machine cloning need different
disk/firmware treatment. Preserve the user's disk/EFI requirements, access path,
previous generation, and rollback plan. Use a VM/snapshot rehearsal when needed.
Never interpret permission to investigate as permission to repartition or reboot.

## Optional delegation

Use one agent for tightly coupled changes. Delegate independent questions only
when the task warrants the cost and the host's authorization permits spawning.
Suitable questions: identify exact target-pin options; explain a failing drv;
review CI cleanup; independently check the resulting diff.

Pass: question, relevant files/commit, target pin/system, actions allowed,
actions excluded by the user, and return format. Ask for command + cwd + exit
code + finding + unverified claims. Avoid passing private deployment state.
Keep writers disjoint or centralize edits. Verify results before acting on them.
No fixed provider/model name is required: use available permitted capabilities.
