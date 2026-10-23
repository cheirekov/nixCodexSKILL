# Validation — 2026-10-23

Verified on Ubuntu x86_64 with Nix 2.31.4. The toolbox Nixpkgs revision is
`02c087f3fe673c9e317f206a627cb6b910336dbe`.

- Skill metadata passes the Codex skill validator.
- Inspector tests cover missing Nix, malformed/external-symlink locks, omitted
  credential-bearing URL fields, and unchanged input content.
- Installer tests cover unrelated TOML settings/comments, empty configuration,
  repeat installation, conflicting entries, and disabled server handling.
- statix/deadnix run successfully on a separate infrastructure-project export.
  Seeded issues produce JSON diagnostics without changing the input file.
- nixfmt check passes on the toolbox flake.
- A temporary locked `jq` environment runs successfully.
- `nix path-info` and `nix why-depends` expose a realized fixture's runtime closure
  and the dependency path to glibc.
- All toolbox apps evaluate for x86_64-linux and aarch64-linux.
- MCP-NixOS 3.0.1 starts over STDIO, completes MCP initialization, advertises
  `nix` and `nix_versions`, and answers a real package-info query for `jq`.
- Local installation uses a linked skill and a persistent Nix output link.
  The MCP configuration preserves unrelated existing settings.

ARM runtime, a NixOS host, automatic skill selection, and behavioral comparisons
across GPT/Qwen/GLM/DeepSeek have not been tested. These checks establish tool
availability and technical contracts, not a measured improvement in model
quality or cost. MCP channel results still need verification against project pins.

Specialized operations of nix-locate, nix-diff, nom, nix-init, nix-update, and
nix-fast-build have not been exercised; their app evaluation is the current
coverage. No remote provisioning, cache publication, activation, or reboot was
part of these checks. Full local infrastructure logs are excluded from this
public repository.
