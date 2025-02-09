# cost-split
Based on a CSV file containing common costs, generate PDF invoice files for each co-owner

# CSV Format
In this example:
> March 2025,Total,Bob,Alice,Charles
> 
> Electricity, 50, 20, 14.5, 15.5
> 
> Water, 100, 50.5, 40, 9.5

March 2025 is the name of the report. The first column contains the name of the expenses, the second column contains the total for each expense.
Other columns contain each co-owner name and their share for each expense

# Latex template
This template contains strings %NAME%, %TITLE%, %AMOUNT% and %TABLE% that will be replaced by the tool.
