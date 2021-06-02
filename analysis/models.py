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
        print('Pending') #TODO


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
    
    def get_status(self):
        """
        Get all associated checks and work out the status
        """
        checks = Check.objects.filter(analysis = self)
        print(checks)
        #TODO


class Check(models.Model):
    """
    Model to store 1st, 2nd check etc

    """
    analysis = models.ForeignKey('SampleAnalysis', on_delete=models.CASCADE)
    stage = models.CharField(max_length=50) # 1st check IGV, 2nd, 3rd..., interpretation
    status = models.CharField(max_length=50)
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
