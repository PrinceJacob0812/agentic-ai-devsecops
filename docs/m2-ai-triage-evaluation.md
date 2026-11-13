

\# M2 AI Triage Evaluation



\## 1. Evaluation Purpose



The evaluation script `src/evaluate\_triage.py` compares AI triage predictions with the expected labels in a labelled dataset.



It reports evaluation coverage, failed and unmatched predictions, uncertain predictions, classification metrics, and a confusion matrix.



Two curated datasets were evaluated:



\- `samples/sast\_findings.json` with `results/evaluation\_results.json`

\- `samples/robustness\_findings.json` with `results/robustness\_results.json`



These are controlled test datasets. They are useful for checking the current implementation but are not a substitute for validation on a large, independently labelled production dataset.



\## 2. SAST Evaluation



\### Dataset and Prediction Matching



| Measure | Result |

|---|---:|

| Ground-truth findings | 10 |

| Valid evaluated findings | 10 |

| Failed predictions | 0 |

| Unmatched results | 0 |

| Duplicate results | 0 |

| Evaluation coverage | 100% |

| Uncertain predictions | 0 |

| Decisive predictions | 10 |



\### Classification Metrics



| Class | Precision | Recall | F1-score | Support |

|---|---:|---:|---:|---:|

| TRUE\_POSITIVE | 1.00 | 1.00 | 1.00 | 6 |

| FALSE\_POSITIVE | 1.00 | 1.00 | 1.00 | 4 |

| INSUFFICIENT\_EVIDENCE | 0.00 | 0.00 | 0.00 | 0 |



Overall accuracy: \*\*1.00 (100%)\*\*



Macro average: precision 0.67, recall 0.67, F1-score 0.67.



Weighted average: precision 1.00, recall 1.00, F1-score 1.00.



The insufficient-evidence class has zero support in this dataset. Its zero-valued metrics should not be interpreted as a failed prediction; no examples of that class were present in the ground truth.



\### Confusion Matrix



Rows represent actual labels; columns represent predicted labels.



Label order: `TRUE\_POSITIVE`, `FALSE\_POSITIVE`, `INSUFFICIENT\_EVIDENCE`.



```text

\[\[6 0 0]

&#x20;\[0 4 0]

&#x20;\[0 0 0]]

```



\### Binary Metrics on Decisive Predictions



\- Accuracy: 1.00

\- True-positive precision: 1.00

\- True-positive recall: 1.00

\- True-positive F1-score: 1.00



\## 3. Robustness Evaluation



\### Dataset and Prediction Matching



| Measure | Result |

|---|---:|

| Ground-truth findings | 10 |

| Valid evaluated findings | 10 |

| Failed predictions | 0 |

| Unmatched results | 0 |

| Duplicate results | 0 |

| Evaluation coverage | 100% |

| Uncertain predictions | 2 |

| Decisive predictions | 8 |



\### Classification Metrics



| Class | Precision | Recall | F1-score | Support |

|---|---:|---:|---:|---:|

| TRUE\_POSITIVE | 1.00 | 1.00 | 1.00 | 5 |

| FALSE\_POSITIVE | 1.00 | 1.00 | 1.00 | 3 |

| INSUFFICIENT\_EVIDENCE | 1.00 | 1.00 | 1.00 | 2 |



Overall accuracy: \*\*1.00 (100%)\*\*



Macro average: precision 1.00, recall 1.00, F1-score 1.00.



Weighted average: precision 1.00, recall 1.00, F1-score 1.00.



\### Confusion Matrix



Rows represent actual labels; columns represent predicted labels.



Label order: `TRUE\_POSITIVE`, `FALSE\_POSITIVE`, `INSUFFICIENT\_EVIDENCE`.



```text

\[\[5 0 0]

&#x20;\[0 3 0]

&#x20;\[0 0 2]]

```



\### Binary Metrics on Decisive Predictions Only



\- Accuracy: 1.00

\- True-positive precision: 1.00

\- True-positive recall: 1.00

\- True-positive F1-score: 1.00



These binary metrics exclude the two uncertain predictions. They should be interpreted alongside the overall three-class accuracy and the 100% evaluation coverage.



\## 4. Combined Results



| Measure | SAST | Robustness |

|---|---:|---:|

| Findings evaluated | 10 | 10 |

| Evaluation coverage | 100% | 100% |

| Overall accuracy | 100% | 100% |

| Failed predictions | 0 | 0 |

| Unmatched results | 0 | 0 |

| Uncertain predictions | 0 | 2 |



Across both datasets, 20 findings were evaluated and all predictions matched their expected labels.



\## 5. Interpretation and Limitations



The results show that the current agent correctly classified all examples in these two curated test datasets. They demonstrate that the evaluation pipeline, result matching, and current test cases are working as expected.



They do not establish that the model will achieve 100% accuracy on unseen or production findings. The datasets are small, and their labels may not represent the variety, ambiguity, and complexity of real security findings.



Other limitations:



\- The evaluation does not measure performance on a large independent benchmark.

\- The model-provided confidence score is not calibrated as a probability.

\- No measured false-positive reduction rate is claimed because a baseline comparison has not been completed.

\- The robustness dataset includes two insufficient-evidence cases; the SAST dataset includes none.

\- Human review remains important for uncertain and potentially high-impact findings.



\## 6. Reproducing the Evaluation



From the repository root, run:



```powershell

python -m src.evaluate\_triage `

&#x20; --dataset samples/sast\_findings.json `

&#x20; --results results/evaluation\_results.json



python -m src.evaluate\_triage `

&#x20; --dataset samples/robustness\_findings.json `

&#x20; --results results/robustness\_results.json

```



The evaluation script requires the dependencies listed in `requirements.txt`, including scikit-learn.



\## 7. Conclusion



The current controlled evaluation completed with 100% coverage and 100% accuracy on both 10-example datasets. The results support the correctness of the current implementation against these test cases. Broader testing, baseline comparison, and real-world validation are required before making production-performance or false-positive-reduction claims.
