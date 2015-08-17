#!/usr/bin/env python
#encoding: utf-8

"""
This is a script for converting the raw Appraise XML file to pairwise comparisons
in the "WMT CSV" format. 

Usage: python wmt15.xml.gz
-> produces a CSV file for each language pair, anonymizing the judges.

Example XML:

    <WMT15-results>
    <HIT hit-id="32872282" source-language="deu" block-id="-1" target-language="eng">
    <ranking-task id="0">
      <ranking-result duration="00:00:35.337000" user="jonny_appleseed">
        <translation system="newstest2015.online-E.0.de-en.txt" rank="3" />
        <translation system="newstest2015.dfki-experimental.4060.de-en.txt" rank="4" />
        <translation system="newstest2015.KIT.4017.de-en.txt" rank="2" />
        <translation system="newstest2015.Illinois.4085.de-en.txt" rank="5" />
        <translation system="newstest2015.online-B.0.de-en.txt" rank="1" />
      </ranking-result>
    </ranking-task>
    <ranking-task id="1">
      <ranking-result duration="00:01:14.726000" user="jonny_appleseed">
        <translation system="newstest2015.uedin-jhu-phrase.4102.de-en.txt" rank="1" />
        <translation system="newstest2015.online-F.0.de-en.txt" rank="4" />
        <translation system="newstest2015.online-E.0.de-en.txt" rank="2" />
        <translation system="newstest2015.online-A.0.de-en.txt" rank="1" />
        <translation system="newstest2015.Illinois.4085.de-en.txt,newstest2015.uedin-syntax.4027.de-en.txt" rank="3" />
      </ranking-result>
    </ranking-task>
    <ranking-task id="2">
      <ranking-result duration="00:01:02.235000" user="jonny_appleseed">
        <translation system="newstest2015.uedin-syntax.4027.de-en.txt" rank="1" />
        <translation system="newstest2015.online-F.0.de-en.txt" rank="2" />
        <translation system="newstest2015.online-A.0.de-en.txt" rank="2" />
        <translation system="newstest2015.Neural-MT.4097.de-en.txt" rank="5" />
        <translation system="newstest2015.online-E.0.de-en.txt" rank="1" />
      </ranking-result>
    </ranking-task>
    </HIT>
    ...

Original Author: Keisuke Sakaguchi
WMT modifications by: Matt Post
"""

EXCLUDE_REF = True
N = 2 # extracting pairwise judgements

import sys
import os
import csv 
import gzip
import itertools
import xml.etree.ElementTree as ET
from collections import Counter

def extract_all_judgements(ranking):
    systems_j = []
    ranks_j = []
    if len(ranking.findall(".//translation")) == 0:
        pass
    else:
        for i, rank in enumerate(ranking.findall(".//translation")):
            rank_i = rank.attrib['rank']
            for system_name in rank.attrib['system'].split(','):
                if EXCLUDE_REF and system_name[0:3] == 'ref':
                    pass
                else:
                    systems_j.append(system_name)
                    ranks_j.append(rank_i)

    return zip(systems_j, ranks_j)

judges = {}
def anonymize_judge(judgeID):
    if not judges.has_key(judgeID):
        judges[judgeID] = 'judge%d' % (len(judges)+1)
    return judges[judgeID]

xmlPath = sys.argv[1]
xmlStream = gzip.GzipFile(xmlPath) if xmlPath.endswith('.gz') else open(xmlPath)
elem = ET.parse(xmlStream).getroot()

header_fields = 'srclang,trglang,srcIndex,segmentId,judgeID,system1Id,system1rank,system2Id,system2rank,rankingID'.split(',')
csvPrefix = xmlPath.split('.xml')[0]

writers = {}

hits = elem.findall(".//HIT")
resultno = 0
for hit in hits:
    source_lang = hit.attrib['source-language']
    target_lang = hit.attrib['target-language']

    if not writers.has_key((source_lang,target_lang)):
        writers[(source_lang,target_lang)] = csv.DictWriter(open('%s.%s-%s.csv' % (csvPrefix,source_lang, target_lang), 'w'), fieldnames=header_fields)
        writers[(source_lang,target_lang)].writeheader()
    
    rankings = hit.findall(".//ranking-task")

    for ranking in rankings:
        for result in ranking.findall(".//ranking-result"):
            resultno += 1

            csv_row = {}
            csv_row['srcIndex'] = ranking.attrib['id']
            csv_row['segmentId'] = ranking.attrib['id']
            csv_row['srclang'] = source_lang
            csv_row['trglang'] = target_lang
            csv_row['judgeID'] = anonymize_judge(result.attrib['user'])

            # This groups together the ranking task that the pairwise judgments came from
            csv_row['rankingID'] = resultno

            systems_ranks = extract_all_judgements(result)
            for element in itertools.combinations(systems_ranks, N):
                for i, system_rank in enumerate(element):
                    systemID = "system{}Id".format(str(i+1))
                    systemRank = "system{}rank".format(str(i+1))
                    csv_row[systemID] = system_rank[0]
                    csv_row[systemRank] = system_rank[1]

                writers[(source_lang, target_lang)].writerow(csv_row)

xmlStream.close()
