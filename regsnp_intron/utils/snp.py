#!/usr/bin/env python
import argparse
import os.path

import pandas as pd


class SNP(object):
    def __init__(self, in_fname):
        self.in_fname = os.path.expanduser(in_fname)

    def sort(self, out_fname):
        in_f = pd.read_csv(self.in_fname, sep='\s+', names=['#chrom', 'pos', 'ref', 'alt'])
        in_f.sort_values(by=['#chrom', 'pos']).to_csv(out_fname, sep='\t', header=False, index=False)


def main():
    parser = argparse.ArgumentParser(description='''
            Given input SNP file, prepare for feature calculator.''')
    parser.add_argument('ifname',
            help='input snp file, contains four columns: chrom, pos, ref, alt')
    parser.add_argument('ofname',
            help='output snp file')
    args = parser.parse_args()
    snp = SNP(args.ifname)
    snp.sort(args.ofname)

if __name__ == '__main__':
    main()
