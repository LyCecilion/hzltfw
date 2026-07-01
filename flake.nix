{
  description = "Development environment for Hazelita Forensics Workbench";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.python312
              pkgs.uv
              pkgs.ruff
              pkgs.zsh
            ];

            env = {
              UV_PYTHON = "${pkgs.python312}/bin/python";
              SHELL = "${pkgs.zsh}/bin/zsh";
            };

            shellHook = ''
              if [ -z "$HZLTFW_NIX_ZSH" ]; then
                export HZLTFW_NIX_ZSH=1
                exec ${pkgs.zsh}/bin/zsh
              fi
            '';
          };
        }
      );
    };
}
