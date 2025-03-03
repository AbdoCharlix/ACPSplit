import argparse
import os
from pathlib import Path
import subprocess
from cost_table import CostTable
from send_email import EmailWrapper
import configparser
import tempfile
from shutil import copy


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

    parser.add_argument(
        '--config', '-c',
        type=str,
        required=True,
        help='Path for configuration file, with email parameters and strings to replace in templates'
    )

    args = parser.parse_args()

    # Get global variables for bills and email
    config = configparser.ConfigParser()
    config.read(args.config)

    # Read table and get owners+expenses names
    expense_report = CostTable(table_path=args.input, tex_path=args.tex)

    # Create output directory if it does not exist
    out_folder = args.out_dir
    Path(out_folder).mkdir(parents=True, exist_ok=True)

    # Prepare email out if a template exists
    email = args.mail is not None
    if email:
        email_wrapper = EmailWrapper(args.mail, config['Email'])

    # We want only the pdfs, so we put all the tex source and artifacts in a temp folder
    with tempfile.TemporaryDirectory() as tmpdirname:
        for o in expense_report.get_owners():
            letter_tex = expense_report.get_latex_owner(o)
            # Replace global variables with values from config file
            for key in config['Tex']:
                letter_tex = letter_tex.replace(key, config['Tex'][key])

            tex_filename = os.path.join(tmpdirname, o + '.tex')
            # Write final .tex file
            with open(tex_filename, 'w') as f:
                f.write(letter_tex)
            jobname = 'Decompte_' + expense_report.get_report_title() + '_' + expense_report.get_owner_name(o)
            # Don't want space in file name
            jobname = jobname.replace(' ', '_')
            subprocess.run(
                ['pdflatex', '-output-directory=' + tmpdirname,
                 '-jobname=' + jobname, tex_filename])

            # Copy pdf output to permanent output folder
            src_pdf_filename = os.path.join(tmpdirname,
                                    jobname + '.pdf')
            dst_pdf_filename = os.path.join(out_folder,
                                            jobname + '.pdf')
            copy(src_pdf_filename, dst_pdf_filename)

            if email and len(expense_report.get_owner_email(o)) > 0:
                filename = os.path.join(out_folder,
                                        jobname + '.pdf')
                email_wrapper.send_email(expense_report, o, filename)


if __name__ == '__main__':
    main()
