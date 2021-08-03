
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.models import *

import os
import csv
import json
import pybedtools


class Command(BaseCommand):
    help = "Import a DNA run"

    def add_arguments(self, parser):
        parser.add_argument('--list', nargs=1, type=str, required=True, help='Run ID')


    @transaction.atomic
    def handle(self, *args, **options):
        """
        Run sample upload script
        """
        # extract variables from argparse
        poly_list = options['list'][0]

        # check that inputs are valid
        if not os.path.isfile(poly_list):
            raise IOError(f'{poly_list} file does not exist')


        # get poly list object
        list_obj = VariantList.objects.get(name='TSO500_polys')


        # make variants and variant checks
        with open(poly_list) as f:
            reader = csv.DictReader(f, delimiter=',')

            for v in reader:
                #print(v)
                # format pos, chr, ref etc as genomic coords
                genomic_coords = v['Variant']

                #print(genomic_coords)

                # variant object is created for all variants across whole panel
                new_var, created = Variant.objects.get_or_create(
                    genomic_37 = genomic_coords,
                    genomic_38 = None,
                )

                new_var_list_obj, created = VariantToVariantList.objects.get_or_create(
                    variant_list = list_obj,
                    variant = new_var,
                )

