#!/usr/bin/env python3

import sys
from mergerlib import cat_reports


def main():
    if len(sys.argv) != 2 or sys.argv[1] != 'catreports':
              # args:    0       1
        print('Usage: python3 mergerapp.py catreports')
        sys.exit(1)

    cat_reports()
    sys.exit(0)

if __name__ == '__main__':
    main()
