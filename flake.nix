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
        p3pkgs = pkgs.python312Packages;
        ocaml-pkgs = with pkgs.ocamlPackages; [
          findlib
          extlib
          ounit2
          utop
          odoc
          ocaml-lsp
          ocamlformat
          ocamlbuild
        ];
        build-pkgs =  with pkgs; [
          ocaml
          dune_3
          nasm
          clang
          valgrind
        ]; 
        grading-pkgs = with pkgs; [
          unzip # to unzip student submissions :p
          pyright # to develop my grading script
          p3pkgs.orgparse # ditto
        ];
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = build-pkgs ++ ocaml-pkgs;
        };
        devShells.grading = pkgs.mkShell {
          buildInputs = build-pkgs ++ ocaml-pkgs ++ grading-pkgs;
        };
        packages = {
          default = pkgs.writers.writePython3Bin "grading"
            { libraries = [ p3pkgs.orgparse ]; }
            (builtins.readFile ./grading.py);
        };
      });
  
}
