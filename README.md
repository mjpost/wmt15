# How to produce the WMT human rankings

0. If you *really* want to start from the beginning, download the raw XML dump of the 
   ranking tasks from [Appraise](http://appraise.cf/admin/wmt15/hit/) and save it
   as data/wmt15.xml.gz. Then run

        cd data
        python xml2csv.py wmt15.xml.gz

   This will generate wmt15.XXX.csv files, one for each language pair, and anonymize the
   judges.

   Note that WMT15 had judges compare unique outputs, instead of system outputs (which
   was done prior to WMT15). Rankings were then assigned to all systems that had a unique
   output. For this reason, the WMT CSV file has a slightly different format: each line
   is a pairwise (2-way) comparison instead of a 5-way one. The last field, rankingID, groups
   together the judgments that were in an individual ranking task.

1. Now, to compute the rankings. Install wmt-trueskill:

        git clone https://github.com/keisks/wmt-trueskill

2. Install the trueskill code

        cd wmt-trueskill/src
        git clone https://github.com/sublee/trueskill

3. Compute the rankings

        for type in ew ts; do 
          for lang in $(ls data/wmt15*csv | cut -d. -f2); do 
            qsub scripts/run-1000.sh $lang $type
          done
        done

   If you're not on a cluster, it's

        for type in ew ts; do 
          for lang in $(ls data/wmt15*csv | cut -d. -f2); do 
            for num in $(seq 1 1000); do
              SGE_TASK_ID=$num ./scripts/run-1000.sh $lang $type
            done
          done
        done

4. Compute the clusters

        for lang in $(ls data/wmt15*csv | cut -d. -f2); do 
          ./wmt-trueskill/eval/cluster.py -by-rank results/$lang/ts/*/*.json > results/wmt15.$lang.txt; 
        done

5. That's it! Please direct questions to Matt Post <post@cs.jhu.edu>.
