import re
from copy import deepcopy
import pandas as pd


class CostTable:
    def __init__(self, table_path: str, tex_path: str):
        # Load table from csv file
        self.cost_table = pd.read_csv(table_path)
        # Missing value means this person does not pay towards that expense
        self.cost_table.fillna(0, inplace=True)

        # Read template LaTeX for pdf letters
        template_file = open(tex_path, 'r')
        self.template_tex = template_file.read()
        template_file.close()

        self.email_pattern = re.compile(r"\S+@\S+")

    def get_report_title(self):
        # We read the title from top left corner, since it's directly related to the expenses
        # Makes tracking a bit easier
        return self.cost_table.columns[0]

    def get_total_column(self):
        return self.cost_table.columns[1]

    def get_owners(self):
        return self.cost_table.columns[2:]

    def get_owner_name(self, owner):
        return self.email_pattern.split(owner)[0].strip()

    def get_owner_email(self, owner):
        email = self.email_pattern.findall(owner)
        return email

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
        latex_owner = latex_owner.replace(r"_NAME_", self.get_owner_name(owner))
        latex_owner = latex_owner.replace(r"_TABLE_", self.get_cost_summary(owner))
        latex_owner = latex_owner.replace(r"_AMOUNT_", self.get_owner_total(owner))
        latex_owner = latex_owner.replace(r"_TITLE_", self.get_report_title())
        return latex_owner