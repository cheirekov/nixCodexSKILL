{
  description = "On-demand Nix tools for the nix-toolbox agent skill";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forSystems = nixpkgs.lib.genAttrs systems;
      toolsFor =
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          inherit (pkgs)
            statix
            deadnix
            nixfmt
            nix-diff
            nix-init
            nix-update
            nix-fast-build
            mcp-nixos
            ;
          nom = pkgs.nix-output-monitor;
          nix-locate = pkgs.nix-index;
        };
    in
    {
      # Temporary ordinary tools, e.g. nix shell .#jq -c jq --version.
      legacyPackages = forSystems (system: import nixpkgs { inherit system; });

      apps = forSystems (
        system:
        let
          tools = toolsFor system;
        in
        builtins.mapAttrs (name: package: {
          type = "app";
          inherit (package) meta;
          program = if name == "nix-locate" then "${package}/bin/nix-locate" else nixpkgs.lib.getExe package;
        }) tools
      );

      # No default shell: an agent fetches only the helper it needs.
      formatter = forSystems (system: (toolsFor system).nixfmt);
    };
}
