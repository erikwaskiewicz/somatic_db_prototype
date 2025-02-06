import random
import string

from django.db import models
from django.contrib.auth.models import User
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
    
    def __str__(self):
        return f"{self.gene}"
    
class Transcript(models.Model):
    """
    NCBI transcript identifiers
    """
    transcript = models.CharField(max_length=50, primary_key=True)
    gene = models.ForeignKey("Gene", on_delete=models.CASCADE)

    def __repr__(self):
        return f"Transcript {self.transcript} in gene {self.gene}"
    
    def __str__(self):
        return f"{self.transcript}"

######################
### Analysis Setup ###
######################

class Patient(models.Model):
    """
    An individual patient.
    If NHS number is not available, it is replaced with UNKNOWN[id]
    """
    
    id = models.AutoField(primary_key=True)
    nhs_number = models.CharField(max_length=10, default="UNKNOWN")

    def __str__(self):
        return f"{self.nhs_number}"


class Sample(models.Model):
    """
    An individual sample
    """
    sample_id = models.CharField(max_length=20, primary_key=True)

    def __repr__(self):
        return f"Sample {self.sample_id}"
    
    def __str__(self):
        return f"{self.sample_id}"
    
class Panel(models.Model):
    """
    A virtual panel of genes
    """
    id = models.AutoField(primary_key=True)
    panel_name = models.CharField(max_length=50)
    panel_version = models.DecimalField(max_digits=4, decimal_places=1)
    panel_notes = models.TextField(null=True, blank=True)
    panel_approved = models.BooleanField(default=False)
    genes = models.ManyToManyField('Gene', related_name="panels")
    #settings

    class Meta:
        unique_together = ["panel_name", "panel_version"]

    def __repr__(self):
        return f"Panel: {self.panel_name} {self.panel_version}"
    
    def __str__(self):
        return f"{self.panel_name}_{str(self.panel_version)}"

class Indication(models.Model):
    """
    Indication the patient is being tested for e.g. ALL
    Note: Germline panels being tiers 1 and 3 is deliberate because this is what GEL do
    """
    indication = models.CharField(max_length=20, primary_key=True)
    indication_pretty_print = models.CharField(max_length=100, null=True, blank=True)
    lims_code = models.CharField(max_length=20, null=True, blank=True)
    germline_panels_tier_zero = models.ManyToManyField("Panel", related_name="germline_panels_tier_zero", blank=True)
    germline_panels_tier_one = models.ManyToManyField("Panel", related_name="germline_panels_tier_one")
    germline_panels_tier_three = models.ManyToManyField("Panel", related_name="germline_panels_tier_three")
    somatic_panels_tier_zero = models.ManyToManyField("Panel", related_name="somatic_panels_tier_zero", blank=True)
    somatic_panels_tier_one = models.ManyToManyField("Panel", related_name="somatic_panels_tier_one")
    somatic_panels_tier_two = models.ManyToManyField("Panel", related_name="somatic_panels_tier_two")

    def __repr__(self):
        return f"Indication: {self.indication_pretty_print}"
    
    def __str__(self):
        return f"{self.indication}"
    
    def get_germline_tier_zero_genes(self):
        pass

    def get_germline_tier_one_genes(self):
        pass

    def get_germline_tier_three_genes(self):
        pass

class Run(models.Model):
    """
    NGS Run. Using the Run as the primary key as new LIMS worklists are inconsistent
    """
    run = models.CharField(max_length=50, primary_key=True)
    worksheet = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.run}"

    def get_patient_analysis(self):
        patient_analyses = PatientAnalysis.objects.filter(run=self)
        #patient_analysis_list = []
        #for p in patient_analyses:
            #patient_analysis_list.append(p.id)
        #return patient_analysis_list
        for p in patient_analyses:
            return p.id

