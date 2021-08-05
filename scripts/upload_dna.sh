


for s in $(cat $1); do
    sample_id=$(echo $s | cut -d, -f1)
    referral=$(echo $s | cut -d, -f4)
    ws=$(echo $s | cut -d, -f2)

    echo $sample_id
    echo $referral
    echo $ws

    python manage.py import_dna \
      --run $2 \
      --worksheet $ws \
      --sample $sample_id \
      --panel $referral \
      --variants Database/"$sample_id"_variants.tsv \
      --coverage Database/"$sample_id"_"$referral"_coverage.json
done



