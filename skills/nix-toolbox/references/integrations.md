# Optional integrations

Read only the entry relevant to the task. These are project integration choices,
not extra tools to install by default. Preserve an existing working build system.

| Project need | Candidate and useful evidence |
| --- | --- |
| Package a Python uv workspace reproducibly | [uv2nix](https://github.com/pyproject-nix/uv2nix): inspect `pyproject.toml`/`uv.lock`, supported source types and platform dependencies; validate the actual package and runtime imports. A Python interpreter supplied by Nix alone may suffice for ordinary development. |
| Repeated Rust dependency builds across CI checks | [crane](https://github.com/ipetkov/crane): inspect `Cargo.lock`, toolchain and existing artifact reuse; measure reuse across build/test/clippy before adding complexity. |
| Test Nix-generated structured configuration | [namaka](https://github.com/nix-community/namaka): review snapshot diffs as behavior changes. Its check can create pending snapshots; accepting a new snapshot is not proof that the new result is correct. |

Pin compatible inputs and read the installed revision's API before writing an
integration. These routes have not been runtime-tested by this toolbox; test
them on the project that needs them. Cross-language conversion and framework
migration are not prerequisites for benefiting from a Nix development shell.
