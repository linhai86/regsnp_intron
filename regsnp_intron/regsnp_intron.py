#!/usr/bin/env python
import argparse
import json
import logging
import os.path

from feature_calculator import FeatureCalculator
from predictor.predictor import Predictor


def main():
    parser = argparse.ArgumentParser(description='''
            Given a list of intronic SNVs, predict the disease-causing probability
            based on genomic and protein structural features.''')
    parser.add_argument('sfname',
            help='JSON file containing settings.')
    parser.add_argument('ifname',
            help='input SNV file. Contains four columns: chrom, pos, ref, alt.')
    parser.add_argument('out_dir',
            help='directory contains output files')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)
    settings = json.load(open(args.sfname))
    feature_calculator = FeatureCalculator(settings, args.ifname, args.out_dir)
    feature_calculator.calculate_feature()

    db_dir = os.path.expanduser(settings['db_dir'])
    predictor = Predictor(os.path.join(db_dir, 'model', 'on_ss_imp.pkl'),
                          os.path.join(db_dir, 'model', 'off_ss_imp.pkl'),
                          os.path.join(db_dir, 'model', 'on_ss_clf.pkl'),
                          os.path.join(db_dir, 'model', 'off_ss_clf.pkl'))
    predictor.predict(os.path.join(args.out_dir, 'snp.features.txt'), os.path.join(args.out_dir, 'snp.prediction.txt'))

if __name__ == '__main__':
    main()
