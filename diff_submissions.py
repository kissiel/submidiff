#!/usr/bin/env python3

"""
Take two checkbox submission and print out differences in test outcome
between those two.
"""

import json
import tarfile
import sys

def extract_submissions(xz_file: str) -> dict:
    """
    Open submission.tar.xz and extract the submission.json that's within.
    Return unmarshalled JSON as a dictionary.
    """
    # Extract the submission.json from submission.tar.xz
    with tarfile.open(xz_file, "r:xz") as tar:
        json_file = tar.extractfile("submission.json")
        json_data = json_file.read()
        return json.loads(json_data)

def simplify_submission(submission: dict) -> dict:
    """
    Take a complicated checkbox submission and simplify it to a simple
    "job_id": "outcome" dict.
    """
    return {result["id"]: result["status"] for result in submission["results"]}


def diff_submissions(submission1: dict, submission2: dict) -> dict:
    """
    Take two simplified submissions and a tuple containing:
    - jobs that were only present in the first submission
    - jobs that were only present in the second submission
    - jobs that were present in both submissions but had different outcomes
    """
    jobs1 = set(submission1.keys())
    jobs2 = set(submission2.keys())
    only1 = jobs1 - jobs2
    only2 = jobs2 - jobs1
    both = jobs1 & jobs2
    different = {job: (submission1[job], submission2[job]) for job in both if submission1[job] != submission2[job]}
    return only1, only2, different

def colorize_outcome(outcome: str) -> str:
    """
    Given an outcome, return a colorized version of it.
    """
    prefix = ""
    if outcome == "pass":
        prefix = "\033[1;32;5m"
    elif outcome == "fail":
        prefix = "\033[1;31;5m"

    return prefix + outcome + "\033[0m"


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: diff_submissions.py submission1.tar.xz submission2.tar.xz")
    submission1 = simplify_submission(extract_submissions(sys.argv[1]))
    submission2 = simplify_submission(extract_submissions(sys.argv[2]))
    only1, only2, different = diff_submissions(submission1, submission2)
    if only1:
        print(f"Jobs only in the {sys.argv[1]}:")
        for job in sorted(only1):
            print(f"  '{job}': '{colorize_outcome(submission1[job])}'")

    if only2:
        print(f"Jobs only in the {sys.argv[2]}:")
        for job in sorted(only2):
            print(f"  '{job}': '{colorize_outcome(submission2[job])}'")

    if different:
        print("Jobs with different outcomes:")
        print(f"  {sys.argv[1]} vs {sys.argv[2]}")
        for job, outcomes in different.items():
            print(f"  '{job}': '{outcomes[0]} ' vs '{outcomes[1]}'")



if __name__ == "__main__":
    main()
