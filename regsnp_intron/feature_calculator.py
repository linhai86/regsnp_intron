#!/usr/bin/env python
import argparse
import json
import logging
import os
import os.path

import pandas as pd

from utils.seq import FlankingSeq
from utils.snp import SNP
from utils.annovar import Annovar
from utils.closest_exon import ClosestExon
from rbp.rbp_change import RBPChange
from protein_feature.protein_feature import ProteinFeature
from junc_score.junction_strength import JunctionStrength
from conservation.phylop import Phylop


class FeatureCalculator(object):
    def __init__(self, settings, ifname, out_dir):
        self.settings = settings
        self.db_dir = os.path.expanduser(settings['db_dir'])
        self.ifname = os.path.expanduser(ifname)
        self.out_dir = os.path.expanduser(out_dir)
        self.logger = logging.getLogger(__name__)
    
    def calculate_feature(self):
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
        out_dir_tmp = os.path.join(self.out_dir, 'tmp')
        if not os.path.exists(out_dir_tmp):
            os.mkdir(out_dir_tmp)

        if not os.path.exists(os.path.join(out_dir_tmp, 'snp.sorted')):
            self.logger.info('Sorting input file.')
            snp = SNP(self.ifname)
            snp.sort(os.path.join(out_dir_tmp, 'snp.sorted'))

        if not os.path.exists(os.path.join(out_dir_tmp, 'snp.distance')):
            self.logger.info('Annotating SNVs with ANNOVAR.')
            annovar_path = os.path.expanduser(self.settings['annovar_path'])
            annovar_db_path = os.path.expanduser(self.settings['annovar_db_path'])
            annovar = Annovar(annovar_path, annovar_db_path)
            annovar.annotate(os.path.join(out_dir_tmp, 'snp.sorted'), os.path.join(out_dir_tmp, 'snp'))

            self.logger.info('Calculating distance to closest protein coding exons.')
            protein_coding_exon_fname = os.path.join(self.db_dir, 'hg19_ensGene_exon.bed')
            closest_exon = ClosestExon(protein_coding_exon_fname)
            closest_exon.get_closest_exon(os.path.join(out_dir_tmp, 'snp.intronic'),
                                          os.path.join(out_dir_tmp, 'snp.distance'))

        if not os.path.exists(os.path.join(out_dir_tmp, 'snp.seq')):
            self.logger.info('Fetching flanking sequence.')
            ref_name = os.path.join(self.db_dir, 'hg19/hg19.fa')
            seq = FlankingSeq(ref_name, 20)
            seq.fetch_flanking_seq(os.path.join(out_dir_tmp, 'snp.distance'), os.path.join(out_dir_tmp, 'snp.seq'))
            seq.fetch_flanking_seq(os.path.join(out_dir_tmp, 'snp.distance'), os.path.join(out_dir_tmp, 'snp.fa'),
                                   otype='fasta')
            seq.close()

        if not os.path.exists(os.path.join(out_dir_tmp, 'snp.rbp_change')):
            self.logger.info('Calculating RBP binding change.')
            pssm_path = os.path.join(self.db_dir, 'motif/pwm')
            pssm_list_fname = os.path.join(self.db_dir, 'motif/pwm_valid.txt')
            ms_fname = os.path.join(self.db_dir, 'motif/binding_score_mean_sd.txt')
            rbp = RBPChange(pssm_path, pssm_list_fname, ms_fname)
            rbp.rbps.cal_matching_score(os.path.join(out_dir_tmp, 'snp.seq'),
                                        os.path.join(out_dir_tmp, 'snp.rbp_score'))
            rbp.cal_change(os.path.join(out_dir_tmp, 'snp.rbp_score'), os.path.join(out_dir_tmp, 'snp.rbp_change'))

        if not os.path.exists(os.path.join(out_dir_tmp, 'snp.protein_feature')):
            self.logger.info('Extracting protein structural features.')
            db_fname = os.path.join(self.db_dir, 'ensembl.db')
            gene_pred_fname = os.path.join(self.db_dir, 'hg19_ensGene.txt')
            protein_feature = ProteinFeature(db_fname, gene_pred_fname)
            protein_feature.calculate_protein_feature(os.path.join(out_dir_tmp, 'snp.distance'),
                                                      os.path.join(out_dir_tmp, 'snp.protein_feature'))

        if not os.path.exists(os.path.join(out_dir_tmp, 'snp.junc')):
            self.logger.info('Calculating junction strength change.')
            donor_ic_fname = os.path.join(self.db_dir, 'motif/donorsite.pssm')
            acceptor_ic_fname = os.path.join(self.db_dir, 'motif/acceptorsite.pssm')
            junction_strength = JunctionStrength(donor_ic_fname, acceptor_ic_fname)
            junction_strength.cal_junction_strength(ref_name, os.path.join(out_dir_tmp, 'snp.distance'),
                                                    os.path.join(out_dir_tmp, 'snp.junc'))

        if not os.path.exists(os.path.join(out_dir_tmp, 'snp.phylop')):
            self.logger.info('Calculating conservation score.')
            phylop_fname = os.path.join(self.db_dir, 'phylop/hg19.100way.phyloP100way.bw')
            phylop = Phylop(phylop_fname)
            phylop.calculate(os.path.join(out_dir_tmp, 'snp.distance'), os.path.join(out_dir_tmp, 'snp.phylop'))
            phylop.close()

        self._merge_features()

    def _merge_features(self):
        self.logger.info('Merging all the features.')
        out_dir_tmp = os.path.join(self.out_dir, 'tmp')
        rbp_change = pd.read_csv(os.path.join(out_dir_tmp, 'snp.rbp_change'), sep='\t', header=0)
        snps = rbp_change.loc[:, ['#chrom', 'pos', 'ref', 'alt']]
        rbp_change.drop(['#chrom', 'pos', 'ref', 'alt', 'ref_seq', 'alt_seq'], axis=1, inplace=True)

        column_to_drop = ['#chrom_snp', 'start_snp', 'end_snp', 'ref', 'alt', 'feature',
                          'gene_id', 'chrom', 'start', 'end', 'score']
        protein_feature = pd.read_csv(os.path.join(out_dir_tmp, 'snp.protein_feature'), sep='\t', header=0)
        protein_feature.drop(column_to_drop, axis=1, inplace=True)

        junction_strength = pd.read_csv(os.path.join(out_dir_tmp, 'snp.junc'), sep='\t', header=0,
                                        usecols=['aic', 'dic', 'aic_change', 'dic_change'])

        phylop = pd.read_csv(os.path.join(out_dir_tmp, 'snp.phylop'), sep='\t', header=0,
                             usecols=['phylop1', 'phylop3', 'phylop7'])

        result = pd.concat([snps, rbp_change, protein_feature, junction_strength, phylop], axis=1)
        result.to_csv(os.path.join(self.out_dir, 'snp.features.txt'), sep='\t', index=False, na_rep='NA')


def main():
    parser = argparse.ArgumentParser(description='''
            Given input SNP file, calculate features for classifier.''')
    parser.add_argument('sfname',
            help='JSON file containing settings.')
    parser.add_argument('ifname',
            help='input SNP file. Contains four columns: chrom, pos, ref, alt.')
    parser.add_argument('out_dir',
            help='directory contains output files')
    args = parser.parse_args()

    settings = json.load(open(args.sfname))
    feature_calculator = FeatureCalculator(settings, args.ifname, args.out_dir)
    feature_calculator.calculate_feature()

if __name__ == '__main__':
    main()