import pandas as pd
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description='Generates pdfs for invoicing common costs'
    )

    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Path to common cost table - csv file'
    )

    parser.add_argument(
        '--template', '-t',
        type=str,
        required=True,
        help='Path to tex template'
    )

    parser.add_argument(
        '--out_dir', '-o',
        type=str,
        help='Path for generated pdfs.',
        default='outputs'
    )

    args = parser.parse_args()

    # Read table and get owners+expenses names
    cost_table = pd.read_csv(args.input)
    report_name = cost_table.columns[0]
    total_column = cost_table.columns[1]
    owners = cost_table.columns[2:]

    # Read template LaTeX for pdf letters
    template_file = open(args.template, 'r')
    template_tex = template_file.read()
    template_file.close()

    out_folder = args.out_dir

    for o in owners:
        tex_filename = os.path.join(out_folder, o + '.tex')
        # Create expense table for that owner in tex - usable format
        table = ''
        table += r"\begin{center}" + '\n'
        table += r"\begin{tabular}{ | l | c | r |}" + '\n'
        table += r"\hline" + '\n'
        table += r"\textbf{Expense} & \textbf{Total} & \textbf{Share}" + '\n'
        table += r"\\ \hline" + '\n'
        # Populate table for each expense
        for l in cost_table.index:
            table += cost_table[report_name][l]
            table += ' & '
            table += str(cost_table[total_column][l])
            table += ' & '
            table += str(cost_table[o][l])
            table += r"\\ \hline" + '\n'
        table += r"\end{tabular}" + '\n'
        table += r"\end{center}" + '\n'

        # Compute total amount for that owner
        to_pay = cost_table.sum(axis=0)[o]

        # Replace relevant strings in the template tex
        letter_tex = template_tex.replace(r"%NAME%", o)
        letter_tex = letter_tex.replace(r"%TABLE%", table)
        letter_tex = letter_tex.replace(r"%AMOUNT%", str(to_pay))
        letter_tex = letter_tex.replace(r"%TITLE%", report_name)

        # Write final .tex file
        with open(tex_filename, 'w') as f:
            f.write(letter_tex)


if __name__ == '__main__':
    main()
