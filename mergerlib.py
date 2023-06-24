import os
import re
import pdfplumber
from PyPDF2 import PdfFileMerger


def cat_reports():
    # Create dictionary of pdf file metadata prior to merging
    dir_path = os.path.dirname(os.path.realpath(__file__)) # path to script
    rep_path = os.path.join(dir_path, 'conc_reports')      # path to reports
    pattern = re.compile('^(CTR_\d+_\d+_\d+_\d+_C)(\d+).pdf$') # CTR_XXX_XX_XXX_XXX_CX.pdf
    reports = {} # {'wo': {'first': int, 'last': int}}
    for filename in os.listdir(rep_path):
        if filename.endswith('.pdf'):
            m = re.match(pattern, filename)
            if m is not None:
                wo = m.group(1)
                set_no = int(m.group(2))
                if wo not in reports.keys():
                    reports[wo] = {'first': set_no, 'last': set_no}
                else:
                    if reports[wo]['first'] > set_no:
                        reports[wo]['first'] = set_no
                    elif reports[wo]['last'] < set_no:
                        reports[wo]['last'] = set_no

    # Merge pdfs by work order in ascending set order
    for wo in reports.keys():

        # Extract pdf info for output file filename
        rev_no, days, loc = '1', '0', 'pour_location' # default values
        first, last = reports[wo]['first'], reports[wo]['last']
        rev_p = re.compile('Issue No:  (\d+)')
        day_p = re.compile('\d+-\d+-\d+-\d+-C\d+[A-Z] \d+/\d+/\d+ (\d+) \d+\.\d')
        loc_p = re.compile('Sample Location: (.+)     Measured Specified')
        with pdfplumber.open(os.path.join(rep_path, f'{wo}{first}.pdf')) as pdf:
            for line in pdf.pages[0].extract_text().splitlines():
                rev_m = re.match(rev_p, line)
                day_m = re.match(day_p, line)
                loc_m = re.match(loc_p, line)
                if rev_m is not None:
                    rev_no = rev_m.group(1)
                if day_m is not None:
                    if int(day_m.group(1)) > int(days):
                        days = day_m.group(1)
                if loc_m is not None:
                    loc = loc_m.group(1).replace('/', ',') # replace problem characters

        # Merge pdfs
        merger = PdfFileMerger()
        for set_no in range(first, last + 1):
            merger.append(os.path.join(rep_path, f'{wo}{set_no}.pdf'))
        if first == last:
            merger.write(os.path.join(rep_path, f'{wo}{first}_[{rev_no}] - Concrete Test ' + \
                                                f'Report - {days}d - {loc}.pdf'))
        else:
            merger.write(os.path.join(rep_path, f'{wo}{first}_[{rev_no}] to C{last}_[{rev_no}]' + \
                                                f' - Concrete Test Report - {days}d - {loc}.pdf'))
        merger.close()

    return 0
