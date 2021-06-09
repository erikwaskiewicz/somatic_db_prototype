from .models import *
from django.utils import timezone


def signoff_check(user, current_step_obj, status='C'):
    """
    """
    now = timezone.now()

    # signoff current check
    current_step_obj.user = user
    current_step_obj.signoff_time = now
    current_step_obj.status = status
    
    # save objects
    current_step_obj.save()


def make_next_check(sample_obj, next_step):
    """
    """
    # add new check object
    new_check_obj = Check(
        analysis=sample_obj, 
        stage=next_step,
        status='P',
    )

    # save objects
    new_check_obj.save()
