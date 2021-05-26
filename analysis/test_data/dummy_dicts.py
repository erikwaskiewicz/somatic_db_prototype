view_worksheets_dict = {
    'worksheets': [
        {
            'worksheet_id': '21-123',
            'run_id': '210521_A34412_001_dbgwb4q32g34',
            'assay': 'TSO500',
            'status': '1st check | 2nd check',
        },
        {
            'worksheet_id': '21-456',
            'run_id': '210521_A34412_001_dbgwb4q32g34',
            'assay': 'TSO500',
            'status': '2nd check',
        },
        {
            'worksheet_id': '21-789',
            'run_id': '210521_A34412_001_dbgwb4q32g34',
            'assay': 'TSO500',
            'status': 'Complete',
        },
    ],
}

view_samples_dict = {
        'worksheet': '21-123',
        'samples': [
            {
                'sample_id': '21M12345',
                'dna_rna': 'DNA',
                'panels': [
                    {
                        'panel': 'Lung',
                        'status': '1st check',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'Unassigned',
                    },
                ],
            },
            {
                'sample_id': '21M54321',
                'dna_rna': 'RNA',
                'panels': [
                    {
                        'panel': 'Lung',
                        'status': 'Complete',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'N/A',
                    },
                    {
                        'panel': 'Colorectal',
                        'status': '1st check',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'EW',
                    },
                ],
            },
            {
                'sample_id': '21M12345',
                'dna_rna': 'DNA',
                'panels': [
                    {
                        'panel': 'Lung',
                        'status': '1st check',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'Unassigned',
                    },
                ],
            },
            {
                'sample_id': '21M54321',
                'dna_rna': 'RNA',
                'panels': [
                    {
                        'panel': 'Lung',
                        'status': 'Complete',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'N/A',
                    },
                    {
                        'panel': 'Colorectal',
                        'status': '1st check',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'EW',
                    },
                ],
            },
            {
                'sample_id': '21M12345',
                'dna_rna': 'DNA',
                'panels': [
                    {
                        'panel': 'Lung',
                        'status': '1st check',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'Unassigned',
                    },
                ],
            },
            {
                'sample_id': '21M54321',
                'dna_rna': 'RNA',
                'panels': [
                    {
                        'panel': 'Lung',
                        'status': 'Complete',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'N/A',
                    },
                    {
                        'panel': 'Colorectal',
                        'status': '1st check',
                        'analysis_id': 'TODO - link to specific analysis in database',
                        'assigned_to': 'EW',
                    },
                ],
            },
        ]
    }


