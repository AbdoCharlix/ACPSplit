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
    #for o in owners:


if __name__ == '__main__':
    main()
