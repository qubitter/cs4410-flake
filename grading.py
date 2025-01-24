import orgparse
from argparse import ArgumentParser
import copy

parser = ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

# grade | list | skip | jump | quit | help
section_opts = ["g", "l", "s", "j", "q", "h"]
section_prompt = "/".join(section_opts)
section_help = [
    "[g]rade this section",
    "[l]ist subsections of this section",
    "[s]kip this section and go to the next ungraded section",
    "[j]ump to a specific section",
    "[q]uit grading for now (save progress)",
    "[h]elp",
]

print(f"""
* * * * * * * * * * * * * {"* " * (2 + len(args.file) // 2)}
* Grading based on rubric {args.file}{" " if len(args.file) % 2 == 0 else ""} *
* * * * * * * * * * * * * {"* " * (2 + len(args.file) // 2)}
""")

root = orgparse.load(args.file)
deductions = []
bonuses = []

grad = input("Grade this submission as graduate? ").lower().strip() == "y"


def print_output():
    print(f"Calculated deductions:\n{'\n'.join(deductions)}")
    print(f"Calculated bonuses:\n{'\n'.join(bonuses)}")


def get_points(p):
    p[p.rfind("[") + 1 : -1]


def get_clean_heading(h):
    if "[" in h.get_heading():
        return h.get_heading()[
            h.get_heading().find(".") + 1 : h.get_heading().rfind("[")
        ].strip()
    else:
        return h.get_heading()[h.get_heading().find(".") + 1 :].strip()

is_note = lambda h: h.get_heading().lower().strip().startswith("note:")

def grade_subpart(r, path):
    pad = copy.deepcopy(path)
    pad.append(get_clean_heading(r) if not r.is_root() else "")
    sections = r.children
    ungraded_sections = sections
    graded_sections = []
    current_section = 0

    while len(graded_sections) != len(sections):
        sect = sections[current_section % len(sections)]
        options = [i for i in sect.children if get_clean_heading(i).endswith("option")]
        if sect.children: print("/".join(pad) + "/" + get_clean_heading(sect))
        cmd = input(
            f"{len([i for i in sect.children if not is_note(i)])} {'subsections' if len(options) == 0 else 'options'} to grade. {section_prompt}: "
        ) if sect.children else "fallthrough"
        match cmd:
            case "h":
                print("\n".join(section_help))
            case "q":
                print_output()
                quit()
            case "j":
                print("\n".join(map((lambda x: x.get_heading()), ungraded_sections)))
            case "s":
                current_section += 1
                current_section = current_section % len(ungraded_sections)
            case "l":
                print("\n".join([get_clean_heading(i) for i in sect.children]))
            case "g" | "" | "fallthrough":
                if (
                    not len(
                        [
                            x.children
                            for x in sect.children
                            if x.children
                        ]
                    )
                    == 0
                ) and len(options) == 0:
                    grade_subpart(sect, pad)
                    graded_sections.append(sect)
                    current_section += 1
                    continue
                elif len(options) != 0:
                    print(
                        f"There are {len(options)} options:\n"
                        + "\n".join([x.get_heading() for x in options])
                    )
                    chosen_int = input(f"choose 1-{len(options)}: ")
                    choice = 0 if chosen_int == "" else int(chosen_int) - 1
                    sect = options[choice]

                if cmd != "fallthrough": print(f"Now grading {sect.get_heading()}")
                notes = [i for i in sect.children if is_note(i)]
                if notes: print("\n".join([get_clean_heading(i) for i in notes]))
                for subsec in ([i for i in sect.children if i not in notes] if sect.children else [sect]):
                    bonus = True in [i in subsec.get_heading().lower() for i in ["i]", "??", "bonus point"]]
                    inp = input(f"{subsec.get_heading()}: {"y/N" if bonus else "Y/n"} ").lower().strip()
                    if inp == "n" and not bonus:
                        deductions.append(
                            "/".join(pad + [get_clean_heading(sect)])
                            + ": "
                            + subsec.get_heading()
                        )
                    elif inp == "y" and bonus:
                        bonuses.append(
                            "/".join(pad + [get_clean_heading(sect)])
                            + ": "
                            + subsec.get_heading()
                        )
                graded_sections.append(sect)
                current_section += 1
    if path == []:
        print("* " * 32)
        print("Grading complete!")
        print_output()

grade_subpart(root, [])
