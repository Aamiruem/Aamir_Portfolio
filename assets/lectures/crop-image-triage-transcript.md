## Opening

A field worker takes a photo of a crop that may be under stress. The real problem is not just asking a model to name a disease. A wrong confident answer can waste a farmer’s time, while a useful system needs to say what it saw, how sure it is, and when a person should take over. In this lesson, we’ll design a small image-triage pipeline around that real constraint.

## Define the task

Start with a narrow, testable goal: identify a short list of visible symptoms and route uncertain photos for human review. Do not promise a diagnosis from one photo. Define the classes with an agronomist, collect examples across farms, phones, lighting, and growth stages, and record the image’s location and date only when the user has agreed to that collection.

## Build a trustworthy dataset

The split matters as much as the model. If near-identical photos from the same plant land in both training and test sets, your test score can look excellent while the model fails on a new farm. Split by farm or collection session first. Keep a final untouched test set, inspect class balance, and label uncertain examples for review instead of quietly forcing a label.

## Train and evaluate

For object detection, each example needs a class and a bounding box around the visible symptom. Train a baseline detector, then inspect precision and recall per class. If missing a severe symptom is costly, monitor recall; if false alarms overwhelm the field team, monitor precision too. A single overall accuracy number hides both failure modes. Review the confusion matrix and sample false positives and false negatives with a domain expert.

## Make uncertainty useful

At inference time, do not turn every prediction into an alert. Apply a confidence threshold chosen on validation data. High-confidence results can show the detected region and a cautious next step. Low-confidence or out-of-distribution photos should say “needs review.” The safe fallback is part of the product, not a failure of the model.

## Ship the service

A production request can carry an image and a request ID. Validate file type and size, reject unreadable images, run inference in a worker, and return the model version with each result. Store only the image and metadata the user has consented to retain. Log latency and review outcomes so the team can spot drift without treating a model score as ground truth.

## Close

The useful deliverable is a measured triage workflow: a carefully split dataset, per-class metrics, a human-review path, and a service that exposes uncertainty. Start with one crop and one field partner, learn from reviewed examples, and expand only when the system helps people make a better decision.
