from .models import *
from django.utils import timezone

# TODO make sure that nothing gets saved to db if there's an error -- ? transaction.atomic
def signoff_check(user, current_step_obj, status='C'):
    """

    """
    # make sure each variant has a class
    variant_checks = VariantCheck.objects.filter(check_object=current_step_obj)
    for v in variant_checks:
        if v.decision == '-':
            # this trigers view to render the error on the page
            return False

    # signoff current check
    now = timezone.now()
    current_step_obj.user = user
    current_step_obj.signoff_time = now
    current_step_obj.status = status
    
    # save object
    current_step_obj.save()

    return True


def make_next_check(sample_obj, next_step):
    """

    """
    # add new check object
    new_check_obj = Check(
        analysis=sample_obj, 
        stage=next_step,
        status='P',
    )

    # save object
    new_check_obj.save()

    # make check objects for all variants
    variant_objects = VariantAnalysis.objects.filter(sample=sample_obj)
    for v in variant_objects:
        new_variant_check = VariantCheck(
            variant_analysis = v,
            check_object = new_check_obj,
        )
        new_variant_check.save()

    return True
