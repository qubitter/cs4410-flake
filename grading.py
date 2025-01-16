import orgparse
from functools import reduce
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

# grade | skip | quit | jump | help
section_opts = ["g", "s", "j", "q", "h"]
section_prompt = "/".join(section_opts)
section_help = [
        "[g]rade this section",
        "[s]kip this section and go to the next ungraded section",
        "[j]ump to a specific section",
        "[q]uit grading for now (save progress)",
        "[h]elp"
    ]

print(f"""
* * * * * * * * * * * * * {"* "*(2 + len(args.file)//2)}
* Grading based on rubric {args.file}{" " if len(args.file) % 2 == 0 else ""} *
* * * * * * * * * * * * * {"* "*(2 + len(args.file)//2)}
""")

root = orgparse.load(args.file)
submission_points = 0


def sum_im(x,y):
    def ct_im(z):
        return 1 if z == "i" else int(z[:-1])
    return ct_im(x)+ct_im(y)


def split_im(z):
    return (z.split("+")[0], z.split("+")[1])

(max_re, max_im) = reduce(
        (lambda x,y: (x[0]+y[0],sum_im(x[1],y[1]))), 
        map(lambda x: split_im(x[(str(x).rfind("[")+1):-1]), root.children),
        (0,0))

def grade_subpart(r):
    sections = r.children
    at_bottom = len(
            list(
                filter(
                    (lambda x: hasattr(x.children, "children")),
                    sections))) == 0
    ungraded_sections = []
    graded_sections = []
    current_section = 0

    while (len(graded_sections) != len(sections)):
        print(ungraded_sections[current_section])
        cmd = input(
            f"{len(ungraded_sections)} sections to grade. {section_prompt}:\n")
        match cmd:
            case "h":
                print("\n".join(section_help))
            case "q":
                quit()
            case "j":
                print("\n".join(ungraded_sections))
            case "s":
                current_section += 1
                current_section = current_section % len(ungraded_sections)
            case "g":
                if not at_bottom:
                    grade_subpart(ungraded_sections[current_section].children)
                else:
                    print(f"Now grading {sections[current_section]}")
                    for subsec in sections[current_section].children:
                        points = subsec[str(subsec).rfind("[")+1:-1]
                        if "," in points:
                            (grad_re, grad_im) = split_im(points.split(",")[1])
                        (ug_re, ug_im) = split_im(points.split(",")[0])
                        if input(f"{subsec}: Y/n: ").lower() == "y":
                            points += ug_re

