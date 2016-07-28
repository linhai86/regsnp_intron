#!/usr/bin/env python
import argparse
import os.path

from pybedtools import BedTool


class ClosestExon(object):
    def __init__(self, efname):
        self.efname = os.path.expanduser(efname)

    def get_closest_exon(self, in_fname, out_fname):
        in_f = BedTool(in_fname)
        in_f.sort().closest(self.efname, D='b', t='first').moveto(out_fname)


def main():
    parser = argparse.ArgumentParser(description='''
            Given BED file and exon annotation, find the closest exon.''')
    parser.add_argument('efname',
            help='exon bed file')
    parser.add_argument('ifname',
            help='input bed file')
    parser.add_argument('ofname',
            help='output bed file')
    args = parser.parse_args()
    closest_exon = ClosestExon(args.efname)
    closest_exon.get_closest_exon(args.ifname, args.ofname)

if __name__ == '__main__':
    main()
