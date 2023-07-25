
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from django.contrib.auth.models import User
from analysis.models import *

import os
import csv
import textwrap
from argparse import RawTextHelpFormatter


class Command(BaseCommand):
    help = textwrap.dedent(
    """
    Import a poly list from file, file should be in the following format:
        Variant
        <genomic_coords_variant_1>
        <genomic_coords_variant_2>

    Variant must be genomic coords. Additional columns can be included but 
    will be ignored by script. See roi/b37_polys.txt and roi/b38_polys.txt 
    for examples.

    Using --both_checks flag is meant for dev work, it will add poly straight 
    into the poly list without checks, for live database dont use this flag
    """)


    def create_parser(self, *args, **kwargs):
        """ edit class so that help text above wraps round lines """
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser


    def add_arguments(self, parser):
        parser.add_argument('--list', nargs=1, type=str, required=True, help='Poly list file')
        parser.add_argument('--genome', nargs=1, type=str, required=True, help='Genome build as 37 or 38')
        parser.add_argument('--both_checks', default=False, action='store_true', help='Autocomplete both checks for each poly. IMPORTANT for use in dev work only')


    @transaction.atomic
    def handle(self, *args, **options):
        """
        Run poly upload script
        """
        # extract variables from argparse
        poly_list = options['list'][0]

        # check that inputs are valid
        if not os.path.isfile(poly_list):
            raise IOError(f'{poly_list} file does not exist')

        #  get poly list object
        genome = options['genome'][0]
        if genome == '37': 
            list_obj = VariantList.objects.get(name='build_37_polys')

        elif genome == '38':
            list_obj = VariantList.objects.get(name='build_38_polys')

        # error handling to make sure correct genome build is picked (otherwise it'll add a load of weird variants to the wrong list)
        validate_build = input(f'You have entered "{genome}" for the genome build, to confirm that this is correct please re-enter the build: \n')
        if genome != validate_build:
            exit(f'ERROR\t{timezone.now()}\t"{validate_build}" does not match the input genome build "{genome}", check inputs and try again')

        # get admin user to put aginst auto checks, must already exist
        user = User.objects.get(username='admin')

        # make variants and variant checks
        with open(poly_list) as f:
            reader = csv.DictReader(f, delimiter=',')

            for v in reader:
                # format pos, chr, ref etc as genomic coords
                genomic_coords = v['Variant']

                # variant object is created for all variants across whole panel
                new_var, created = Variant.objects.get_or_create(
                    variant = genomic_coords,
                    genome_build = genome,
                )

                # add variant to the poly list
                new_var_list_obj, created = VariantToVariantList.objects.get_or_create(
                    variant_list = list_obj,
                    variant = new_var,
                )

                # if the poly list instance is newly created, add user info
                if created:
                    new_var_list_obj.upload_user = user
                    new_var_list_obj.upload_time = timezone.now()
                    new_var_list_obj.upload_comment = 'Auto-uploaded by bioinformatics'
                    new_var_list_obj.save()
                    print(f'INFO\t{timezone.now()}\t{new_var_list_obj} added - {list_obj.name} - {genomic_coords}')
                else:
                    print(f'INFO\t{timezone.now()}\t{new_var_list_obj} already exists - {list_obj.name} - {genomic_coords}')

                # if both checks are to be auto signed off, add checker info
                if options['both_checks']:
                    new_var_list_obj.check_user = user
                    new_var_list_obj.check_time = timezone.now()
                    new_var_list_obj.check_comment = 'Auto-uploaded by bioinformatics'
                    new_var_list_obj.save()
