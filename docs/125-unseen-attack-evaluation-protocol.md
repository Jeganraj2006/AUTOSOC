# Unseen Attack Evaluation Protocol

## Purpose
To accurately evaluate how well the baseline models detect "previously unseen behavior" without improperly mislabeling them as "confirmed zero-days", we will hold out specific attack families from the training phase.

## Methodology
1. Select a specific attack family (e.g., `PortScan` or `Exploits`) depending on the dataset.
2. Remove ALL instances of this attack family from the **Training** split.
3. Train supervised models on Benign data + Remaining Attack families.
4. Evaluate models on the Validation/Test set containing both the seen families and the **Unseen Attack Family**.

## Terminology
In evaluations, the held-out attacks will be referred to as "previously unseen attack family during training". They are NOT "zero-days", because a dataset label does not inherently constitute a true in-the-wild zero-day exploit.
