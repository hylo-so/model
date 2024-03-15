{
  description = "Python + micromamba environment";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/30ff48f4f1b6dc5033001e86d6524018ceeae709";
  };
  outputs = { self, nixpkgs }:
  with import nixpkgs { system = "aarch64-darwin"; };
  {
    devShells.aarch64-darwin.default = mkShell {
      packages = [ micromamba pyright ];
    };
  };
}
