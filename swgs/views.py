import csv
import datetime
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

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
def view_panels(request):
    """
    View panels, panel update pages
    """
    pass


@login_required
def view_patient_analysis(request, patient_id):
    """
    View variants in a PatientAnalysis
    """

    download_csv_form = DownloadCsvForm()

    patient_analysis = PatientAnalysis.objects.get(id=patient_id)

    check_options = AbstractVariantInstance.OUTCOME_CHOICES

    germline_snvs_query = GermlineVariantInstance.objects.filter(patient_analysis=patient_analysis)
    somatic_snvs_query = SomaticVariantInstance.objects.filter(patient_analysis=patient_analysis)
    germline_snvs_tier_one = []
    germline_snvs_tier_three = []
    somatic_snvs_tier_one = []
    somatic_snvs_tier_two = []

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
        force_display = v.force_display()
        status = v.get_status_display()
        id = v.id
        var_type = "somatic"
        checks = v.get_all_checks()

        # handle gnomad
        if float(gnomad) == -1:
            gnomad_formatted = "Not in Gnomad"
        else:
            gnomad_formatted = f"{gnomad:.3f}%"

        # make variant dict
        variant_dict = {
                "pk": variant,
                "gnomad": gnomad_formatted,
                "vaf": f"{vaf:.2f}",
                "hgvsc": hgvsc,
                "hgvsp": hgvsp,
                "gene": gene,
                "consequence": consequences_formatted,
                "force_display": force_display,
                "status": status,
                "id": id,
                "var_type": var_type,
                "checks": checks

            }

        # lose >5% in gnomad and modifier only variants
        if float(gnomad) >= 0.05 or (len(impacts) == 1 and impacts[0] == "MODIFIER"):
            if not force_display:
                continue

        # Put in tier list
        if v.display_in_tier_zero():
            variant_dict["tier"] = "0"
            somatic_snvs_tier_one.append(variant_dict)
        elif v.display_in_tier_one():
            variant_dict["tier"] = "1"
            somatic_snvs_tier_one.append(variant_dict)
        elif v.display_in_tier_two():
            variant_dict["tier"] = "2"
            somatic_snvs_tier_two.append(variant_dict)
        else:
            pass

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
        force_display = v.force_display()
        status = v.get_status_display()
        id = v.id
        var_type = "germline"
        checks = v.get_all_checks()

        # handle gnomad
        if float(gnomad) == -1:
            gnomad_formatted = "Not in Gnomad"
        else:
            gnomad_formatted = f"{gnomad:.3f}%"

        # make variant dict
        variant_dict = {
                "pk": variant,
                "gnomad": gnomad_formatted,
                "vaf": f"{vaf:.2f}",
                "hgvsc": hgvsc,
                "hgvsp": hgvsp,
                "gene": gene,
                "consequence": consequences_formatted,
                "force_display": force_display,
                "status": status,
                "id": id,
                "var_type": var_type,
                "checks": checks
            }

        # lose >5% in gnomad and modifier only variants
        if float(gnomad) >= 0.05 or (len(impacts) == 1 and impacts[0] == "MODIFIER"):
            if not force_display:
                continue

        # Put in tier list
        if v.display_in_tier_zero():
            variant_dict["tier"] = "0"
            germline_snvs_tier_one.append(variant_dict)
        elif v.display_in_tier_one():
            variant_dict["tier"] = "1"
            germline_snvs_tier_one.append(variant_dict)
        elif v.display_in_tier_three():
            variant_dict["tier"] = "3"
            germline_snvs_tier_three.append(variant_dict)
        else:
            pass
    
    context = {
        "form": download_csv_form,
        "patient_analysis": patient_analysis,
        "somatic_snvs_tier_one": somatic_snvs_tier_one,
        "somatic_snvs_tier_two": somatic_snvs_tier_two,
        "germline_snvs_tier_one": germline_snvs_tier_one,
        "germline_snvs_tier_three": germline_snvs_tier_three,
        "check_options": check_options
    }

    # Download a csv
    if request.POST:

        today = datetime.date.today().strftime("%Y%m%d")
        filename = f"{patient_analysis.tumour_sample.sample_id}_{patient_analysis.germline_sample.sample_id}_{today}"
        response = HttpResponse(content_type = "text/csv")
        response["Content-Disposition"] = f"attachement; filename={filename}"
        
        somatic_snvs = somatic_snvs_tier_one + somatic_snvs_tier_two
        germline_snvs = germline_snvs_tier_one + germline_snvs_tier_three

        csv_writer = csv.writer(response)
        header_line = ["Germline_or_Somatic", "Variant", "Gene", "Tier", "Consequence", "HGVSC", "HGVSP", "VAF", "GnomAD"]
        csv_writer.writerow(header_line)
        for variant in somatic_snvs:
            if variant["tier"] != "None":
                csv_writer.writerow(["somatic", variant["pk"], variant["gene"], variant["tier"], variant["consequence"], variant["hgvsc"], variant["hgvsp"], f"{variant['vaf']}%", variant["gnomad"]])
        for variant in germline_snvs:
            if variant["tier"] != "None":
                csv_writer.writerow(["germline", variant["pk"], variant["gene"], variant["tier"], variant["consequence"], variant["hgvsc"], variant["hgvsp"], f"{variant['vaf']}%", variant["gnomad"]])

        return response

    return render(request, "swgs/view_patient_analysis.html", context)

def ajax(request):
    """
    Ajax handling of the variant check submission
    """

    if request.is_ajax():
        
        selections = json.loads(request.POST.get('selections'))
        patient_pk = request.POST.get('patient_analysis_pk')
        
        for variant in selections:
                
                #Get decision
                decision = selections[variant][1]['genuine_dropdown']

                #Get variant object - use type marker to determine what kind of check and then create check object
                type = selections[variant][0]
                
                if type == "germline":

                    variant_obj = GermlineVariantInstance.objects.get(id=variant)
                    check_obj = GermlineIGVCheck.objects.create(variant_instance = variant_obj,
                                                                 decision = decision,
                                                                 user = request.user,
                                                                 check_date = timezone.now())
                    check_obj.save()
                   
                elif type == "somatic":

                    variant_obj = SomaticVariantInstance.objects.get(id=variant)
                    check_obj = SomaticIGVCheck.objects.create(variant_instance = variant_obj,
                                                               decision = decision,
                                                               user = request.user,
                                                               check_date = timezone.now())
                    check_obj.save()

                #Update status of variant_obj - ie complete if last two checks matching
                variant_obj.update_status()

        return JsonResponse({"status": "success", "redirect_url": f"/swgs/view_patient_analysis/{patient_pk}"})

    return JsonResponse({"status": "error"}, status=400)
    