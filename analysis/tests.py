import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "somatic_variant_db.settings")

import django
django.setup()

from django.test import TestCase
from django.urls import reverse
from analysis.forms import *
from analysis.utils import *


class TestViews(TestCase):


	def test_signup(self):
		self.client.logout()
		response = self.client.get('/signup', follow=True)
		self.assertEqual(response.status_code,200)



	def test_login(self):
		self.client.logout()
		response = self.client.get('/login', follow=True)
		self.assertEqual(response.status_code,200)


	def setUp(self):
		self.client.login(username='test', password= 'hello123')


	def test_view_worksheets(self):
		response = self.client.get('/worksheets')
		self.assertEqual(response.status_code,200)


	def test_logout(self):
		response = self.client.get('/logout', follow=True)
		self.assertEqual(response.status_code,200)


	def test_get_samples(self):

		samples = SampleAnalysis.objects.filter(worksheet = "w3")
		samples_dict= get_samples(samples)
		self.assertEqual(list(samples_dict.keys()), ['21M00305-control'])
		sample=samples_dict.get('21M00305-control')
		self.assertEqual(sample.get('dna_rna'), 'DNA')


		samples = SampleAnalysis.objects.filter(worksheet = "w2")
		samples_dict= get_samples(samples)
		self.assertEqual(list(samples_dict.keys()), ['21M81042-control'])
		sample=samples_dict.get('21M81042-control')
		self.assertEqual(sample.get('dna_rna'), 'RNA')


	def test_get_sample_info(self):

		panel_obj = Panel.objects.filter(panel_name="Tumour", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk

		sample_obj = SampleAnalysis.objects.filter(panel=panel_pk)
		for sample in sample_obj:

			sample_info=get_sample_info(sample)
			self.assertEqual(sample_info.get('dna_or_rna'), 'DNA')
			self.assertEqual(sample_info.get('sample_id'), '21M00305-control')
			self.assertEqual(sample_info.get('worksheet_id'), 'w3')
			self.assertEqual(sample_info.get('panel'), 'Tumour')
			self.assertEqual(sample_info.get('run_id'), 'run')
			self.assertEqual(sample_info.get('total_reads'), None)
			self.assertEqual(sample_info.get('total_reads_ntc'), None)
			self.assertEqual((sample_info.get('checks')).get('current_status'), 'IGV check 1')
			self.assertEqual((sample_info.get('checks')).get('assigned_to'), None)


		#RNA Tumour
		samples_RNA = SampleAnalysis.objects.filter(sample_id="21M81042-control")
		sample_0=samples_RNA[0]

		sample_info_RNA_0=get_sample_info(sample_0)
		self.assertEqual(sample_info_RNA_0.get('dna_or_rna'), 'RNA')
		self.assertEqual(sample_info_RNA_0.get('sample_id'), '21M81042-control')
		self.assertEqual(sample_info_RNA_0.get('worksheet_id'), 'w2')
		self.assertEqual(sample_info_RNA_0.get('panel'), 'Tumour')
		self.assertEqual(sample_info_RNA_0.get('run_id'), 'run')
		self.assertEqual(sample_info_RNA_0.get('total_reads'), 9000004)
		self.assertEqual(sample_info_RNA_0.get('total_reads_ntc'), 596)
		self.assertEqual((sample_info_RNA_0.get('checks')).get('current_status'), 'IGV check 1')
		self.assertEqual((sample_info_RNA_0.get('checks')).get('assigned_to'), None)

		#RNA Glioma
		sample_1=samples_RNA[1]
		sample_info_RNA_1=get_sample_info(sample_1)
		self.assertEqual(sample_info_RNA_1.get('dna_or_rna'), 'RNA')
		self.assertEqual(sample_info_RNA_1.get('sample_id'), '21M81042-control')
		self.assertEqual(sample_info_RNA_1.get('worksheet_id'), 'w2')
		self.assertEqual(sample_info_RNA_1.get('panel'), 'Glioma')
		self.assertEqual(sample_info_RNA_1.get('run_id'), 'run')
		self.assertEqual(sample_info_RNA_1.get('total_reads'), 23875300)
		self.assertEqual(sample_info_RNA_1.get('total_reads_ntc'), 6170)
		self.assertEqual((sample_info_RNA_1.get('checks')).get('current_status'), 'IGV check 1')
		self.assertEqual((sample_info_RNA_1.get('checks')).get('assigned_to'), None)


		#RNA GIST
		sample_2=samples_RNA[2]
		sample_info_RNA_2=get_sample_info(sample_2)
		self.assertEqual(sample_info_RNA_2.get('dna_or_rna'), 'RNA')
		self.assertEqual(sample_info_RNA_2.get('sample_id'), '21M81042-control')
		self.assertEqual(sample_info_RNA_2.get('worksheet_id'), 'w2')
		self.assertEqual(sample_info_RNA_2.get('panel'), 'GIST')
		self.assertEqual(sample_info_RNA_2.get('run_id'), 'run')
		self.assertEqual(sample_info_RNA_2.get('total_reads'), 69576959)
		self.assertEqual(sample_info_RNA_2.get('total_reads_ntc'), 765)
		self.assertEqual((sample_info_RNA_2.get('checks')).get('current_status'), 'IGV check 1')
		self.assertEqual((sample_info_RNA_2.get('checks')).get('assigned_to'), None)


		#RNA Melanoma
		sample_3=samples_RNA[3]
		sample_info_RNA_3=get_sample_info(sample_3)
		self.assertEqual(sample_info_RNA_3.get('dna_or_rna'), 'RNA')
		self.assertEqual(sample_info_RNA_3.get('sample_id'), '21M81042-control')
		self.assertEqual(sample_info_RNA_3.get('worksheet_id'), 'w2')
		self.assertEqual(sample_info_RNA_3.get('panel'), 'Melanoma')
		self.assertEqual(sample_info_RNA_3.get('run_id'), 'run')
		self.assertEqual(sample_info_RNA_3.get('total_reads'), 34444)
		self.assertEqual(sample_info_RNA_3.get('total_reads_ntc'), 6170)
		self.assertEqual((sample_info_RNA_3.get('checks')).get('current_status'), 'IGV check 1')
		self.assertEqual((sample_info_RNA_3.get('checks')).get('assigned_to'), None)

		#RNA Lung
		sample_4=samples_RNA[4]
		sample_info_RNA_4=get_sample_info(sample_4)
		self.assertEqual(sample_info_RNA_4.get('dna_or_rna'), 'RNA')
		self.assertEqual(sample_info_RNA_4.get('sample_id'), '21M81042-control')
		self.assertEqual(sample_info_RNA_4.get('worksheet_id'), 'w2')
		self.assertEqual(sample_info_RNA_4.get('panel'), 'Lung')
		self.assertEqual(sample_info_RNA_4.get('run_id'), 'run')
		self.assertEqual(sample_info_RNA_4.get('total_reads'), 8795879)
		self.assertEqual(sample_info_RNA_4.get('total_reads_ntc'), 34)
		self.assertEqual((sample_info_RNA_4.get('checks')).get('current_status'), 'IGV check 1')
		self.assertEqual((sample_info_RNA_4.get('checks')).get('assigned_to'), None)

		#RNA Thyroid
		sample_5=samples_RNA[5]
		sample_info_RNA_5=get_sample_info(sample_5)
		self.assertEqual(sample_info_RNA_5.get('dna_or_rna'), 'RNA')
		self.assertEqual(sample_info_RNA_5.get('sample_id'), '21M81042-control')
		self.assertEqual(sample_info_RNA_5.get('worksheet_id'), 'w2')
		self.assertEqual(sample_info_RNA_5.get('panel'), 'Thyroid')
		self.assertEqual(sample_info_RNA_5.get('run_id'), 'run')
		self.assertEqual(sample_info_RNA_5.get('total_reads'), 6000)
		self.assertEqual(sample_info_RNA_5.get('total_reads_ntc'), 170)
		self.assertEqual((sample_info_RNA_5.get('checks')).get('current_status'), 'IGV check 1')
		self.assertEqual((sample_info_RNA_5.get('checks')).get('assigned_to'), None)

		#RNA Thyroid
		sample_6=samples_RNA[6]
		sample_info_RNA_6=get_sample_info(sample_6)
		self.assertEqual(sample_info_RNA_6.get('dna_or_rna'), 'RNA')
		self.assertEqual(sample_info_RNA_6.get('sample_id'), '21M81042-control')
		self.assertEqual(sample_info_RNA_6.get('worksheet_id'), 'w2')
		self.assertEqual(sample_info_RNA_6.get('panel'), 'NTRK')
		self.assertEqual(sample_info_RNA_6.get('run_id'), 'run')
		self.assertEqual(sample_info_RNA_6.get('total_reads'), 1070560)
		self.assertEqual(sample_info_RNA_6.get('total_reads_ntc'), 14)
		self.assertEqual((sample_info_RNA_6.get('checks')).get('current_status'), 'IGV check 1')
		self.assertEqual((sample_info_RNA_6.get('checks')).get('assigned_to'), None)



	def test_get_variant_info(self):

		#Tumour

		panel_obj = Panel.objects.filter(panel_name="Tumour", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk

		samples = SampleAnalysis.objects.filter(sample_id="21M00305-control", panel=panel_pk)

		for sample in samples:

			sample_data=get_sample_info(sample)

			variant_data=get_variant_info(sample_data, sample)
			variant_calls=variant_data.get('variant_calls')
			variant_0=variant_calls[0]
			variant_5=variant_calls[5]
			variant_14=variant_calls[14]
			variant_22=variant_calls[22]
			variant_37=variant_calls[37]
			variant_44=variant_calls[44]
			variant_58=variant_calls[58]
			variant_63=variant_calls[63]
			variant_72=variant_calls[72]
			variant_77=variant_calls[77]

			self.assertEqual(variant_0.get('genomic'), '1:27023212C>T')
			self.assertEqual(variant_0.get('gene'), 'ARID1A')
			self.assertEqual(variant_0.get('exon'), '1/20')
			self.assertEqual(variant_0.get('hgvs_c'), 'NM_006015.4:c.318C>T')
			self.assertEqual(variant_0.get('hgvs_p'), 'NM_006015.4:c.318C>T(p.(Asn106=))')
			self.assertEqual((variant_0.get('vaf').get('vaf')), 9)
			self.assertEqual((variant_0.get('vaf').get('total_count')), 338)
			self.assertEqual((variant_0.get('vaf').get('alt_count')), 32)
			self.assertEqual(variant_0.get('checks'), ['Pending'])

			self.assertEqual(variant_5.get('genomic'), '1:27105930TG>T')
			self.assertEqual(variant_5.get('gene'), 'ARID1A')
			self.assertEqual(variant_5.get('exon'), '20/20')
			self.assertEqual(variant_5.get('hgvs_c'), 'NM_006015.4:c.5548del')
			self.assertEqual(variant_5.get('hgvs_p'), 'NP_006006.3:p.(Asp1850ThrfsTer33)')
			self.assertEqual((variant_5.get('vaf').get('vaf')), 10)
			self.assertEqual((variant_5.get('vaf').get('total_count')), 1659)
			self.assertEqual((variant_5.get('vaf').get('alt_count')), 171)
			self.assertEqual(variant_5.get('checks'), ['Pending'])

			self.assertEqual(variant_14.get('genomic'), '7:55241707G>A')
			self.assertEqual(variant_14.get('gene'), 'EGFR')
			self.assertEqual(variant_14.get('exon'), '18/28')
			self.assertEqual(variant_14.get('hgvs_c'), 'NM_005228.4:c.2155G>A')
			self.assertEqual(variant_14.get('hgvs_p'), 'NP_005219.2:p.(Gly719Ser)')
			self.assertEqual((variant_14.get('vaf').get('vaf')), 4)
			self.assertEqual((variant_14.get('vaf').get('total_count')), 1608)
			self.assertEqual((variant_14.get('vaf').get('alt_count')), 77)
			self.assertEqual(variant_14.get('checks'), ['Pending'])

			self.assertEqual(variant_22.get('genomic'), '10:43595968A>G')
			self.assertEqual(variant_22.get('gene'), 'RET')
			self.assertEqual(variant_22.get('exon'), '2/20')
			self.assertEqual(variant_22.get('hgvs_c'), 'NM_020975.4:c.135=')
			self.assertEqual(variant_22.get('hgvs_p'), 'NM_020975.4:c.135=(p.(Ala45=))')
			self.assertEqual((variant_22.get('vaf').get('vaf')), 75)
			self.assertEqual((variant_22.get('vaf').get('total_count')), 1573)
			self.assertEqual((variant_22.get('vaf').get('alt_count')), 1187)
			self.assertEqual(variant_22.get('checks'), ['Pending'])

			self.assertEqual(variant_37.get('genomic'), '13:32911463A>G')
			self.assertEqual(variant_37.get('gene'), 'BRCA2')
			self.assertEqual(variant_37.get('exon'), '11/27')
			self.assertEqual(variant_37.get('hgvs_c'), 'NM_000059.3:c.2971A>G')
			self.assertEqual(variant_37.get('hgvs_p'), 'NP_000050.2:p.(Asn991Asp)')
			self.assertEqual((variant_37.get('vaf').get('vaf')), 10)
			self.assertEqual((variant_37.get('vaf').get('total_count')), 943)
			self.assertEqual((variant_37.get('vaf').get('alt_count')), 101)
			self.assertEqual(variant_37.get('checks'), ['Pending'])

			self.assertEqual(variant_44.get('genomic'), '13:32913836CA>C')
			self.assertEqual(variant_44.get('gene'), 'BRCA2')
			self.assertEqual(variant_44.get('exon'), '11/27')
			self.assertEqual(variant_44.get('hgvs_c'), 'NM_000059.3:c.5351del')
			self.assertEqual(variant_44.get('hgvs_p'), 'NP_000050.2:p.(Asn1784ThrfsTer7)')
			self.assertEqual((variant_44.get('vaf').get('vaf')), 12)
			self.assertEqual((variant_44.get('vaf').get('total_count')), 998)
			self.assertEqual((variant_44.get('vaf').get('alt_count')), 124)
			self.assertEqual(variant_44.get('checks'), ['Pending'])

			self.assertEqual(variant_58.get('genomic'), '17:41234470A>G')
			self.assertEqual(variant_58.get('gene'), 'BRCA1')
			self.assertEqual(variant_58.get('exon'), '12/23')
			self.assertEqual(variant_58.get('hgvs_c'), 'NM_007294.3:c.4308T>C')
			self.assertEqual(variant_58.get('hgvs_p'), 'NM_007294.3:c.4308T>C(p.(Ser1436=))')
			self.assertEqual((variant_58.get('vaf').get('vaf')), 20)
			self.assertEqual((variant_58.get('vaf').get('total_count')), 1698)
			self.assertEqual((variant_58.get('vaf').get('alt_count')), 346)
			self.assertEqual(variant_58.get('checks'), ['Pending'])

			self.assertEqual(variant_63.get('genomic'), '17:41245090T>C')
			self.assertEqual(variant_63.get('gene'), 'BRCA1')
			self.assertEqual(variant_63.get('exon'), '10/23')
			self.assertEqual(variant_63.get('hgvs_c'), 'NM_007294.3:c.2458A>G')
			self.assertEqual(variant_63.get('hgvs_p'), 'NP_009225.1:p.(Lys820Glu)')
			self.assertEqual((variant_63.get('vaf').get('vaf')), 10)
			self.assertEqual((variant_63.get('vaf').get('total_count')), 1662)
			self.assertEqual((variant_63.get('vaf').get('alt_count')), 173)
			self.assertEqual(variant_63.get('checks'), ['Pending'])

			self.assertEqual(variant_72.get('genomic'), 'X:76937963G>C')
			self.assertEqual(variant_72.get('gene'), 'ATRX')
			self.assertEqual(variant_72.get('exon'), '9/35')
			self.assertEqual(variant_72.get('hgvs_c'), 'NM_000489.4:c.2785=')
			self.assertEqual(variant_72.get('hgvs_p'), 'NM_000489.4:c.2785=(p.(Glu929=))')
			self.assertEqual((variant_72.get('vaf').get('vaf')), 30)
			self.assertEqual((variant_72.get('vaf').get('total_count')), 702)
			self.assertEqual((variant_72.get('vaf').get('alt_count')), 213)
			self.assertEqual(variant_72.get('checks'), ['Pending'])

			self.assertEqual(variant_77.get('genomic'), '13:32972286AT>-')
			self.assertEqual(variant_77.get('gene'), 'N4BP2L1')
			self.assertEqual(variant_77.get('exon'), '')
			self.assertEqual(variant_77.get('hgvs_c'), '')
			self.assertEqual(variant_77.get('hgvs_p'), '')
			self.assertEqual((variant_77.get('vaf').get('vaf')), 5)
			self.assertEqual((variant_77.get('vaf').get('total_count')), 355)
			self.assertEqual((variant_77.get('vaf').get('alt_count')), 21)
			self.assertEqual(variant_77.get('checks'), ['Pending'])



		#Glioma

		panel_obj = Panel.objects.filter(panel_name="Glioma", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk

		samples = SampleAnalysis.objects.filter(sample_id="21M00305-control", panel=panel_pk)

		for sample in samples:

			sample_data=get_sample_info(sample)

			variant_data=get_variant_info(sample_data, sample)
			variant_calls=variant_data.get('variant_calls')
			variant_0=variant_calls[0]
			variant_6=variant_calls[6]
			variant_12=variant_calls[12]
			variant_19=variant_calls[19]

			self.assertEqual(variant_0.get('genomic'), '2:209113192G>A')
			self.assertEqual(variant_0.get('gene'), 'IDH1')
			self.assertEqual(variant_0.get('exon'), '4/10')
			self.assertEqual(variant_0.get('hgvs_c'), 'NM_005896.3:c.315C>T')
			self.assertEqual(variant_0.get('hgvs_p'), 'NM_005896.3:c.315C>T(p.(Gly105=))')
			self.assertEqual((variant_0.get('vaf').get('vaf')), 16)
			self.assertEqual((variant_0.get('vaf').get('total_count')), 1380)
			self.assertEqual((variant_0.get('vaf').get('alt_count')), 221)
			self.assertEqual(variant_0.get('checks'), ['Pending'])

			self.assertEqual(variant_6.get('genomic'), '9:21970916C>T')
			self.assertEqual(variant_6.get('gene'), 'CDKN2A')
			self.assertEqual(variant_6.get('exon'), '2/3')
			self.assertEqual(variant_6.get('hgvs_c'), 'NM_000077.4:c.442G>A')
			self.assertEqual(variant_6.get('hgvs_p'), 'NP_000068.1:p.(Ala148Thr)')
			self.assertEqual((variant_6.get('vaf').get('vaf')), 6)
			self.assertEqual((variant_6.get('vaf').get('total_count')), 683)
			self.assertEqual((variant_6.get('vaf').get('alt_count')), 43)
			self.assertEqual(variant_6.get('checks'), ['Pending'])

			self.assertEqual(variant_12.get('genomic'), '17:7578419C>A')
			self.assertEqual(variant_12.get('gene'), 'TP53')
			self.assertEqual(variant_12.get('exon'), '5/11')
			self.assertEqual(variant_12.get('hgvs_c'), 'NM_000546.5:c.511G>T')
			self.assertEqual(variant_12.get('hgvs_p'), 'NP_000537.3:p.(Glu171Ter)')
			self.assertEqual((variant_12.get('vaf').get('vaf')), 16)
			self.assertEqual((variant_12.get('vaf').get('total_count')), 1450)
			self.assertEqual((variant_12.get('vaf').get('alt_count')), 232)
			self.assertEqual(variant_12.get('checks'), ['Pending'])

			self.assertEqual(variant_19.get('genomic'), 'X:76938208A>G')
			self.assertEqual(variant_19.get('gene'), 'ATRX')
			self.assertEqual(variant_19.get('exon'), '9/35')
			self.assertEqual(variant_19.get('hgvs_c'), 'NM_000489.4:c.2540T>C')
			self.assertEqual(variant_19.get('hgvs_p'), 'NP_000480.3:p.(Phe847Ser)')
			self.assertEqual((variant_19.get('vaf').get('vaf')), 5)
			self.assertEqual((variant_19.get('vaf').get('total_count')), 571)
			self.assertEqual((variant_19.get('vaf').get('alt_count')), 32)
			self.assertEqual(variant_19.get('checks'), ['Pending'])


		#Lung

		panel_obj = Panel.objects.filter(panel_name="Lung", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk

		samples = SampleAnalysis.objects.filter(sample_id="21M00305-control", panel=panel_pk)

		for sample in samples:

			sample_data=get_sample_info(sample)

			variant_data=get_variant_info(sample_data, sample)
			variant_calls=variant_data.get('variant_calls')
			variant_0=variant_calls[0]
			variant_1=variant_calls[1]
			variant_2=variant_calls[2]
			variant_3=variant_calls[3]
			variant_4=variant_calls[4]
			variant_5=variant_calls[5]


			self.assertEqual(variant_0.get('genomic'), '7:55241707G>A')
			self.assertEqual(variant_0.get('gene'), 'EGFR')
			self.assertEqual(variant_0.get('exon'), '18/28')
			self.assertEqual(variant_0.get('hgvs_c'), 'NM_005228.4:c.2155G>A')
			self.assertEqual(variant_0.get('hgvs_p'), 'NP_005219.2:p.(Gly719Ser)')
			self.assertEqual((variant_0.get('vaf').get('vaf')), 4)
			self.assertEqual((variant_0.get('vaf').get('total_count')), 1608)
			self.assertEqual((variant_0.get('vaf').get('alt_count')), 77)
			self.assertEqual(variant_0.get('checks'), ['Pending'])

			self.assertEqual(variant_1.get('genomic'), '7:55242464AGGAATTAAGAGAAGC>A')
			self.assertEqual(variant_1.get('gene'), 'EGFR')
			self.assertEqual(variant_1.get('exon'), '19/28')
			self.assertEqual(variant_1.get('hgvs_c'), 'NM_005228.4:c.2235_2249del')
			self.assertEqual(variant_1.get('hgvs_p'), 'NP_005219.2:p.(Glu746_Ala750del)')
			self.assertEqual((variant_1.get('vaf').get('vaf')), 5)
			self.assertEqual((variant_1.get('vaf').get('total_count')), 1729)
			self.assertEqual((variant_1.get('vaf').get('alt_count')), 96)
			self.assertEqual(variant_1.get('checks'), ['Pending'])

			self.assertEqual(variant_4.get('genomic'), '7:140453136A>T')
			self.assertEqual(variant_4.get('gene'), 'BRAF')
			self.assertEqual(variant_4.get('exon'), '15/18')
			self.assertEqual(variant_4.get('hgvs_c'), 'NM_004333.4:c.1799T>A')
			self.assertEqual(variant_4.get('hgvs_p'), 'NP_004324.2:p.(Val600Glu)')
			self.assertEqual((variant_4.get('vaf').get('vaf')), 15)
			self.assertEqual((variant_4.get('vaf').get('total_count')), 1434)
			self.assertEqual((variant_4.get('vaf').get('alt_count')), 226)
			self.assertEqual(variant_4.get('checks'), ['Pending'])

			self.assertEqual(variant_5.get('genomic'), '12:25398281C>T')
			self.assertEqual(variant_5.get('gene'), 'KRAS')
			self.assertEqual(variant_5.get('exon'), '2/6')
			self.assertEqual(variant_5.get('hgvs_c'), 'NM_033360.3:c.38G>A')
			self.assertEqual(variant_5.get('hgvs_p'), 'NP_203524.1:p.(Gly13Asp)')
			self.assertEqual((variant_5.get('vaf').get('vaf')), 5)
			self.assertEqual((variant_5.get('vaf').get('total_count')), 1205)
			self.assertEqual((variant_5.get('vaf').get('alt_count')), 67)
			self.assertEqual(variant_5.get('checks'), ['Pending'])


		#Melanoma
		panel_obj = Panel.objects.filter(panel_name="Melanoma", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk

		samples = SampleAnalysis.objects.filter(sample_id="21M00305-control", panel=panel_pk)

		for sample in samples:

			sample_data=get_sample_info(sample)

			variant_data=get_variant_info(sample_data, sample)
			variant_calls=variant_data.get('variant_calls')
			variant_0=variant_calls[0]
			variant_1=variant_calls[1]


			self.assertEqual(variant_0.get('genomic'), '4:55599268C>T')
			self.assertEqual(variant_0.get('gene'), 'KIT')
			self.assertEqual(variant_0.get('exon'), '17/21')
			self.assertEqual(variant_0.get('hgvs_c'), 'NM_000222.2:c.2394C>T')
			self.assertEqual(variant_0.get('hgvs_p'), 'NM_000222.2:c.2394C>T(p.(Ile798=))')
			self.assertEqual((variant_0.get('vaf').get('vaf')), 3)
			self.assertEqual((variant_0.get('vaf').get('total_count')), 1260)
			self.assertEqual((variant_0.get('vaf').get('alt_count')), 44)
			self.assertEqual(variant_0.get('checks'), ['Pending'])

			self.assertEqual(variant_1.get('genomic'), '7:140453136A>T')
			self.assertEqual(variant_1.get('gene'), 'BRAF')
			self.assertEqual(variant_1.get('exon'), '15/18')
			self.assertEqual(variant_1.get('hgvs_c'), 'NM_004333.4:c.1799T>A')
			self.assertEqual(variant_1.get('hgvs_p'), 'NP_004324.2:p.(Val600Glu)')
			self.assertEqual((variant_1.get('vaf').get('vaf')), 15)
			self.assertEqual((variant_1.get('vaf').get('total_count')), 1434)
			self.assertEqual((variant_1.get('vaf').get('alt_count')), 226)
			self.assertEqual(variant_1.get('checks'), ['Pending'])


		#Colorectal
		panel_obj = Panel.objects.filter(panel_name="Colorectal", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk

		samples = SampleAnalysis.objects.filter(sample_id="21M00305-control", panel=panel_pk)

		for sample in samples:

			sample_data=get_sample_info(sample)

			variant_data=get_variant_info(sample_data, sample)
			variant_calls=variant_data.get('variant_calls')
			variant_0=variant_calls[0]
			variant_8=variant_calls[8]
			variant_11=variant_calls[11]


			self.assertEqual(variant_0.get('genomic'), '3:178936091G>A')
			self.assertEqual(variant_0.get('gene'), 'PIK3CA')
			self.assertEqual(variant_0.get('exon'), '10/21')
			self.assertEqual(variant_0.get('hgvs_c'), 'NM_006218.3:c.1633G>A')
			self.assertEqual(variant_0.get('hgvs_p'), 'NP_006209.2:p.(Glu545Lys)')
			self.assertEqual((variant_0.get('vaf').get('vaf')), 5)
			self.assertEqual((variant_0.get('vaf').get('total_count')), 1206)
			self.assertEqual((variant_0.get('vaf').get('alt_count')), 61)
			self.assertEqual(variant_0.get('checks'), ['Pending'])

			self.assertEqual(variant_8.get('genomic'), '17:7577559G>A')
			self.assertEqual(variant_8.get('gene'), 'TP53')
			self.assertEqual(variant_8.get('exon'), '7/11')
			self.assertEqual(variant_8.get('hgvs_c'), 'NM_000546.5:c.722C>T')
			self.assertEqual(variant_8.get('hgvs_p'), 'NP_000537.3:p.(Ser241Phe)')
			self.assertEqual((variant_8.get('vaf').get('vaf')), 8)
			self.assertEqual((variant_8.get('vaf').get('total_count')), 1082)
			self.assertEqual((variant_8.get('vaf').get('alt_count')), 95)
			self.assertEqual(variant_8.get('checks'), ['Pending'])

			self.assertEqual(variant_11.get('genomic'), '17:7579472G>C')
			self.assertEqual(variant_11.get('gene'), 'TP53')
			self.assertEqual(variant_11.get('exon'), '4/11')
			self.assertEqual(variant_11.get('hgvs_c'), 'NM_000546.5:c.215C>G')
			self.assertEqual(variant_11.get('hgvs_p'), 'NP_000537.3:p.(Pro72Arg)')
			self.assertEqual((variant_11.get('vaf').get('vaf')), 82)
			self.assertEqual((variant_11.get('vaf').get('total_count')), 1460)
			self.assertEqual((variant_11.get('vaf').get('alt_count')), 1198)
			self.assertEqual(variant_11.get('checks'), ['Pending'])



		#Thyroid
		panel_obj = Panel.objects.filter(panel_name="Thyroid", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk

		samples = SampleAnalysis.objects.filter(sample_id="21M00305-control", panel=panel_pk)

		for sample in samples:

			sample_data=get_sample_info(sample)

			variant_data=get_variant_info(sample_data, sample)
			variant_calls=variant_data.get('variant_calls')
			variant_0=variant_calls[0]
			variant_8=variant_calls[4]
			variant_13=variant_calls[13]


			self.assertEqual(variant_0.get('genomic'), '10:43595968A>G')
			self.assertEqual(variant_0.get('gene'), 'RET')
			self.assertEqual(variant_0.get('exon'), '2/20')
			self.assertEqual(variant_0.get('hgvs_c'), 'NM_020975.4:c.135=')
			self.assertEqual(variant_0.get('hgvs_p'), 'NM_020975.4:c.135=(p.(Ala45=))')
			self.assertEqual((variant_0.get('vaf').get('vaf')), 75)
			self.assertEqual((variant_0.get('vaf').get('total_count')), 1573)
			self.assertEqual((variant_0.get('vaf').get('alt_count')), 1187)
			self.assertEqual(variant_0.get('checks'), ['Pending'])


			self.assertEqual(variant_4.get('genomic'), '7:140453136A>T')
			self.assertEqual(variant_4.get('gene'), 'BRAF')
			self.assertEqual(variant_4.get('exon'), '15/18')
			self.assertEqual(variant_4.get('hgvs_c'), 'NM_004333.4:c.1799T>A')
			self.assertEqual(variant_4.get('hgvs_p'), 'NP_004324.2:p.(Val600Glu)')
			self.assertEqual((variant_4.get('vaf').get('vaf')), 15)
			self.assertEqual((variant_4.get('vaf').get('total_count')), 1434)
			self.assertEqual((variant_4.get('vaf').get('alt_count')), 226)
			self.assertEqual(variant_4.get('checks'), ['Pending'])

			self.assertEqual(variant_13.get('genomic'), '17:7579472G>C')
			self.assertEqual(variant_13.get('gene'), 'TP53')
			self.assertEqual(variant_13.get('exon'), '4/11')
			self.assertEqual(variant_13.get('hgvs_c'), 'NM_000546.5:c.215C>G')
			self.assertEqual(variant_13.get('hgvs_p'), 'NP_000537.3:p.(Pro72Arg)')
			self.assertEqual((variant_13.get('vaf').get('vaf')), 82)
			self.assertEqual((variant_13.get('vaf').get('total_count')), 1460)
			self.assertEqual((variant_13.get('vaf').get('alt_count')), 1198)
			self.assertEqual(variant_13.get('checks'), ['Pending'])


	def test_get_fusion_info(self):

		#Tumour
		panel_obj = Panel.objects.filter(panel_name="Tumour", dna_or_rna="RNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)
		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")


		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_1=fusion_calls[1]
		self.assertEqual(fusion_1.get('fusion_genes'), 'LMNA-NTRK1')
		self.assertEqual(fusion_1.get('left_breakpoint'), 'chr1:156100562')
		self.assertEqual(fusion_1.get('right_breakpoint'), 'chr1:156844696')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'SLC45A3-BRAF')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr1:205649521')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr7:140494266')

		fusion_3=fusion_calls[3]
		self.assertEqual(fusion_3.get('fusion_genes'), 'EML4-ALK')
		self.assertEqual(fusion_3.get('left_breakpoint'), 'chr2:42522654')
		self.assertEqual(fusion_3.get('right_breakpoint'), 'chr2:29446394')

		fusion_4=fusion_calls[4]
		self.assertEqual(fusion_4.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_4.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_4.get('right_breakpoint'), 'chr1:156844360')

		fusion_5=fusion_calls[5]
		self.assertEqual(fusion_5.get('fusion_genes'), 'SLC34A2-ROS1;GOPC')
		self.assertEqual(fusion_5.get('left_breakpoint'), 'chr4:25665950')
		self.assertEqual(fusion_5.get('right_breakpoint'), 'chr6:117645578')


		fusion_6=fusion_calls[6]
		self.assertEqual(fusion_6.get('fusion_genes'), 'CD74-ROS1;GOPC')
		self.assertEqual(fusion_6.get('left_breakpoint'), 'chr5:149784243')
		self.assertEqual(fusion_6.get('right_breakpoint'), 'chr6:117645578')

		fusion_7=fusion_calls[7]
		self.assertEqual(fusion_7.get('fusion_genes'), 'KIF5B-RET')
		self.assertEqual(fusion_7.get('left_breakpoint'), 'chr10:32306071')
		self.assertEqual(fusion_7.get('right_breakpoint'), 'chr10:43609927')

		fusion_8=fusion_calls[8]
		self.assertEqual(fusion_8.get('fusion_genes'), 'NCOA4-RET')
		self.assertEqual(fusion_8.get('left_breakpoint'), 'chr10:51582937')
		self.assertEqual(fusion_8.get('right_breakpoint'), 'chr10:43612030')

		fusion_9=fusion_calls[9]
		self.assertEqual(fusion_9.get('fusion_genes'), 'CCDC6-RET')
		self.assertEqual(fusion_9.get('left_breakpoint'), 'chr10:61665879')
		self.assertEqual(fusion_9.get('right_breakpoint'), 'chr10:43612032')

		fusion_10=fusion_calls[10]
		self.assertEqual(fusion_10.get('fusion_genes'), 'ETV6-NTRK3')
		self.assertEqual(fusion_10.get('left_breakpoint'), 'chr12:12022900')
		self.assertEqual(fusion_10.get('right_breakpoint'), 'chr15:88483984')

		fusion_11=fusion_calls[11]
		self.assertEqual(fusion_11.get('fusion_genes'), 'EGFR 2-7/28')
		self.assertEqual(fusion_11.get('left_breakpoint'), 'chr7:55087058')
		self.assertEqual(fusion_11.get('right_breakpoint'), 'chr7:55223522')


		fusion_12=fusion_calls[12]
		self.assertEqual(fusion_12.get('fusion_genes'), 'MET 14/21')
		self.assertEqual(fusion_12.get('left_breakpoint'), 'chr7:116411708')
		self.assertEqual(fusion_12.get('right_breakpoint'), 'chr7:116414934')




		#Glioma
		panel_obj = Panel.objects.filter(panel_name="Glioma", dna_or_rna="RNA")
		glioma_panel=panel_obj[0]
		panel_pk=glioma_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)

		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")

		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'SLC45A3-BRAF')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr1:205649521')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr7:140494266')

		fusion_3=fusion_calls[3]
		self.assertEqual(fusion_3.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_3.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_3.get('right_breakpoint'), 'chr1:156844360')

		fusion_4=fusion_calls[4]
		self.assertEqual(fusion_4.get('fusion_genes'), 'ETV6-NTRK3')
		self.assertEqual(fusion_4.get('left_breakpoint'), 'chr12:12022900')
		self.assertEqual(fusion_4.get('right_breakpoint'), 'chr15:88483984')

		fusion_5=fusion_calls[5]
		self.assertEqual(fusion_5.get('fusion_genes'), 'EGFR 2-7/28')
		self.assertEqual(fusion_5.get('left_breakpoint'), 'chr7:55087058')
		self.assertEqual(fusion_5.get('right_breakpoint'), 'chr7:55223522')


		#Melanoma

		panel_obj = Panel.objects.filter(panel_name="Melanoma", dna_or_rna="RNA")
		melanoma_panel=panel_obj[0]
		panel_pk=melanoma_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)

		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")

		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_1=fusion_calls[1]
		self.assertEqual(fusion_1.get('fusion_genes'), 'LMNA-NTRK1')
		self.assertEqual(fusion_1.get('left_breakpoint'), 'chr1:156100562')
		self.assertEqual(fusion_1.get('right_breakpoint'), 'chr1:156844696')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr1:156844360')

		fusion_3=fusion_calls[3]
		self.assertEqual(fusion_3.get('fusion_genes'), 'ETV6-NTRK3')
		self.assertEqual(fusion_3.get('left_breakpoint'), 'chr12:12022900')
		self.assertEqual(fusion_3.get('right_breakpoint'), 'chr15:88483984')


		# NTRK
		panel_obj = Panel.objects.filter(panel_name="NTRK", dna_or_rna="RNA")
		NTRK_panel=panel_obj[0]
		panel_pk=NTRK_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)

		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")


		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_1=fusion_calls[1]
		self.assertEqual(fusion_1.get('fusion_genes'), 'LMNA-NTRK1')
		self.assertEqual(fusion_1.get('left_breakpoint'), 'chr1:156100562')
		self.assertEqual(fusion_1.get('right_breakpoint'), 'chr1:156844696')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr1:156844360')


		fusion_3=fusion_calls[3]
		self.assertEqual(fusion_3.get('fusion_genes'), 'ETV6-NTRK3')
		self.assertEqual(fusion_3.get('left_breakpoint'), 'chr12:12022900')
		self.assertEqual(fusion_3.get('right_breakpoint'), 'chr15:88483984')



		# GIST
		panel_obj = Panel.objects.filter(panel_name="GIST", dna_or_rna="RNA")
		GIST_panel=panel_obj[0]
		panel_pk=GIST_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)

		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")


		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_1=fusion_calls[1]
		self.assertEqual(fusion_1.get('fusion_genes'), 'LMNA-NTRK1')
		self.assertEqual(fusion_1.get('left_breakpoint'), 'chr1:156100562')
		self.assertEqual(fusion_1.get('right_breakpoint'), 'chr1:156844696')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr1:156844360')


		fusion_3=fusion_calls[3]
		self.assertEqual(fusion_3.get('fusion_genes'), 'ETV6-NTRK3')
		self.assertEqual(fusion_3.get('left_breakpoint'), 'chr12:12022900')
		self.assertEqual(fusion_3.get('right_breakpoint'), 'chr15:88483984')



		# Thyroid
		panel_obj = Panel.objects.filter(panel_name="Thyroid", dna_or_rna="RNA")
		GIST_panel=panel_obj[0]
		panel_pk=GIST_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)

		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")


		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_1=fusion_calls[1]
		self.assertEqual(fusion_1.get('fusion_genes'), 'LMNA-NTRK1')
		self.assertEqual(fusion_1.get('left_breakpoint'), 'chr1:156100562')
		self.assertEqual(fusion_1.get('right_breakpoint'), 'chr1:156844696')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr1:156844360')


		fusion_3=fusion_calls[3]
		self.assertEqual(fusion_3.get('fusion_genes'), 'KIF5B-RET')
		self.assertEqual(fusion_3.get('left_breakpoint'), 'chr10:32306071')
		self.assertEqual(fusion_3.get('right_breakpoint'), 'chr10:43609927')

		fusion_4=fusion_calls[4]
		self.assertEqual(fusion_4.get('fusion_genes'), 'NCOA4-RET')
		self.assertEqual(fusion_4.get('left_breakpoint'), 'chr10:51582937')
		self.assertEqual(fusion_4.get('right_breakpoint'), 'chr10:43612030')

		fusion_5=fusion_calls[5]
		self.assertEqual(fusion_5.get('fusion_genes'), 'CCDC6-RET')
		self.assertEqual(fusion_5.get('left_breakpoint'), 'chr10:61665879')
		self.assertEqual(fusion_5.get('right_breakpoint'), 'chr10:43612032')

		fusion_6=fusion_calls[6]
		self.assertEqual(fusion_6.get('fusion_genes'), 'ETV6-NTRK3')
		self.assertEqual(fusion_6.get('left_breakpoint'), 'chr12:12022900')
		self.assertEqual(fusion_6.get('right_breakpoint'), 'chr15:88483984')

		fusion_7=fusion_calls[7]
		self.assertEqual(fusion_7.get('fusion_genes'), 'EGFR 2-7/28')
		self.assertEqual(fusion_7.get('left_breakpoint'), 'chr7:55087058')
		self.assertEqual(fusion_7.get('right_breakpoint'), 'chr7:55223522')


		# Lung
		panel_obj = Panel.objects.filter(panel_name="Lung", dna_or_rna="RNA")
		Lung_panel=panel_obj[0]
		panel_pk=Lung_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)

		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")


		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_1=fusion_calls[1]
		self.assertEqual(fusion_1.get('fusion_genes'), 'LMNA-NTRK1')
		self.assertEqual(fusion_1.get('left_breakpoint'), 'chr1:156100562')
		self.assertEqual(fusion_1.get('right_breakpoint'), 'chr1:156844696')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'EML4-ALK')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr2:42522654')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr2:29446394')


		fusion_3=fusion_calls[3]
		self.assertEqual(fusion_3.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_3.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_3.get('right_breakpoint'), 'chr1:156844360')


		fusion_4=fusion_calls[4]
		self.assertEqual(fusion_4.get('fusion_genes'), 'SLC34A2-ROS1;GOPC')
		self.assertEqual(fusion_4.get('left_breakpoint'), 'chr4:25665950')
		self.assertEqual(fusion_4.get('right_breakpoint'), 'chr6:117645578')


		fusion_5=fusion_calls[5]
		self.assertEqual(fusion_5.get('fusion_genes'), 'CD74-ROS1;GOPC')
		self.assertEqual(fusion_5.get('left_breakpoint'), 'chr5:149784243')
		self.assertEqual(fusion_5.get('right_breakpoint'), 'chr6:117645578')

		fusion_6=fusion_calls[6]
		self.assertEqual(fusion_6.get('fusion_genes'), 'KIF5B-RET')
		self.assertEqual(fusion_6.get('left_breakpoint'), 'chr10:32306071')
		self.assertEqual(fusion_6.get('right_breakpoint'), 'chr10:43609927')

		fusion_7=fusion_calls[7]
		self.assertEqual(fusion_7.get('fusion_genes'), 'NCOA4-RET')
		self.assertEqual(fusion_7.get('left_breakpoint'), 'chr10:51582937')
		self.assertEqual(fusion_7.get('right_breakpoint'), 'chr10:43612030')

		fusion_8=fusion_calls[8]
		self.assertEqual(fusion_8.get('fusion_genes'), 'CCDC6-RET')
		self.assertEqual(fusion_8.get('left_breakpoint'), 'chr10:61665879')
		self.assertEqual(fusion_8.get('right_breakpoint'), 'chr10:43612032')

		fusion_9=fusion_calls[9]
		self.assertEqual(fusion_9.get('fusion_genes'), 'ETV6-NTRK3')
		self.assertEqual(fusion_9.get('left_breakpoint'), 'chr12:12022900')
		self.assertEqual(fusion_9.get('right_breakpoint'), 'chr15:88483984')

		fusion_10=fusion_calls[10]
		self.assertEqual(fusion_10.get('fusion_genes'), 'EGFR 2-7/28')
		self.assertEqual(fusion_10.get('left_breakpoint'), 'chr7:55087058')
		self.assertEqual(fusion_10.get('right_breakpoint'), 'chr7:55223522')

		fusion_11=fusion_calls[11]
		self.assertEqual(fusion_11.get('fusion_genes'), 'MET 14/21')
		self.assertEqual(fusion_11.get('left_breakpoint'), 'chr7:116411708')
		self.assertEqual(fusion_11.get('right_breakpoint'), 'chr7:116414934')



		# Colorectal
		panel_obj = Panel.objects.filter(panel_name="Colorectal", dna_or_rna="RNA")
		Lung_panel=panel_obj[0]
		panel_pk=Lung_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M81042-control",panel=panel_pk)
		sample=sample_obj[0]
		sample_data=get_sample_info(sample)

		fusion_data=get_fusion_info(sample_data, sample)
		fusion_calls=fusion_data.get("fusion_calls")


		fusion_0=fusion_calls[0]
		self.assertEqual(fusion_0.get('fusion_genes'), 'TPM3-NTRK1')
		self.assertEqual(fusion_0.get('left_breakpoint'), 'chr1:154142876')
		self.assertEqual(fusion_0.get('right_breakpoint'), 'chr1:156844361')

		fusion_1=fusion_calls[1]
		self.assertEqual(fusion_1.get('fusion_genes'), 'LMNA-NTRK1')
		self.assertEqual(fusion_1.get('left_breakpoint'), 'chr1:156100562')
		self.assertEqual(fusion_1.get('right_breakpoint'), 'chr1:156844696')

		fusion_2=fusion_calls[2]
		self.assertEqual(fusion_2.get('fusion_genes'), 'TFG-NTRK1')
		self.assertEqual(fusion_2.get('left_breakpoint'), 'chr3:100451513')
		self.assertEqual(fusion_2.get('right_breakpoint'), 'chr1:156844360')






	def test_get_coverage_data(self):


		#Glioma
		panel_obj = Panel.objects.filter(panel_name="Glioma", dna_or_rna="DNA")
		glioma_panel=panel_obj[0]
		panel_pk=glioma_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M00305-control",panel=panel_pk)
		sample=sample_obj[0]
		coverage_data= get_coverage_data(sample)

		H3F3A_coverage=coverage_data.get('H3F3A')
		IDH1_coverage=coverage_data.get('IDH1')
		TERT_coverage=coverage_data.get('TERT')
		EGFR_coverage=coverage_data.get('EGFR')
		BRAF_coverage=coverage_data.get('BRAF')
		IDH2_coverage=coverage_data.get('IDH2')
		CDKN2A_coverage=coverage_data.get('CDKN2A')
		PTEN_coverage=coverage_data.get('PTEN')
		TP53_coverage=coverage_data.get('TP53')
		ATRX_coverage=coverage_data.get('ATRX')

		self.assertEqual(H3F3A_coverage.get('av_coverage'), 886)
		self.assertEqual(H3F3A_coverage.get('percent_270x'), 100)
		self.assertEqual(H3F3A_coverage.get('percent_135x'), 100)
		self.assertEqual(H3F3A_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(H3F3A_coverage.get('percent_ntc'), 0)

		self.assertEqual(IDH1_coverage.get('av_coverage'), 1054)
		self.assertEqual(IDH1_coverage.get('percent_270x'), 100)
		self.assertEqual(IDH1_coverage.get('percent_135x'), 100)
		self.assertEqual(IDH1_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(IDH1_coverage.get('percent_ntc'), 0)

		self.assertEqual(TERT_coverage.get('av_coverage'), 240)
		self.assertEqual(TERT_coverage.get('percent_270x'), 50)
		self.assertEqual(TERT_coverage.get('percent_135x'), 100)
		self.assertEqual(TERT_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(TERT_coverage.get('percent_ntc'), 0)

		self.assertEqual(BRAF_coverage.get('av_coverage'), 1250)
		self.assertEqual(BRAF_coverage.get('percent_270x'), 100)
		self.assertEqual(BRAF_coverage.get('percent_135x'), 100)
		self.assertEqual(BRAF_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(BRAF_coverage.get('percent_ntc'), 0)

		self.assertEqual(IDH2_coverage.get('av_coverage'), 1306)
		self.assertEqual(IDH2_coverage.get('percent_270x'), 100)
		self.assertEqual(IDH2_coverage.get('percent_135x'), 100)
		self.assertEqual(IDH2_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(IDH2_coverage.get('percent_ntc'), 0)

		self.assertEqual(CDKN2A_coverage.get('av_coverage'), 644)
		self.assertEqual(CDKN2A_coverage.get('percent_270x'), 95)
		self.assertEqual(CDKN2A_coverage.get('percent_135x'), 100)
		self.assertEqual(CDKN2A_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(CDKN2A_coverage.get('percent_ntc'), 0)

		self.assertEqual(PTEN_coverage.get('av_coverage'), 936)
		self.assertEqual(PTEN_coverage.get('percent_270x'), 100)
		self.assertEqual(PTEN_coverage.get('percent_135x'), 100)
		self.assertEqual(PTEN_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(PTEN_coverage.get('percent_ntc'), 0)

		self.assertEqual(TP53_coverage.get('av_coverage'), 1244)
		self.assertEqual(TP53_coverage.get('percent_270x'), 100)
		self.assertEqual(TP53_coverage.get('percent_135x'), 100)
		self.assertEqual(TP53_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(TP53_coverage.get('percent_ntc'), 0)

		self.assertEqual(ATRX_coverage.get('av_coverage'), 692)
		self.assertEqual(ATRX_coverage.get('percent_270x'), 100)
		self.assertEqual(ATRX_coverage.get('percent_135x'), 100)
		self.assertEqual(ATRX_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(ATRX_coverage.get('percent_ntc'), 0)



		#Melanoma
		panel_obj = Panel.objects.filter(panel_name="Melanoma", dna_or_rna="DNA")
		melanoma_panel=panel_obj[0]
		panel_pk=melanoma_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M00305-control",panel=panel_pk)
		sample=sample_obj[0]
		coverage_data= get_coverage_data(sample)

		NRAS_coverage=coverage_data.get('NRAS')
		KIT_coverage=coverage_data.get('KIT')
		BRAF_coverage=coverage_data.get('BRAF')

		self.assertEqual(NRAS_coverage.get('av_coverage'), 1380)
		self.assertEqual(NRAS_coverage.get('percent_270x'), 100)
		self.assertEqual(NRAS_coverage.get('percent_135x'), 100)
		self.assertEqual(NRAS_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(NRAS_coverage.get('percent_ntc'), 0)

		self.assertEqual(KIT_coverage.get('av_coverage'), 1301)
		self.assertEqual(KIT_coverage.get('percent_270x'), 100)
		self.assertEqual(KIT_coverage.get('percent_135x'), 100)
		self.assertEqual(KIT_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(KIT_coverage.get('percent_ntc'), 0)

		self.assertEqual(ATRX_coverage.get('av_coverage'), 692)
		self.assertEqual(ATRX_coverage.get('percent_270x'), 100)
		self.assertEqual(ATRX_coverage.get('percent_135x'), 100)
		self.assertEqual(ATRX_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(ATRX_coverage.get('percent_ntc'), 0)



		#Tumour
		panel_obj = Panel.objects.filter(panel_name="Tumour", dna_or_rna="DNA")
		tumour_panel=panel_obj[0]
		panel_pk=tumour_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M00305-control",panel=panel_pk)
		sample=sample_obj[0]
		coverage_data= get_coverage_data(sample)
 
		AR_coverage=coverage_data.get('AR')
		KIT_coverage=coverage_data.get('ATRX')
		ATRX_coverage=coverage_data.get('ARID1A')
		ARID1A_coverage=coverage_data.get('NRAS')
		NRAS_coverage=coverage_data.get('H3F3A')
		BRCA2_coverage=coverage_data.get('BRCA2')
		IDH2_coverage=coverage_data.get('IDH2')
		TP53_coverage=coverage_data.get('TP53')
		ERBB2_coverage=coverage_data.get('ERBB2')
		PIK3CA_coverage=coverage_data.get('PIK3CA')

		self.assertEqual(AR_coverage.get('av_coverage'), 1044)
		self.assertEqual(AR_coverage.get('percent_270x'), 98)
		self.assertEqual(AR_coverage.get('percent_135x'), 99)
		self.assertEqual(AR_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(AR_coverage.get('percent_ntc'), 0)

		self.assertEqual(KIT_coverage.get('av_coverage'), 692)
		self.assertEqual(KIT_coverage.get('percent_270x'), 100)
		self.assertEqual(KIT_coverage.get('percent_135x'), 100)
		self.assertEqual(KIT_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(KIT_coverage.get('percent_ntc'), 0)

		self.assertEqual(ATRX_coverage.get('av_coverage'), 1222)
		self.assertEqual(ATRX_coverage.get('percent_270x'), 90)
		self.assertEqual(ATRX_coverage.get('percent_135x'), 96)
		self.assertEqual(ATRX_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(ATRX_coverage.get('percent_ntc'), 0)

		self.assertEqual(ARID1A_coverage.get('av_coverage'), 1380)
		self.assertEqual(ARID1A_coverage.get('percent_270x'), 100)
		self.assertEqual(ARID1A_coverage.get('percent_135x'), 100)
		self.assertEqual(ARID1A_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(ARID1A_coverage.get('percent_ntc'), 0)

		self.assertEqual(NRAS_coverage.get('av_coverage'), 886)
		self.assertEqual(NRAS_coverage.get('percent_270x'), 100)
		self.assertEqual(NRAS_coverage.get('percent_135x'), 100)
		self.assertEqual(NRAS_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(NRAS_coverage.get('percent_ntc'), 0)

		self.assertEqual(BRCA2_coverage.get('av_coverage'), 1018)
		self.assertEqual(BRCA2_coverage.get('percent_270x'), 100)
		self.assertEqual(BRCA2_coverage.get('percent_135x'), 100)
		self.assertEqual(BRCA2_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(BRCA2_coverage.get('percent_ntc'), 0)

		self.assertEqual(IDH2_coverage.get('av_coverage'), 1306)
		self.assertEqual(IDH2_coverage.get('percent_270x'), 100)
		self.assertEqual(IDH2_coverage.get('percent_135x'), 100)
		self.assertEqual(IDH2_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(IDH2_coverage.get('percent_ntc'), 0)

		self.assertEqual(TP53_coverage.get('av_coverage'), 1244)
		self.assertEqual(TP53_coverage.get('percent_270x'), 100)
		self.assertEqual(TP53_coverage.get('percent_135x'), 100)
		self.assertEqual(TP53_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(TP53_coverage.get('percent_ntc'), 0)


		self.assertEqual(ERBB2_coverage.get('av_coverage'), 1620)
		self.assertEqual(ERBB2_coverage.get('percent_270x'), 100)
		self.assertEqual(ERBB2_coverage.get('percent_135x'), 100)
		self.assertEqual(ERBB2_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(ERBB2_coverage.get('percent_ntc'), 0)

		self.assertEqual(PIK3CA_coverage.get('av_coverage'), 1258)
		self.assertEqual(PIK3CA_coverage.get('percent_270x'), 100)
		self.assertEqual(PIK3CA_coverage.get('percent_135x'), 100)
		self.assertEqual(PIK3CA_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(PIK3CA_coverage.get('percent_ntc'), 0)


		#Colorectal
		panel_obj = Panel.objects.filter(panel_name="Colorectal", dna_or_rna="DNA")
		colorectal_panel=panel_obj[0]
		panel_pk=colorectal_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M00305-control",panel=panel_pk)
		sample=sample_obj[0]
		coverage_data= get_coverage_data(sample)

		NRAS_coverage=coverage_data.get('NRAS')
		PIK3CA_coverage=coverage_data.get('PIK3CA')
		EGFR_coverage=coverage_data.get('EGFR')
		BRAF_coverage=coverage_data.get('BRAF')
		KRAS_coverage=coverage_data.get('KRAS')
		PTEN_coverage=coverage_data.get('PTEN')
		TP53_coverage=coverage_data.get('TP53')

		self.assertEqual(NRAS_coverage.get('av_coverage'), 1380)
		self.assertEqual(NRAS_coverage.get('percent_270x'), 100)
		self.assertEqual(NRAS_coverage.get('percent_135x'), 100)
		self.assertEqual(NRAS_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(NRAS_coverage.get('percent_ntc'), 0)

		self.assertEqual(PIK3CA_coverage.get('av_coverage'), 1258)
		self.assertEqual(PIK3CA_coverage.get('percent_270x'), 100)
		self.assertEqual(PIK3CA_coverage.get('percent_135x'), 100)
		self.assertEqual(PIK3CA_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(PIK3CA_coverage.get('percent_ntc'), 0)

		self.assertEqual(EGFR_coverage.get('av_coverage'), 1727)
		self.assertEqual(EGFR_coverage.get('percent_270x'), 100)
		self.assertEqual(EGFR_coverage.get('percent_135x'), 100)
		self.assertEqual(EGFR_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(EGFR_coverage.get('percent_ntc'), 0)


		self.assertEqual(BRAF_coverage.get('av_coverage'), 1335)
		self.assertEqual(BRAF_coverage.get('percent_270x'), 100)
		self.assertEqual(BRAF_coverage.get('percent_135x'), 100)
		self.assertEqual(BRAF_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(BRAF_coverage.get('percent_ntc'), 0)


		self.assertEqual(KRAS_coverage.get('av_coverage'), 1288)
		self.assertEqual(KRAS_coverage.get('percent_270x'), 100)
		self.assertEqual(KRAS_coverage.get('percent_135x'), 100)
		self.assertEqual(KRAS_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(KRAS_coverage.get('percent_ntc'), 0)

		self.assertEqual(PTEN_coverage.get('av_coverage'), 936)
		self.assertEqual(PTEN_coverage.get('percent_270x'), 100)
		self.assertEqual(PTEN_coverage.get('percent_135x'), 100)
		self.assertEqual(PTEN_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(PTEN_coverage.get('percent_ntc'), 0)

		self.assertEqual(TP53_coverage.get('av_coverage'), 1244)
		self.assertEqual(TP53_coverage.get('percent_270x'), 100)
		self.assertEqual(TP53_coverage.get('percent_135x'), 100)
		self.assertEqual(TP53_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(TP53_coverage.get('percent_ntc'), 0)


		#Thyroid
		panel_obj = Panel.objects.filter(panel_name="Thyroid", dna_or_rna="DNA")
		colorectal_panel=panel_obj[0]
		panel_pk=colorectal_panel.pk
		sample_obj = SampleAnalysis.objects.filter(sample_id="21M00305-control",panel=panel_pk)
		sample=sample_obj[0]
		coverage_data= get_coverage_data(sample)

		NRAS_coverage=coverage_data.get('NRAS')
		HRAS_coverage=coverage_data.get('HRAS')
		KRAS_coverage=coverage_data.get('KRAS')
		BRAF_coverage=coverage_data.get('BRAF')
		TP53_coverage=coverage_data.get('TP53')
		RET_coverage=coverage_data.get('RET')

		self.assertEqual(NRAS_coverage.get('av_coverage'), 1380)
		self.assertEqual(NRAS_coverage.get('percent_270x'), 100)
		self.assertEqual(NRAS_coverage.get('percent_135x'), 100)
		self.assertEqual(NRAS_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(NRAS_coverage.get('percent_ntc'), 0)

		self.assertEqual(HRAS_coverage.get('av_coverage'), 1222)
		self.assertEqual(HRAS_coverage.get('percent_270x'), 100)
		self.assertEqual(HRAS_coverage.get('percent_135x'), 100)
		self.assertEqual(HRAS_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(HRAS_coverage.get('percent_ntc'), 0)

		self.assertEqual(KRAS_coverage.get('av_coverage'), 1288)
		self.assertEqual(KRAS_coverage.get('percent_270x'), 100)
		self.assertEqual(KRAS_coverage.get('percent_135x'), 100)
		self.assertEqual(KRAS_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(KRAS_coverage.get('percent_ntc'), 0)


		self.assertEqual(BRAF_coverage.get('av_coverage'), 1422)
		self.assertEqual(BRAF_coverage.get('percent_270x'), 100)
		self.assertEqual(BRAF_coverage.get('percent_135x'), 100)
		self.assertEqual(BRAF_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(BRAF_coverage.get('percent_ntc'), 0)


		self.assertEqual(TP53_coverage.get('av_coverage'), 1244)
		self.assertEqual(TP53_coverage.get('percent_270x'), 100)
		self.assertEqual(TP53_coverage.get('percent_135x'), 100)
		self.assertEqual(TP53_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(TP53_coverage.get('percent_ntc'), 0)

		self.assertEqual(RET_coverage.get('av_coverage'), 1570)
		self.assertEqual(RET_coverage.get('percent_270x'), 100)
		self.assertEqual(RET_coverage.get('percent_135x'), 100)
		self.assertEqual(RET_coverage.get('av_ntc_coverage'), 0)
		self.assertEqual(RET_coverage.get('percent_ntc'), 0)




















