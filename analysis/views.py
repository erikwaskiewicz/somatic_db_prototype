from django.shortcuts import render

# Create your views here.
def analysis_sheet(request):
    context = {
        'patient_data': {
            'name': 'Bob',
            'lab_no': '21M12345',
        },
        'coverage_data': {
            'BRAF': [
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
            ],
            'KIT': [
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
            ],
            'EGFR': [
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
                {
                    'genomic': '3:574939',
                    'hgvs_c': 'c.12345',
                    'percent_135x': 10,
                    'percent_270x': 5,
                    'ntc': 1
                },
            ],
        },
        'variant_data': 'test',
        'checking_data': 'test',
    }


    return render(request, 'analysis/analysis_sheet.html', context)
