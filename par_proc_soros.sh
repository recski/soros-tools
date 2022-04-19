for f in data/soros_monthly/*$1*.csv; do
    n=`basename $f | cut -d'.' -f1`
    echo $n
    cat $f | python preproc.py > data/ana/$n.jsonl 2> data/log/$n.log &
done