class PatientAnalysis(models.Model):
    """
    A single analysis of a given patient
    """
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    tumour_sample = models.ForeignKey('Sample', on_delete=models.CASCADE, related_name='tumour_sample')
    germline_sample = models.ForeignKey('Sample', on_delete=models.CASCADE, null=True, related_name='germline_sample')
    indication = models.ForeignKey('Indication', on_delete=models.CASCADE)
    run = models.ForeignKey('Run', on_delete=models.CASCADE)
    # QC
    somatic_vaf_distribution = models.ForeignKey('QCSomaticVAFDistribution', on_delete=models.CASCADE)
    tumour_in_normal_contamination = models.ForeignKey('QCTumourInNormalContamination', on_delete=models.CASCADE)
    germline_cnv_quality = models.ForeignKey('QCGermlineCNVQuality', on_delete=models.CASCADE)
    low_quality_tumour_sample = models.ForeignKey('QCLowQualityTumourSample', on_delete=models.CASCADE)
    tumour_ntc_contamination = models.ForeignKey('QCNTCContamination', on_delete=models.CASCADE, related_name='tumour_ntc_contamination')
    germline_ntc_contamination = models.ForeignKey('QCNTCContamination', on_delete=models.CASCADE, related_name='germline_ntc_contamination')
    relatedness = models.ForeignKey('QCRelatedness', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.run}_{self.tumour_sample}_{self.germline_sample}"

class MDTNotes(models.Model):
    """
    Notes on MDTs. Links to a patient so informaiton from multiple analyses is pulled through
    """
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
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
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=1, choices=QC_CHOICES)
    #TODO sort message out so there's not loads of data replication
    message = models.TextField(max_length=1000)

    class Meta:
        abstract = True

class QCSomaticVAFDistribution(AbstractQCCheck):
    """
    QC check for somatic VAF distribution
    """
    low_vaf_proportion = models.DecimalField(max_digits=7, decimal_places=6)

    class Meta:
        unique_together = ["status", "message", "low_vaf_proportion"]

class QCTumourInNormalContamination(AbstractQCCheck):
    """
    QC check for TINC
    """
    #TODO add fields when we've decided on script use

    class Meta:
        unique_together = ["status", "message"]

class QCGermlineCNVQuality(AbstractQCCheck):
    """
    QC check for germline CNV quality
    """
    passing_cnv_count = models.IntegerField()
    passing_fraction = models.DecimalField(max_digits=7, decimal_places=6)
    log_loss_gain = models.DecimalField(max_digits=7, decimal_places=5)

    class Meta:
        unique_together = ["passing_cnv_count", "passing_fraction", "log_loss_gain"]

class QCLowQualityTumourSample(AbstractQCCheck):
    """
    QC check for low quality tumour sample QC
    """
    unevenness_of_coverage = models.DecimalField(max_digits=7, decimal_places=4)
    median_fragment_length = models.DecimalField(max_digits=7, decimal_places=1)
    at_drop = models.DecimalField(max_digits=7, decimal_places=4)
    cg_drop = models.DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        unique_together = ["status", "message", "unevenness_of_coverage", "median_fragment_length", "at_drop", "cg_drop"]

class QCNTCContamination(AbstractQCCheck):
    """
    QC check for NTC contamination
    """
    ntc_contamination = models.DecimalField(max_digits=7, decimal_places=6)

    class Meta:
        unique_together = ["status", "message", "ntc_contamination"]

class QCRelatedness(AbstractQCCheck):
    relatedness = models.DecimalField(max_digits=4, decimal_places=3)

    class Meta:
        unique_together = ["status", "message", "relatedness"]

################
### Coverage ###
################

class GeneCoverage(models.Model):
    """
    Coverage information for a given gene
    """
    id = models.AutoField(primary_key=True)
    gene = models.ForeignKey("Gene", on_delete=models.CASCADE)
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
    genome_build = models.CharField(primary_key=True, unique=True, max_length=10)

    def __str__(self):
        return f"{self.genome_build}"

class Variant(models.Model):
    """
    An individual SNP/small indel
    """
    #TODO find a way to default to b38
    variant = models.CharField(primary_key=True, max_length=200)
    genome_build = models.ForeignKey("GenomeBuild", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.variant}"
    
    def split_variant(self):
        chrom = self.variant.split(":")[0]
        pos = self.variant.split(":")[1]
        ref = self.variant.split(":")[2].split(">")[0]
        alt = self.variant.split(":")[2].split(">")[1]
        return chrom, pos, ref, alt

