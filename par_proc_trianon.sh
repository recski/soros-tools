for f in split/*.csv; do
    n=`basename $f | cut -d'.' -f1`
    echo $n
    cat $f | python ../soros/soros-tools/preproc_trianon.py > ana/$n.jsonl 2> log/$n.log &
done
