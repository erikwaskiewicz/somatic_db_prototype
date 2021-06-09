from django.db import models

# Create your models here.
class Run(models.Model):
    """
    A sequencing run

    """
    run_id = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.run_id

class Worksheet(models.Model):
    """
    An NGS worksheet, sometimes 1 run == 1 worksheet, sometimes there are multiple ws per run

    """
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
    """
    An individual sample

    """
    TYPE_CHOICES = (
        ('DNA', 'DNA'),
        ('RNA', 'RNA'),
    )
    sample_id = models.CharField(max_length=50, primary_key=True)
    sample_type = models.CharField(max_length=3, choices=TYPE_CHOICES)  # DNA or RNA


class Panel(models.Model):
    """
    A virtual panel
    TODO - add enough info to kick off a reanalysis from within the db
    e.g. path to BED, ?panel version number

    """
    panel_name = models.CharField(max_length=50, primary_key=True)


class SampleAnalysis(models.Model):
    """
    An analysis of a sample, if there are multiple analyses (e.g. multiple panels), 
    then there will be multiple sample analysis objects

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


class Variant(models.Model):
    """
    Variant info that always stays the same
    TODO - ?extract gene/ exon etc into own model

    """
    genomic_37 = models.CharField(max_length=200)
    genomic_38 = models.CharField(max_length=200)
    gene = models.CharField(max_length=50)
    exon = models.CharField(max_length=50)
    transcript = models.CharField(max_length=200)
    hgvs_c = models.CharField(max_length=200)
    hgvs_p = models.CharField(max_length=200)


class VariantAnalysis(models.Model):
    """
    Sample specific information about a variant

    """
    sample = models.ForeignKey('SampleAnalysis', on_delete=models.CASCADE)
    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    vaf = models.IntegerField()
    total_count = models.IntegerField()
    alt_count = models.IntegerField()
    manual_upload = models.BooleanField(default=False)


class VariantCheck(models.Model):
    """
    Record the genuine/ artefact check for a variant analysis

    """
    DECISION_CHOICES = (
        ('-', 'Pending'),
        ('G', 'Genuine'),
        ('A', 'Artefact'),
        ('P', 'Poly'),
        ('M', 'Miscalled'),
    )
    variant_analysis = models.ForeignKey('VariantAnalysis', on_delete=models.CASCADE)
    check_object = models.ForeignKey('Check', on_delete=models.CASCADE)
    decision = models.CharField(max_length=1, default='-')
    comment = models.CharField(max_length=500, blank=True, null=True) # TODO - link out to seperate comment model???


class VariantList(models.Model):
    """
    A list of known variants. e.g. a poly list or previously classified list

    """
    TYPE_CHOICES = (
        ('P', 'Poly'),
        ('K', 'Known'),
        ('A', 'Artefact'),
    )
    name = models.CharField(max_length=50, primary_key=True)
    list_type = models.CharField(max_length=1, choices=TYPE_CHOICES)


class VariantToVariantList(models.Model):
    """
    Link variants to variant lists
    
    """
    variant_list = models.ForeignKey('VariantList', on_delete=models.CASCADE)
    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    classification = models.CharField(max_length=50, blank=True, null=True)


class Gene(models.Model):
    """

    """
    gene = models.CharField(max_length=50, primary_key=True)


class CoverageRegions(models.Model):
    """

    """
    genomic = models.CharField(max_length=50, primary_key=True)
    gene = models.ForeignKey('Gene', on_delete=models.CASCADE)
    hgvs_c = models.CharField(max_length=50)


class GeneCoverageAnalysis(models.Model):
    """

    """
    sample = models.ForeignKey('SampleAnalysis', on_delete=models.CASCADE)
    gene = models.ForeignKey('Gene', on_delete=models.CASCADE)
    percent_270x = models.CharField(max_length=50)
    percent_135x = models.CharField(max_length=50)
    av_ntc_coverage = models.IntegerField()
    percent_ntc = models.CharField(max_length=50)
    percent_cosmic = models.CharField(max_length=50)


class CoverageRegionsAnalysis(models.Model):
    """

    """
    sample = models.ForeignKey('SampleAnalysis', on_delete=models.CASCADE)
    genomic = models.ForeignKey('CoverageRegions', on_delete=models.CASCADE)
    gene = models.ForeignKey('Gene', on_delete=models.CASCADE)
    average_coverage = models.IntegerField()
    percent_270x = models.CharField(max_length=50)
    percent_135x = models.CharField(max_length=50)
    ntc_coverage = models.IntegerField()
    percent_ntc = models.CharField(max_length=50)


class GapsAnalysis(models.Model):
    """

    """
    sample = models.ForeignKey('SampleAnalysis', on_delete=models.CASCADE)
    genomic = models.ForeignKey('CoverageRegions', on_delete=models.CASCADE)
    gene = models.ForeignKey('Gene', on_delete=models.CASCADE)
    average_coverage = models.IntegerField()
    percent_270x = models.CharField(max_length=50)
    percent_135x = models.CharField(max_length=50)
    average_coverage = models.IntegerField()
    percent_cosmic = models.CharField(max_length=50)


class Fusion(models.Model):
    """

    """
    fusion_genes = models.CharField(max_length=50, primary_key=True)
    left_breakpoint = models.CharField(max_length=50)
    right_breakpoint = models.CharField(max_length=50)


class FusionAnalysis(models.Model):
    """

    """
    sample = models.ForeignKey('SampleAnalysis', on_delete=models.CASCADE)
    fusion_genes = models.ForeignKey('Fusion', on_delete=models.CASCADE)
    split_reads = models.IntegerField()
    spanning_reads = models.IntegerField()
