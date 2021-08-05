source ~/miniconda3/bin/activate somatic_variant_db


ws=$1
run=audit_samples


python manage.py import_dna \
  --run $run \
  --worksheet $ws \
  --sample 18M02467-1 \
  --panel Glioma \
  --variants /home/ew/training_samples/18M02467-1/18M02467-1_db.tsv \
  --coverage /home/ew/training_samples/18M02467-1/18M02467-1_Glioma_coverage.json


python manage.py import_dna \
  --run $run \
  --worksheet $ws \
  --sample 20M15221 \
  --panel Melanoma \
  --variants /home/ew/training_samples/20M15221/20M15221_db.tsv \
  --coverage /home/ew/training_samples/20M15221/20M15221_Melanoma_coverage.json


python manage.py import_dna \
  --run $run \
  --worksheet $ws \
  --sample 20M15489 \
  --panel Colorectal \
  --variants /home/ew/training_samples/20M15489/20M15489_db.tsv \
  --coverage /home/ew/training_samples/20M15489/20M15489_Colorectal_coverage.json


~/miniconda3/bin/deactivate

