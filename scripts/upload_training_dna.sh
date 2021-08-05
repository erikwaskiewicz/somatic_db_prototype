source ~/miniconda3/bin/activate somatic_variant_db


ws=$1
run=dna_training


python manage.py import_dna \
  --run $run \
  --worksheet $ws \
  --sample 21M06864-1 \
  --panel Lung \
  --variants /home/ew/training_samples/21M06864-1/21M06864-1_Lung.tsv \
  --coverage /home/ew/training_samples/21M06864-1/21M06864-1_Lung_coverage.json


python manage.py import_dna \
  --run $run \
  --worksheet $ws \
  --sample 20M15539-2 \
  --panel Melanoma \
  --variants /home/ew/training_samples/20M15539-2/20M15539-2_Melanoma.tsv \
  --coverage /home/ew/training_samples/20M15539-2/20M15539-2_Melanoma_coverage.json


python manage.py import_dna \
  --run $run \
  --worksheet $ws \
  --sample 20M14433 \
  --panel Thyroid \
  --variants /home/ew/training_samples/20M14433/20M14433_Thyroid.tsv \
  --coverage /home/ew/training_samples/20M14433/20M14433_Thyroid_coverage.json

~/miniconda3/bin/deactivate

