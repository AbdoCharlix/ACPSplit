import pandas as pd
import argparse
import os
import subprocess
from copy import deepcopy
import re


class CostTable:
    def __init__(self, table_path: str, tex_path: str):
        self.cost_table = pd.read_csv(table_path)

        # Read template LaTeX for pdf letters
        template_file = open(tex_path, 'r')
        self.template_tex = template_file.read()
        template_file.close()

    def get_report_title(self):
        return self.cost_table.columns[0]

    def get_total_column(self):
        return self.cost_table.columns[1]

    def get_owners(self):
        return self.cost_table.columns[2:]

    def get_owner_name(self, owner):
        # TODO: will add some parsing to allow e-mail handling
        return owner

    def get_owner_total(self, o):
        return str(self.cost_table.sum(axis=0)[o])

    def get_cost_summary(self, owner):
        # Create expense table for that owner in tex - usable format
        table = ''
        # First line - column titles (expense, total cost, owner's share
        table += r"\begin{center}" + '\n'
        table += r"\begin{tabular}{ | l | c | r |}" + '\n'
        table += r"\hline" + '\n'
        table += r"\textbf{Expense} & \textbf{Total} & \textbf{Share}" + '\n'
        table += r"\\ \hline" + '\n'
        # Populate table for each expense
        for l in self.cost_table.index:
            table += self.cost_table[self.get_report_title()][l]
            table += ' & '
            table += str(self.cost_table[self.get_total_column()][l])
            table += ' & '
            table += str(self.cost_table[owner][l])
            table += r"\\ \hline" + '\n'
        # Add line with total sum
        table += r"\textbf{Total} & \textbf{" + str(self.cost_table.sum(axis=0)[self.get_total_column()]) + r"} & \textbf{" + self.get_owner_total(owner) + r"}" + '\n'
        table += r"\\ \hline" + '\n'
        table += r"\end{tabular}" + '\n'
        table += r"\end{center}" + '\n'
        return table

    def get_latex_owner(self, owner):
        latex_owner = deepcopy(self.template_tex)
        # Replace relevant strings in the template tex
        latex_owner = latex_owner.replace(r"%NAME%", self.get_owner_name(owner))
        latex_owner = latex_owner.replace(r"%TABLE%", self.get_cost_summary(owner))
        latex_owner = latex_owner.replace(r"%AMOUNT%", self.get_owner_total(owner))
        latex_owner = latex_owner.replace(r"%TITLE%", self.get_report_title())
        return latex_owner


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

    parser.add_argument('--email', '-e', action='store_true', default=False, help='Switch to send invoices via e-mail')

    args = parser.parse_args()

    # Read table and get owners+expenses names
    expense_report = CostTable(table_path=args.input, tex_path=args.template)

    out_folder = args.out_dir
    email = args.email
    email_pattern = r'\S+@\S+.\S+'
    for o in expense_report.get_owners():
        letter_tex = expense_report.get_latex_owner(o)
        tex_filename = os.path.join(out_folder, o + '.tex')
        # Write final .tex file
        with open(tex_filename, 'w') as f:
            f.write(letter_tex)
        subprocess.run(
            ['pdflatex', '-output-directory=' + out_folder, '-jobname=' + expense_report.get_report_title() + '_' + expense_report.get_owner_name(o), tex_filename])


if __name__ == '__main__':
    main()
