#!/usr/bin/env python
import argparse
import logging
import os.path

import pysam

class VCF(object):
    def __init__(self, in_fname):
        self.in_fname = os.path.expanduser(in_fname)
        self.logger = logging.getLogger(__name__)

    def convert_to_txt(self, out_fname, filter=True):
        """
        convert vcf to 4-column txt input file for regsnp_intron.
        :param out_fname: output txt file name
        :param filter: whether filter out variants that failed the filter
        """
        with pysam.VariantFile(self.in_fname, 'r') as vcf, open(os.path.expanduser(out_fname), 'w') as out_f:
            for record  in vcf.fetch():
                if not filter or not list(record.filter) or list(record.filter) == ['PASS']:
                    for alt in record.alts:
                        if len(record.ref) == 1 and len(alt) == 1:
                            out_f.write('\t'.join(map(str, [record.chrom, record.pos, record.ref, alt])) + '\n')

def main():
    parser = argparse.ArgumentParser(description='''
            Convert a vcf file to a 4-column txt file: chrom, pos, ref, alt.''')
    parser.add_argument('ifname',
            help='input vcf file')
    parser.add_argument('ofname',
            help='output txt file')
    args = parser.parse_args()
    vcf = VCF(args.ifname)
    vcf.convert_to_txt(args.ofname)

if __name__ == '__main__':
    main()