analysis_sheet_dict = {
        'sample_data': {
            'name': 'Bob',
            'sample_id': '21M12345',
            'worksheet_id': '21-123',
            'panel': 'Colorectal',
            'run_id': '210521_A00646_001_dffjwifwvw',
            'status': '1st check',
            'assigned_to': 'EW',
        },
        'coverage_data': {
            'BRAF': {
                'av_coverage': 300,
                'percent_270x': 50,
                'percent_135x': 90,
                'av_ntc_coverage': 1,
                'percent_ntc': '0.2%',
                'percent_cosmic': '24%',
                'regions': [
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
                'gaps': [
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
            'KIT': {
                'av_coverage': 300,
                'percent_270x': 50,
                'percent_135x': 90,
                'av_ntc_coverage': 1,
                'percent_ntc': '0.2%',
                'percent_cosmic': '3%',
                'regions': [
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
                'gaps': [
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
            'EGFR': {
                'av_coverage': 300,
                'percent_270x': 50,
                'percent_135x': 90,
                'av_ntc_coverage': 1,
                'percent_ntc': '0.2%',
                'percent_cosmic': '4%',
                'regions': [
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
                'gaps': [
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
        },
        'variant_data': {
            'variant_calls': [
                {
                    'genomic': '1:12345A>G',
                    'gene': 'BRAF',
                    'exon': '1|7',
                    'transcript': 'NM_12345.6',
                    'hgvs_c': 'c.123A>G',
                    'hgvs_p': 'p.Ala123Glu',
                    'vaf': {
                        'vaf': '21%',
                        'total_count': '100',
                        'alt_count': '21',
                    },
                    'this_run': {
                        'count': 0, 
                        'total': 29,
                        'ntc': False,
                    },
                    'previous_runs': {
                        'known': 'Tier IIC',
                        'count': 20,
                    },
                    'checks': [
                        'Genuine', 
                        'Artefact',
                    ],
                    'comments': [
                        'test',
                    ],
                },
                {
                    'genomic': '1:12345A>G',
                    'gene': 'BRAF',
                    'exon': '1|7',
                    'transcript': 'NM_12345.6',
                    'hgvs_c': 'c.123A>G',
                    'hgvs_p': 'p.Ala123Glu',
                    'vaf': {
                        'vaf': '21%',
                        'total_count': '100',
                        'alt_count': '21',
                    },
                    'this_run': {
                        'count': 0, 
                        'total': 29,
                        'ntc': False,
                    },
                    'previous_runs': {
                        'known': 'Tier IIC',
                        'count': 20,
                    },
                    'checks': [
                        'Genuine', 
                        'Artefact',
                    ],
                    'comments': [
                        'test',
                    ],
                },
                {
                    'genomic': '1:12345A>G',
                    'gene': 'BRAF',
                    'exon': '1|7',
                    'transcript': 'NM_12345.6',
                    'hgvs_c': 'c.123A>G',
                    'hgvs_p': 'p.Ala123Glu',
                    'vaf': {
                        'vaf': '21%',
                        'total_count': '100',
                        'alt_count': '21',
                    },
                    'this_run': {
                        'count': 0, 
                        'total': 29,
                        'ntc': False,
                    },
                    'previous_runs': {
                        'known': 'Tier IIC',
                        'count': 20,
                    },
                    'checks': [
                        'Genuine', 
                        'Artefact',
                    ],
                    'comments': [
                        'test',
                        'test2',
                    ],
                },
                {
                    'genomic': '1:12345A>G',
                    'gene': 'BRAF',
                    'exon': '1|7',
                    'transcript': 'NM_12345.6',
                    'hgvs_c': 'c.123A>G',
                    'hgvs_p': 'p.Ala123Glu',
                    'vaf': {
                        'vaf': '21%',
                        'total_count': '100',
                        'alt_count': '21',
                    },
                    'this_run': {
                        'count': 0, 
                        'total': 29,
                        'ntc': False,
                    },
                    'previous_runs': {
                        'known': 'Tier IA',
                        'count': 20,
                    },
                    'checks': [
                        'Genuine', 
                        'Artefact',
                    ],
                    'comments': [
                        'test',
                    ],
                },
                {
                    'genomic': '1:12345A>G',
                    'gene': 'BRAF',
                    'exon': '1|7',
                    'transcript': 'NM_12345.6',
                    'hgvs_c': 'c.123A>G',
                    'hgvs_p': 'p.Ala123Glu',
                    'vaf': {
                        'vaf': '21%',
                        'total_count': '100',
                        'alt_count': '21',
                    },
                    'this_run': {
                        'count': 0, 
                        'total': 29,
                        'ntc': False,
                    },
                    'previous_runs': {
                        'known': '',
                        'count': 20,
                    },
                    'checks': [
                        'Genuine', 
                        'Genuine',
                    ],
                    'comments': [],
                },
            ],
            'polys': [
                {
                    'genomic': '1:1234A>T',
                    'gene': 'BRAF',
                    'exon': '4|16',
                    'transcript': 'NM1234',
                    'hgvs_c': 'c.123',
                    'hgvs_p': 'Arg123Ala',
                    'vaf': {
                        'vaf': '21%',
                        'ref_count': '100',
                        'alt_count': '21',
                    },
                },
                {
                    'genomic': '1:1234A>T',
                    'gene': 'BRAF',
                    'exon': '4|16',
                    'transcript': 'NM1234',
                    'hgvs_c': 'c.123',
                    'hgvs_p': 'Arg123Ala',
                    'vaf': {
                        'vaf': '21%',
                        'ref_count': '100',
                        'alt_count': '21',
                    },
                },
            ],
        },
        'checking_data': 'test',
    }
