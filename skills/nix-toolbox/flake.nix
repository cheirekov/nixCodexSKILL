{
  description = "On-demand Nix tools for the nix-toolbox agent skill";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.git-hooks.url = "github:cachix/git-hooks.nix";
  inputs.git-hooks.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    {
      self,
      nixpkgs,
      treefmt-nix,
      git-hooks,
      ...
    }:
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
            treefmt
            nurl
            direnv
            pre-commit
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

      # Exercise the integrations on this toolbox, without installing Git hooks.
      checks = forSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          formatting = treefmt-nix.lib.evalModule pkgs {
            projectRootFile = "flake.nix";
            programs.nixfmt.enable = true;
          };
        in
        {
          formatting = formatting.config.build.check self;
          git-hooks = git-hooks.lib.${system}.run {
            src = self;
            hooks.deadnix.enable = true;
          };
        }
      );
    };
}
