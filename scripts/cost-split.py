import pandas as pd
import argparse


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
        '--out_dir', '-o',
        type=str,
        help='Path for generated pdfs.'
    )

    args = parser.parse_args()
    cost_table = pd.read_csv(args.input)
    report_name = cost_table.columns[0]
    total_column = cost_table.columns[1]
    owners = cost_table.columns[2:]
    print(owners)
    print(cost_table.values)
    for o in owners:
        with open(o + '.tex', 'w') as f:
            f.write(r"\begin{center}" + '\n')
            f.write(r"\begin{tabular}{ | l | c | r |}" + '\n')
            f.write(r"\hline" + '\n')
            for l in cost_table.index:
                line = cost_table[report_name][l]
                line += ' & '
                line += str(cost_table[total_column][l])
                line += ' & '
                line += str(cost_table[o][l])
                f.write(line + r"\\ \hline" + '\n')
            f.write(r"\end{tabular}" + '\n')
            f.write(r"\end{center}" + '\n')

            to_pay = cost_table.sum(axis=0)
            summary_line = 'Merci de regler la somme de ' + str(to_pay[o]) + r'e avec la communication \textbf{' + report_name + o + "}.\n"
            f.write(summary_line)


if __name__ == '__main__':
    main()