class VEPAnnotationsConsequence(models.Model):
    """
    The variant consequences used by VEP, described here:
    https://www.ensembl.org/info/genome/variation/prediction/predicted_data.html
    """
    consequence = models.CharField(primary_key=True, max_length=50)
    impact = models.ForeignKey("VEPAnnotationsImpact", on_delete=models.CASCADE)

    def format_display_term(self):
        return self.consequence.replace("_"," ")

class VEPAnnotationsImpact(models.Model):
    """
    The impact levels for the different VEP consequences, described here:
    https://www.ensembl.org/info/genome/variation/prediction/predicted_data.html
    """
    impact = models.CharField(primary_key=True, max_length=20)

class VEPAnnotationsExistingVariation(models.Model):
    """
    Existing Variations (e.g. rsids) as annotated by VEP
    """
    existing_variation = models.CharField(primary_key=True, max_length=50)

    # TODO methods to link out e.g. to dbsnp

class VEPAnnotationsPubmed(models.Model):
    """
    Pubmed IDs sourced from VEP
    """
    pubmed_id = models.CharField(primary_key=True, max_length=10)

    def format_pubmed_link(self):
        # create a link for the pubmed ID
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pubmed_id}/"

class VEPAnnotationsClinvar(models.Model):
    """
    Clinvar
    """
    #TODO add clnvarstat
    CLINVAR_CHOICES = (
        ("B", "Benign"),
        ("BLB", "Benign/Likely benign"),
        ("LB", "Likely benign"),
        ("U", "Uncertain significance"),
        ("LP", "Likely pathogenic"),
        ("PLP", "Pathogenic/Likely pathogenic"),
        ("P", "Pathogenic"),
        ("C", "Conflicting classifications of pathogenicity"),
        ("O", "Other")
    )
    #TODO change this to just clinsig and have it be a choice field
    clinvar_id = models.CharField(primary_key=True, max_length=20)
    clinvar_clinsig = models.CharField(max_length=3, choices=CLINVAR_CHOICES)

    def format_clinvar_link(self):
        return f"https://www.ncbi.nlm.nih.gov/clinvar/{self.clinvar_id}/"
    
class VEPAnnotationsCancerHotspots(models.Model):
    """
    Cancer hotspots information for a given somatic variant
    """
    cancer_hotspot = models.CharField(primary_key=True, max_length=20)

    def format_cancer_hotspots_link(self):
        # you currently can't go to the website for a specific variant, return the main link
        return "https://www.cancerhotspots.org/#/home"

class AbstractVEPAnnotations(models.Model):
    """
    Contains VEP annotation fields common to germline and somatic vep annotations
    VEP annotations are described here:
    https://www.ensembl.org/info/docs/tools/vep/vep_formats.html
    """
    id = models.AutoField(primary_key=True)
    consequence = models.ManyToManyField("VEPAnnotationsConsequence")
    transcript = models.ForeignKey("Transcript", on_delete=models.CASCADE)
    exon = models.CharField(max_length=20, null=True, blank=True)
    intron = models.CharField(max_length=10, null=True, blank=True)
    hgvsc = models.CharField(max_length=100, null=True, blank=True)
    hgvsp = models.CharField(max_length=100, null=True, blank=True)
    existing_variation = models.ManyToManyField("VEPAnnotationsExistingVariation")
    pubmed_id = models.ManyToManyField("VEPAnnotationsPubmed")

    class Meta:
        abstract = True

class GermlineVEPAnnotations(AbstractVEPAnnotations):
    """
    Adds germline-specific annotations (Clinvar)
    """
    #clinvar = models.ManyToManyField("VEPAnnotationsClinvar")

    #TODO unique together

class SomaticVEPAnnotations(AbstractVEPAnnotations):
    """
    Adds somatic-specific annotations (Cancer hotspots)
    """
    #cancer_hotspots = models.ForeignKey("VEPAnnotationsCancerHotspots", on_delete=models.CASCADE)

    #TODO unique_together

