import random
import string

from django.db import models
from auditlog.registry import auditlog

#####################
### Common Models ###
#####################

class Gene(models.Model):
    """
    Gene
    """
    gene = models.CharField(max_length=20, primary_key=True)

    def __repr__(self):
        return f"Gene: {self.gene}"
    
class Transcript(models.Model):
    """
    NCBI transcript identifiers
    """
    transcript = models.CharField(max_length=50, primary_key=True)
    gene = models.ForeignKey("Gene", on_delete=models.PROTECT)

    def __repr__(self):
        return f"Transcript {self.transcript} in gene {self.gene}"

######################
### Analysis Setup ###
######################

class Patient(models.Model):
    """
    An individual patient. Primary key is the NHS number.
    If NHS number is not available, a random string of 10 letters is generated
    """
    nhs_number = models.CharField(max_length=10)

    @staticmethod
    def generate_standin_nhs_number():
        lowercase_letters = string.ascii_lowercase
        lowercase_list = [random.choice(lowercase_letters) for i in range(10)]
        standin_nhs_number = "".join(lowercase_list)
        return standin_nhs_number

class Sample(models.Model):
    """
    An individual sample
    """
    sample_id = models.CharField(max_length=20, primary_key=True)

    def __repr__(self):
        return f"Sample {self.sample_id}"
    
class Indication(models.Model):
    """
    Indication the patient is being tested for e.g. ALL
    """
    indication = models.CharField(max_length=20, primary_key=True)
    indication_pretty_print = models.CharField(max_length=100)
    panel_phase_zero = models.ForeignKey('Panel', on_delete=models.SET_NULL, null=True, related_name='panel_phase_zero')
    panel_phase_one = models.ForeignKey('Panel', on_delete=models.PROTECT, related_name='panel_phase_one')

    def __repr__(self):
        return f"Indication: {self.indication_pretty_print}"
    
class Panel(models.Model):
    """
    A virtual panel of genes
    """
    id = models.AutoField(primary_key=True)
    panel_name = models.CharField(max_length=50)
    panel_version = models.IntegerField()
    panel_notes = models.TextField()
    panel_approved = models.BooleanField()
    genes = models.ManyToManyField('Gene', related_name="panels")
    lims_code = models.CharField(max_length=20)
    #settings

    def __repr__(self):
        return f"Panel: {self.panel_name}"

class Run(models.Model):
    """
    NGS Run. Using the Run as the primary key as new LIMS worklists are inconsistent
    """
    run = models.CharField(max_length=50, primary_key=True)
    worklist = models.CharField(max_length=50, null=True, blank=True)

class PatientAnalysis(models.Model):
    """
    A single analysis of a given patient
    """
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.PROTECT)
    tumour_sample = models.ForeignKey('Sample', on_delete=models.PROTECT, related_name='tumour_sample')
    germline_sample = models.ForeignKey('Sample', on_delete=models.PROTECT, null=True, related_name='germline_sample')
    indication = models.ForeignKey('Indication', on_delete=models.PROTECT)
    run = models.ForeignKey('Run', on_delete=models.PROTECT)
    # QC
    somatic_vaf_distribution = models.ForeignKey('QCSomaticVAFDistribution', on_delete=models.PROTECT)
    tumour_in_normal_contamination = models.ForeignKey('QCTumourInNormalContamination', on_delete=models.PROTECT)
    germline_cnv_quality = models.ForeignKey('QCGermlineCNVQuality', on_delete=models.PROTECT)
    low_quality_tumour_sample = models.ForeignKey('QCLowQualityTumourSample', on_delete=models.PROTECT)
    tumour_ntc_contamination = models.ForeignKey('QCNTCContamination', on_delete=models.PROTECT, related_name='tumour_ntc_contamination')
    germline_ntc_contamination = models.ForeignKey('QCNTCContamination', on_delete=models.PROTECT, related_name='germline_ntc_contamination')
    
class MDTNotes(models.Model):
    """
    Notes on MDTs. Links to a patient so informaiton from multiple analyses is pulled through
    """
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.PROTECT)
    notes = models.TextField()
    date = models.DateField()


#################
### QC Models ###
#################

QC_CHOICES = (
    ("P", "Pass"),
    ("W", "Warn"),
    ("F", "Fail")
)

