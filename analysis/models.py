from django.db import models

# Create your models here.
class Run(models.Model):
    run_id = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.run_id

class Worksheet(models.Model):
    ws_id = models.CharField(max_length=50, primary_key=True)
    run = models.ForeignKey('Run', on_delete=models.CASCADE)
    assay = models.CharField(max_length=50)

    def __str__(self):
        return self.ws_id

    def get_status(self):
        samples = SampleAnalysis.objects.filter(worksheet = self)
        l = [ s.get_checks()['current_status'] for s in samples ]
        return ' | '.join( set(l) )


class Sample(models.Model):
    sample_id = models.CharField(max_length=50, primary_key=True)
    sample_type = models.CharField(max_length=50)  # DNA or RNA


class Panel(models.Model):
    """
    """
    panel_name = models.CharField(max_length=50, primary_key=True)


class SampleAnalysis(models.Model):
    """

    """
    worksheet = models.ForeignKey('Worksheet', on_delete=models.CASCADE)
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    panel = models.ForeignKey('Panel', on_delete=models.CASCADE)

    def get_checks(self):
        """
        Get all associated checks and work out the status
        TODO - make this a bit better
        """
        all_checks = Check.objects.filter(analysis = self).order_by('pk')
        igv_checks = all_checks.filter(stage='IGV')
        vus_checks = all_checks.filter(stage='VUS')

        current_status = 'Complete'
        assigned_to = 'N/A'
        current_check_object = None

        for n, c in enumerate(vus_checks):
            if c.status == 'P':
                current_status = f'{c.get_stage_display()}'
                assigned_to = c.user
                current_check_object = c

        for n, c in enumerate(igv_checks):
            if c.status == 'P':
                current_status = f'{c.get_stage_display()} {n+1}'
                assigned_to = c.user
                current_check_object = c

        return {
            'current_status': current_status,
            'assigned_to': assigned_to,
            'current_check_object': current_check_object,
            'all_checks': all_checks,
        }


class Check(models.Model):
    """
    Model to store 1st, 2nd check etc

    """
    STAGE_CHOICES = (
        ('IGV', 'IGV check'),
        ('VUS', 'Interpretation check'),
    )
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('C', 'Complete'),
        ('F', 'Fail'),
    )
    analysis = models.ForeignKey('SampleAnalysis', on_delete=models.CASCADE)
    stage = models.CharField(max_length=3, choices=STAGE_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT, blank=True, null=True)
    signoff_time = models.DateTimeField(blank=True, null=True)
