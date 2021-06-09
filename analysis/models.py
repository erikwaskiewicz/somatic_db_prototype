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
        current_check_object = all_checks.latest('pk')

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

        for c in all_checks:
            if c.status == 'F':
                current_status = 'Fail'
                assigned_to = 'N/A'
                current_check_object = all_checks.latest('pk')

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



class variant_call(models.Model):
    genomic=models.CharField(max_length=50, primary_key=True)
    gene=models.CharField(max_length=50)
    exon=models.CharField(max_length=50)
    transcript=models.CharField(max_length=50)
    hgvs_c=models.CharField(max_length=50)
    hgvs_p=models.CharField(max_length=50)

class variant_analysis(models.Model):
    sampleId=models.ForeignKey(Sample, on_delete=models.CASCADE)
    run = models.ForeignKey('Run', on_delete=models.CASCADE)
    panel = models.ForeignKey('panel', on_delete=models.CASCADE)
    variant=models.ForeignKey(variant_call, on_delete=models.CASCADE)
    vaf=models.CharField(max_length=50)
    total_count=models.IntegerField()
    alt_count=models.IntegerField()
    manual_upload=models.BooleanField(default=False)


class polys(models.Model):

    genomic=models.CharField(max_length=50, primary_key=True)
    gene=models.CharField(max_length=50)
    exon=models.CharField(max_length=50)
    transcript=models.CharField(max_length=50)
    hgvs_c=models.CharField(max_length=50)
    hgvs_p=models.CharField(max_length=50)
    vaf=models.CharField(max_length=50)
    total_count=models.IntegerField()
    alt_count=models.IntegerField()


class gene(models.Model):

    gene=models.CharField(max_length=50, primary_key=True)


class coverage_regions(models.Model):

    genomic=models.CharField(max_length=50, primary_key=True)
    gene=models.ForeignKey(gene, on_delete=models.CASCADE)
    hgvs_c=models.CharField(max_length=50)



class gene_coverage_analysis(models.Model):
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    gene = models.ForeignKey('gene', on_delete=models.CASCADE)
    percent_270x=models.CharField(max_length=50)
    percent_135x=models.CharField(max_length=50)
    panel=models.ForeignKey(Panel, on_delete=models.CASCADE)
    av_ntc_coverage=models.IntegerField()
    percent_ntc=models.CharField(max_length=50)
    percent_cosmic=models.CharField(max_length=50)


class coverage_regions_analysis(models.Model):
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    genomic = models.ForeignKey('coverage_regions', on_delete=models.CASCADE)
    panel=models.ForeignKey(Panel, on_delete=models.CASCADE)
    gene=models.ForeignKey(gene, on_delete=models.CASCADE)
    average_coverage=models.IntegerField()
    percent_270x=models.CharField(max_length=50)
    percent_135x=models.CharField(max_length=50)
    ntc_coverage=models.IntegerField()
    percent_ntc=models.CharField(max_length=50)


class gaps_analysis(models.Model):
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    genomic = models.ForeignKey('coverage_regions', on_delete=models.CASCADE)
    panel=models.ForeignKey(Panel, on_delete=models.CASCADE)
    gene=models.ForeignKey(gene, on_delete=models.CASCADE)
    average_coverage=models.IntegerField()
    percent_270x=models.CharField(max_length=50)
    percent_135x=models.CharField(max_length=50)
    average_coverage=models.IntegerField()
    percent_cosmic=models.CharField(max_length=50)



class fusion(models.Model):
    fusion_genes=models.CharField(max_length=50, primary_key=True)
    left_breakpoint=models.CharField(max_length=50)
    right_breakpoint=models.CharField(max_length=50)


class fusion_analysis(models.Model):
    sampleId=models.ForeignKey(Sample, on_delete=models.CASCADE)
    run = models.ForeignKey('Run', on_delete=models.CASCADE)
    panel=models.ForeignKey(Panel, on_delete=models.CASCADE)
    fusion_genes=models.ForeignKey(fusion, on_delete=models.CASCADE)
    split_reads=models.IntegerField()
    spanning_reads=models.IntegerField()



