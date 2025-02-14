import argparse
import os
import subprocess
from cost_table import CostTable
from send_email import EmailWrapper


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
        '--tex', '-t',
        type=str,
        required=True,
        help='Path to tex template'
    )

    parser.add_argument(
        '--mail', '-m',
        type=str,
        required=False,
        help='Path to txt email template'
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
    expense_report = CostTable(table_path=args.input, tex_path=args.tex)

    out_folder = args.out_dir
    email = args.email and args.mail is not None
    if email:
        email_wrapper = EmailWrapper(args.mail)

    for o in expense_report.get_owners():
        expense_report.get_owner_email(o)
        letter_tex = expense_report.get_latex_owner(o)
        tex_filename = os.path.join(out_folder, o + '.tex')
        # Write final .tex file
        with open(tex_filename, 'w') as f:
            f.write(letter_tex)
        subprocess.run(
            ['pdflatex', '-output-directory=' + out_folder,
             '-jobname=' + expense_report.get_report_title() + '_' + expense_report.get_owner_name(o), tex_filename])
        if email and len(expense_report.get_owner_email(o)) > 0:
            filename = os.path.join(out_folder,
                                    expense_report.get_report_title() + '_' + expense_report.get_owner_name(o) + '.pdf')
            email_wrapper.send_email(expense_report, o, filename)


if __name__ == '__main__':
    main()
