import csv
import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import *
from .forms import *

@login_required
def home_swgs(request):
    """
    """
    return render(request, 'swgs/home.html', {})

@login_required
def view_runs(request):
    """
    View runs / worksheets
    """

    # get all the runs
    runs = Run.objects.all().order_by("-run")
    runs_list = []
    for run in runs:
        run_dict = {
            "run": run.run,
            "worksheet": run.worksheet,
            "patient_analyses": run.get_patient_analysis()
        }
        runs_list.append(run_dict)

    # context dictionary
    context = {
        'runs': runs_list
    }

    return render(request, "swgs/view_runs.html", context)

@login_required
def view_patient_analysis(request, patient_id):
    """
    View variants in a PatientAnalysis
    """

    download_csv_form = DownloadCsvForm()

    patient_analysis = PatientAnalysis.objects.get(id=patient_id)

    germline_snvs_query = GermlineVariantInstance.objects.filter(patient_analysis=patient_analysis)
    somatic_snvs_query = SomaticVariantInstance.objects.filter(patient_analysis=patient_analysis)
    germline_snvs = []
    somatic_snvs = []

    disallowed_consequences_query = VEPAnnotationsConsequence.objects.filter(impact__impact="MODIFIER")
    disallowed_consequences = [c.consequence for c in disallowed_consequences_query]

    for v in somatic_snvs_query:
        variant = v.variant.variant
        gnomad = v.gnomad_popmax_af
        vaf = float(v.af) * 100
        vep_annotations = v.vep_annotations.first()
        hgvsc = vep_annotations.hgvsc
        hgvsp = vep_annotations.hgvsp
        gene = vep_annotations.transcript.gene.gene
        consequences = vep_annotations.consequence.all()
        impacts = list(set(consequence.impact.impact for consequence in consequences))
        consequences = [c.consequence for c in consequences]
        consequences_formatted = [c.replace("_", " ") for c in consequences]
        consequences_formatted = " | ".join(consequences)
        if float(gnomad) >= 0.05 or (len(impacts) == 1 and impacts[0] == "MODIFIER"):
            pass
        elif float(gnomad) == -1:
            
            gnomad = "Not in Gnomad"
            variant_dict = {
                "pk": variant,
                "gnomad": gnomad,
                "vaf": f"{vaf:.2f}",
                "hgvsc": hgvsc,
                "hgvsp": hgvsp,
                "gene": gene,
                "consequence": consequences_formatted
            }
            somatic_snvs.append(variant_dict)
        else:
            variant_dict = {
                "pk": variant,
                "gnomad": f"{gnomad:.3f}%",
                "vaf": f"{vaf:.2f}",
                "hgvsc": hgvsc,
                "hgvsp": hgvsp,
                "gene": gene,
                "consequence": consequences_formatted
            }
            somatic_snvs.append(variant_dict)

    for v in germline_snvs_query:
        variant = v.variant.variant
        gnomad = v.gnomad_popmax_af
        vaf = float(v.af) * 100
        vep_annotations = v.vep_annotations.first()
        hgvsc = vep_annotations.hgvsc
        hgvsp = vep_annotations.hgvsp
        gene = vep_annotations.transcript.gene.gene
        consequences = vep_annotations.consequence.all()
        impacts = list(set(consequence.impact.impact for consequence in consequences))
        consequences = [c.consequence for c in consequences]
        consequences_formatted = [c.replace("_", " ") for c in consequences]
        consequences_formatted = " | ".join(consequences)
        if float(gnomad) >= 0.05 or (len(impacts) == 1 and impacts[0] == "MODIFIER"):
            pass
        elif float(gnomad) == -1:
            
            gnomad = "Not in Gnomad"
            variant_dict = {
                "pk": variant,
                "gnomad": gnomad,
                "vaf": f"{vaf:.2f}",
                "hgvsc": hgvsc,
                "hgvsp": hgvsp,
                "gene": gene,
                "consequence": consequences_formatted
            }
            germline_snvs.append(variant_dict)
        else:
            variant_dict = {
                "pk": variant,
                "gnomad": f"{gnomad:.3f}%",
                "vaf": f"{vaf:.2f}",
                "hgvsc": hgvsc,
                "hgvsp": hgvsp,
                "gene": gene,
                "consequence": consequences_formatted
            }
            germline_snvs.append(variant_dict)
    
    context = {
        "form": download_csv_form,
        "patient_analysis": patient_analysis,
        "somatic_snvs": somatic_snvs,
        "germline_snvs": germline_snvs
    }

    # Download a csv
    if request.POST:

        today = datetime.date.today().strftime("%Y%m%d")
        filename = f"{patient_analysis.tumour_sample.sample_id}_{patient_analysis.germline_sample.sample_id}_{today}"
        response = HttpResponse(content_type = "text/csv")
        response["Content-Disposition"] = f"attachement; filename={filename}"
        
        csv_writer = csv.writer(response)
        header_line = ["Germline_or_Somatic", "Variant", "Gene", "Consequence", "HGVSC", "HGVSP", "VAF", "GnomAD"]
        csv_writer.writerow(header_line)
        for variant in somatic_snvs:
            csv_writer.writerow(["somatic", variant["pk"], variant["gene"], variant["consequence"], variant["hgvsc"], variant["hgvsp"], f"{variant['vaf']}%", variant["gnomad"]])
        for variant in germline_snvs:
            csv_writer.writerow(["germline", variant["pk"], variant["gene"], variant["consequence"], variant["hgvsc"], variant["hgvsp"], f"{variant['vaf']}%", variant["gnomad"]])

        return response

    return render(request, "swgs/view_patient_analysis.html", context)
    