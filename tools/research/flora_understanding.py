#!/usr/bin/env python3
"""Reproduce candidate understanding and research-wave evidence, locally only."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from cios.applications.flora.research_intelligence.model import load_assessment
from cios.applications.flora.research_intelligence.registry import enterprise_domain
from cios.applications.flora.research_intelligence.understanding import (load_review,assess,before_after,replay_research,report_markdown)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--enterprise',choices=('lloyds','easyjet'),required=True)
    p.add_argument('--as-of',required=True)
    p.add_argument('--output',type=Path,required=True,help='New local directory; existing directories are never overwritten')
    a=p.parse_args(argv);domain=enterprise_domain(a.enterprise);data=load_assessment(domain);review=load_review(domain)
    outputs={'assessment.json':assess(data,review,a.as_of),'comparison.json':before_after(data,review,a.as_of),
             'replayed-checkpoint.json':replay_research(data,review)}
    report=report_markdown(data,review,a.as_of)
    a.output.mkdir(parents=True,exist_ok=False)
    for filename,value in outputs.items():(a.output/filename).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    (a.output/'report.md').write_text(report)
    print(f'{a.enterprise}: candidate assessment exported; no canonical acceptance or Pipeline mutation')
    return 0


if __name__=='__main__':raise SystemExit(main())
