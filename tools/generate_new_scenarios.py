#!/usr/bin/env python3
"""Merge of gen_part1 + gen_part2.  Run this file to write all 100 new scenarios.

  python tools/generate_new_scenarios.py

Families generated (100 total):
  retrieval_recall_scale         rrs001-rrs010   10 scenarios
  retrieval_vocabulary_bridge    rvb001-rvb010   10 scenarios
  retrieval_scope_enforcement    rse001-rse010   10 scenarios
  retrieval_deduplication        rde001-rde010   10 scenarios
  injection_eviction_priority    iep001-iep015   15 scenarios
  injection_intra_bucket_order   iibo001-iibo010 10 scenarios
  long_horizon_accumulation      lha001-lha015   15 scenarios
  multi_agent_belief_propagation mabp001-mabp010 10 scenarios
  multi_agent_conflict_resolution macr001-macr010 10 scenarios
"""
import sys, os

# Make the tools directory importable regardless of cwd
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from gen_part1 import SCENARIOS_1          # 40 scenarios
from gen_part2 import SCENARIOS_2, write_all, BASE  # 60 scenarios + writer

ALL_SCENARIOS = SCENARIOS_1 + SCENARIOS_2

if __name__ == "__main__":
    print(f"Generating {len(ALL_SCENARIOS)} scenarios into {BASE} ...")
    write_all(ALL_SCENARIOS)
    # summary by family
    from collections import Counter
    counts = Counter(s["family"] for s in ALL_SCENARIOS)
    print("\nFamily breakdown:")
    for fam, n in sorted(counts.items()):
        print(f"  {fam:<40} {n}")
    print(f"\nTotal: {sum(counts.values())} scenarios across {len(counts)} families.")
