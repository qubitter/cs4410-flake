{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils"; 
  };


  outputs = {
    self,
    nixpkgs,
    ...
  } @ inputs : 
    inputs.flake-utils.lib.eachDefaultSystem (system:
      let
        name = "cs4410-flake";
	src = ./.;
      	pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            ocaml
            dune_3
            nasm
            clang
            valgrind
          ] ++ (with pkgs.ocamlPackages; [
            findlib
            extlib
            ounit2
            utop
            odoc
            ocaml-lsp
            ocamlformat
            ocamlbuild
          ]);
        };
      });
  
}
