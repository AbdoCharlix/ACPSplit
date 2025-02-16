# cost-split
Based on a CSV file containing common costs, generate PDF invoice files for each co-owner
As a small building manager, this is a tool that helps me so I dont have to copy/paste tables in documents and values in e-mail, which is error prone.

# Usage example
python3 ./scripts/cost_split.py -i inputs/cost_example.csv -t inputs/template.tex -o outputs --mail inputs/mail_template.txt -c inputs/config.ini

# CSV Format
In this example:
> March 2025,Total,Bob bob@email.be,Alice,Charles
> 
> Electricity, 50, 20, 14.5, 15.5
> 
> Water, 100, 50.5, 40, 9.5

March 2025 is the name of the report. The first column contains the name of the expenses, the second column contains the total for each expense.
Other columns contain each co-owner name with email address if available, and their share for each expense.

# Latex template
This template contains strings %NAME%, _TITLE_, _AMOUNT_ and _TABLE_ that will be replaced by the tool.
Other strings will be replaced based on fields in config.ini

# Email template
Similar to tex template, strings will be replaced based on csv table or values from config.ini
Note that email parameters (such as smtp server, sender id and email) need to be set in config.ini
User will be prompted for email account password.