class AbstractQCCheck(models.Model):
    """
    Base class for QC checks - cannot be instantiated
    """
    status = models.CharField(max_length=1, choices=QC_CHOICES)
    message = models.ForeignKey("QCMessage", on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True

class QCMessage(models.Model):
    """
    Canned messages used for QC checks
    """
    id = models.AutoField(primary_key=True)
    message = models.TextField(max_length=1000)

    def __repr__(self):
        return f"Message: {self.message}"

class QCSomaticVAFDistribution(AbstractQCCheck):
    """
    QC check for somatic VAF distribution
    """
    id = models.AutoField(primary_key=True)
    low_vaf_proportion = models.DecimalField(max_digits=7, decimal_places=6)

class QCTumourInNormalContamination(AbstractQCCheck):
    """
    QC check for TINC
    """
    id = models.AutoField(primary_key=True)
    #TODO add fields when we've decided on script use
    pass

class QCGermlineCNVQuality(AbstractQCCheck):
    """
    QC check for germline CNV quality
    """
    id = models.AutoField(primary_key=True)
    passing_cnv_count = models.IntegerField()
    passing_fraction = models.DecimalField(max_digits=7, decimal_places=6)
    log_loss_gain = models.DecimalField(max_digits=7, decimal_places=5)

class QCLowQualityTumourSample(AbstractQCCheck):
    """
    QC check for low quality tumour sample QC
    """
    id = models.AutoField(primary_key=True)
    unevenness_of_coverage = models.DecimalField(max_digits=7, decimal_places=4)
    median_fragment_length = models.DecimalField(max_digits=7, decimal_places=1)
    at_drop = models.DecimalField(max_digits=7, decimal_places=4)
    cg_drop = models.DecimalField(max_digits=7, decimal_places=4)

class QCNTCContamination(AbstractQCCheck):
    """
    QC check for NTC contamination
    """
    id = models.AutoField(primary_key=True)
    ntc_contamination = models.DecimalField(max_digits=7, decimal_places=6)

################
### Coverage ###
################

class GeneCoverage(models.Model):
    """
    Coverage information for a given gene
    """
    id = models.AutoField(primary_key=True)
    gene = models.ForeignKey("Gene", on_delete=models.PROTECT)
    is_germline = models.BooleanField()
    mean_coverage = models.DecimalField(max_digits=7, decimal_places=1)
    # threshold coverage

################
### Variants ###
################

class GenomeBuild(models.Model):
    """
    Genome Builds
    """
    genome_build = models.CharField(primary_key=True, max_length=10)

class Variant(models.Model):
    """
    An individual SNP/small indel
    """
    variant = models.CharField(primary_key=True, max_length=200)
    genome_build = models.ForeignKey("GenomeBuild", on_delete=models.PROTECT)

class AbstractVariantInstance(models.Model):
    """
    Abstract class for variant instance. Stores the fields common to germline and somatic instances
    """
    variant = models.ForeignKey("Variant", on_delete=models.PROTECT)
    patient_analysis = models.ForeignKey("PatientAnalysis", on_delete=models.PROTECT)
    ad = models.CharField(max_length=10)
    af = models.DecimalField(max_digits=7, decimal_places=6)
    dp = models.IntegerField()
    
    class Meta:
        abstract = True

class GermlineVariantInstance(AbstractVariantInstance):
    """
    
    """
    id = models.AutoField(primary_key=True)
    vep_annotations = models.ForeignKey("GermlineVEPAnnotations", on_delete=models.PROTECT)

class SomaticVariantInstance(AbstractVariantInstance):
    """
    
    """
    id = models.AutoField(primary_key=True)
    vep_annotations = models.ForeignKey("SomaticVEPAnnotations", on_delete=models.PROTECT)

class VEPAnnotationsConsequence(models.Model):
    """
    The variant consequences used by VEP, described here:
    https://www.ensembl.org/info/genome/variation/prediction/predicted_data.html
    """
    consequence = models.CharField(primary_key=True, max_length=50)
    impact = models.ForeignKey("VEPAnnotationsImpact", on_delete=models.PROTECT)

    def format_display_term(self):
        return self.consequence.replace("_"," ")

class VEPAnnotationsImpact(models.Model):
    """
    The impact levels for the different VEP consequences, described here:
    https://www.ensembl.org/info/genome/variation/prediction/predicted_data.html
    """
    impact_level = models.CharField(primary_key=True, max_length=20)

class VEPAnnotationsExistingVariation(models.Model):
    """
    Existing Variations (e.g. rsids) as annotated by VEP
    """
    existing_variation = models.CharField(primary_key=True, max_length=50)

class VEPAnnotationsPubmed(models.Model):
    """
    Pubmed IDs sourced from VEP
    """
    pubmed_id = models.CharField(primary_key=True, max_length=10)

    def format_pubmed_link(self):
        # create a link for the pubmed ID
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pubmed_id}/"


class AbstractVEPAnnotations(models.Model):
    """
    Contains VEP annotation fields common to germline and somatic vep annotations
    VEP annotations are described here:
    https://www.ensembl.org/info/docs/tools/vep/vep_formats.html
    """
    consequence = models.ManyToManyField("VEPAnnotationsConsequence")
    transcript = models.ManyToManyField("Transcript")
    exon = models.CharField(max_length=20, null=True, blank=True)
    intron = models.CharField(max_length=10, null=True, blank=True)
    hgvs_c = models.CharField(max_length=100, null=True, blank=True)
    hgvs_p = models.CharField(max_length=100, null=True, blank=True)
    existing_variation = models.ManyToManyField("VEPAnnotationsExistingVariation")
    pubmed = models.ManyToManyField("VEPAnnotationsPubmed")

    class Meta:
        abstract = True

class VEPAnnotationsClinvar(models.Model):
    """
    Clinvar
    """
    clinvar_id = models.CharField(primary_key=True, max_length=20)
    clinvar_clinsig = models.ManyToManyField("VEPAnnotationsClinvarClinsig")
    clinvar_clinsigconf = models.ManyToManyField("VEPAnnotationsClinvarClinsigConf")

    def format_clinvar_link(self):
        return f"https://www.ncbi.nlm.nih.gov/clinvar/{self.clinvar_id}/"
    
class VEPAnnotationsClinvarClinsig(models.Model):
    """
    Clinical signficance consequences for Clinvar variants
    """
    clinvar_clinsig = models.CharField(primary_key=True, max_length=50)


class VEPAnnotationsClinvarClinsigConf(models.Model):
    """
    Clinical significance consequence scores for Clinvar variants
    """
    clinvar_clinsig_conf = models.CharField(primary_key=True, max_length=10)

class GermlineVEPAnnotations(AbstractVEPAnnotations):
    """
    Adds germline-specific annotations (Clinvar)
    """
    id = models.AutoField(primary_key=True)
    clinvar = models.ManyToManyField("VEPAnnotationsClinvar")

class SomaticVEPAnnotations(AbstractVEPAnnotations):
    """
    
    """
    #TODO fill in these fields once added in cancer hotspots annotations
    pass
    