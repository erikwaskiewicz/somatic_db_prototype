


for s in $(cat $1); do
    sample_id=$(echo $s | cut -d, -f1)
    referral=$(echo $s | cut -d, -f4)
    ws=$(echo $s | cut -d, -f2)
    cov=$(echo $s | cut -d, -f5)
    ntc_cov=$(echo $s | cut -d, -f6)


    echo $sample_id
    echo $referral
    echo $ws
    echo $cov
    echo $ntc_cov

    python manage.py import_rna \
      --run $2 \
      --worksheet $ws \
      --sample $sample_id \
      --panel $referral \
      --fusions Database/"$sample_id"_fusion_check.csv \
      --coverage "$cov","$ntc_cov"
done



