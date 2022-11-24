
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.models import *


class Command(BaseCommand):
    help = "Add a single variant to the poly list"

    def add_arguments(self, parser):
        parser.add_argument('--genomic_coords', nargs=1, type=str, required=True, help='')


    @transaction.atomic
    def handle(self, *args, **options):
        """
        Run sample upload script
        """

        list_obj = VariantList.objects.get(name='TSO500_polys')

        # format pos, chr, ref etc as genomic coords
        genomic_coords = options['genomic_coords'][0]
        print(genomic_coords)

        # get or create the variant object
        new_var, created = Variant.objects.get_or_create(
            genomic_37 = genomic_coords,
            genomic_38 = None,
        )

        if created:
            print(f'New variant object created for {genomic_coords}.')
        else:
            print(f'Variant object for {genomic_coords} already exists, using existing object.')

        # create new variant list object
        new_var_list_obj, created = VariantToVariantList.objects.get_or_create(
            variant_list = list_obj,
            variant = new_var,
        )

        if created:
            print(f'{genomic_coords} added to the poly list.')
        else:
            print(f'{genomic_coords} is already in the poly list.')