class AbstractVariantInstance(models.Model):
    """
    Abstract class for variant instance. Stores the fields common to germline and somatic instances
    """
    
    OUTCOME_CHOICES = (
        ('G', 'Genuine'),
        ('A', 'Artefact'),
    )

    STATUS_CHOICES = (
        ('P','Pending'),
        ('C','Complete'),
    )
    
    id = models.AutoField(primary_key=True)
    variant = models.ForeignKey("Variant", on_delete=models.CASCADE)
    patient_analysis = models.ForeignKey("PatientAnalysis", on_delete=models.CASCADE)
    ad = models.CharField(max_length=10)
    af = models.DecimalField(max_digits=7, decimal_places=6)
    dp = models.IntegerField()
    qual = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    max_splice_ai = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    gnomad_popmax_af = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    gnomad_nhomalt = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    decision = models.CharField(max_length=1, choices=OUTCOME_CHOICES, null=True, blank=True)
    
    class Meta:
        abstract = True

    @staticmethod
    def get_chrom_and_pos(variant_id):
        chrom = variant_id.split(":")[0]
        pos = int(variant_id.split(":")[1])
        return chrom, pos
    
    @staticmethod
    def get_worst_modifier_from_vep_annotations(vep_annotations):
        impacts = []
        for vep_annotation in vep_annotations:
            consequences = vep_annotation.consequence.all()
            for consequence in consequences:
                impacts.append(consequence.impact.impact)
        impacts = list(set(impacts))
        if "HIGH" in impacts:
            return "HIGH"
        elif "MEDIUM" in impacts:
            return "MEDIUM"
        elif "LOW" in impacts:
            return "LOW"
        else:
            return "MODIFIER"

class GermlineVariantInstance(AbstractVariantInstance):
    """
    
    """
    vep_annotations = models.ManyToManyField("GermlineVEPAnnotations")

    def display_in_tier_zero(self):
        variant_gene = self.vep_annotations.first().transcript.gene
        associated_panels = variant_gene.panels.all()
        # if any of the associated panels are in a tier 0 panel, display
        for panel in associated_panels:
            if panel in self.patient_analysis.indication.germline_panels_tier_zero.all():
                return True
        return False

    def display_in_tier_one(self):
        """
        Returns a Boolean for if a panel should be displayed in Tier 1
        """
        variant_gene = self.vep_annotations.first().transcript.gene
        associated_panels = variant_gene.panels.all()
        # if any of the associated panels are in a tier 1 panel, display
        for panel in associated_panels:
            if panel in self.patient_analysis.indication.germline_panels_tier_one.all():
                return True
        return False
        
    def display_in_tier_three(self):
        variant_gene = self.vep_annotations.first().transcript.gene
        associated_panels = variant_gene.panels.all()
        # if any of the associated panels are in a tier 3 panel, display
        for panel in associated_panels:
            if panel in self.patient_analysis.indication.germline_panels_tier_three.all():
                return True
        return False
    
    def force_display(self):
        """
        A potentially informative MNV could be split to multiple SNVs during annotation and we could lose information
        Function force-includes variants called +-2 bp (potentially same codon) irrespective of other filtering criteria outside of gene
        """
        # get the 2 closest variants to this one
        id_lower_limit = self.id - 1
        id_upper_limit = self.id + 1
        close_variants = GermlineVariantInstance.objects.filter(patient_analysis=self.patient_analysis, id__range=[id_lower_limit, id_upper_limit])

        # if we get an empty list there are no other variants, return False (but also this is weird)
        if len(close_variants) == 0:
            return False
        
        else:
            # get chrom and pos for this variant
            chrom, pos = self.get_chrom_and_pos(self.variant.variant)

            for variant in close_variants:
                close_chrom, close_pos = self.get_chrom_and_pos(variant.variant.variant)

                # if the variant is within 2bp, compare the consequences
                if chrom == close_chrom and abs(pos - close_pos) in [1, 2]:
                    if self.get_worst_modifier_from_vep_annotations(self.vep_annotations.all()) != "MODIFIER" or variant.get_worst_modifier_from_vep_annotations(variant.vep_annotations.all()) != "MODIFIER":
                        return True
            
            # otherwise the nearest variants are > 2bp away
            return False
        
    def update_status(self):
        """
        Update status if last two checks are matching
        """

        print("HELLO")
        all_checks = GermlineIGVCheck.objects.filter(variant_instance__id = self.id).order_by('-check_date')

        print(all_checks)


        

