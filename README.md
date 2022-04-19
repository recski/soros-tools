# soros-tools

scripts to preprocess `soros` and `trianon` datasets with `emtsv` and then use dependency graphs to build `POTATO` datasets


## sample commands for trianon dataset

split dataset into 43 files of 1000 docs each:

```
cat articles_trianon_only_cleaned_categorized.csv | python split_trianon.py 1000 split/trianon
```

preprocess single file (once
[emtsv](https://github.com/nytud/emtsv#as-service-through-rest-api-docker-container) is running on port 5000)

```
cat split/trianon_0.csv | python preproc_trianon.py > ana/trianon_0.jsonl
```

preprocess all files in parallel

```
nice bash par_proc_trianon.sh
```


build POTATO dataset

```
cat ana/trianon_*.jsonl | python build_potato_dataset.py trianon_ana_potato.csv trianon
```


