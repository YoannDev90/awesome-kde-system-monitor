{
  description = "KDE Plasma System Monitor custom pages + generator";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in
      {
        packages.default = python.pkgs.buildPythonPackage {
          pname = "awesome-kde-system-monitor";
          version = "1.0.0";
          src = ./.;
          format = "pyproject";
          build-system = [ python.pkgs.hatchling ];
          propagatedBuildInputs = [
            python.pkgs.pygobject
            pkgs.glib
            pkgs.gobject-introspection
          ];
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            python.pkgs.pygobject
            python.pkgs.pytest
            python.pkgs.ruff
            python.pkgs.mypy
            pkgs.glib
            pkgs.gobject-introspection
            pkgs.pkg-config
          ];
        };
      });
}