class SomaticVariantInstance(AbstractVariantInstance):
    """
    
    """
    vep_annotations = models.ManyToManyField("SomaticVEPAnnotations")

    def display_in_tier_zero(self):
        variant_gene = self.vep_annotations.first().transcript.gene
        associated_panels = variant_gene.panels.all()
        # if any of the associated panels are in a tier 0 panel, display
        for panel in associated_panels:
            if panel in self.patient_analysis.indication.somatic_panels_tier_zero.all():
                return True
        return False

    def display_in_tier_one(self):
        """
        Returns a Boolean for if a panel should be displayed in Tier 1
        """
        variant_gene = self.vep_annotations.first().transcript.gene
        associated_panels = variant_gene.panels.all()
        # if any of the associated panels are in a tier 1 panel, display
        for panel in associated_panels:
            if panel in self.patient_analysis.indication.somatic_panels_tier_one.all():
                return True
        return False
        
    def display_in_tier_two(self):
        variant_gene = self.vep_annotations.first().transcript.gene
        associated_panels = variant_gene.panels.all()
        # if any of the associated panels are in a tier 2 panel, display
        for panel in associated_panels:
            if panel in self.patient_analysis.indication.somatic_panels_tier_two.all():
                return True
        return False
    
    def force_display(self):
        """
        A potentially informative MNV could be split to multiple SNVs during annotation and we could lose information
        Function force-includes variants called +-2 bp (potentially same codon) irrespective of other filtering criteria outside of gene
        """
        # get the 2 closest variants to this one
        id_lower_limit = self.id - 1
        id_upper_limit = self.id + 1
        close_variants = SomaticVariantInstance.objects.filter(patient_analysis=self.patient_analysis, id__range=[id_lower_limit, id_upper_limit])

        # if we get an empty list there are no other variants, return False (but also this is weird)
        if len(close_variants) == 0:
            return False
        
        else:
            # get chrom and pos for this variant
            chrom, pos = self.get_chrom_and_pos(self.variant.variant)
            for variant in close_variants:
                close_chrom, close_pos = self.get_chrom_and_pos(variant.variant.variant)

                # if the variant is within 2bp, force display should be true
                if chrom == close_chrom and abs(pos - close_pos) in [1, 2]:
                    if self.get_worst_modifier_from_vep_annotations(self.vep_annotations.all()) != "MODIFIER" or variant.get_worst_modifier_from_vep_annotations(variant.vep_annotations.all()) != "MODIFIER":
                        return True
            
            # otherwise the nearest variants are > 2bp away
            return False
        
    def update_status(self):
        """
        Update status if last two checks are matching
        """

        print("HELLO SOMATIC")
        all_checks = SomaticIGVCheck.objects.filter(variant_instance__id = self.id).order_by('-check_date')

        print(all_checks)

class AbstractVariantChecks(models.Model):
    """
    Abstract class for variant checks. Stores the fields common to all checks
    """

    OUTCOME_CHOICES = (
        ('G', 'Genuine'),
        ('A', 'Artefact'),
    )

    decision = models.CharField(max_length=1, choices = OUTCOME_CHOICES, blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT, blank=True, null=True)
    check_date = models.DateTimeField(blank=True, null=True)
        
    class Meta:
        abstract = True

class GermlineIGVCheck(AbstractVariantChecks):
    """
    IGV checks for germline variants
    """
    
    variant_instance = models.ForeignKey(GermlineVariantInstance, on_delete=models.CASCADE)

class SomaticIGVCheck(AbstractVariantChecks):
    """
    IGV checks for somatic variants
    """

    variant_instance = models.ForeignKey(SomaticVariantInstance, on_delete=models.CASCADE)



