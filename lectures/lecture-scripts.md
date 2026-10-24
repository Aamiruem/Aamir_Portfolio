# Practical lecture scripts

These scripts are the narration and lesson plan for the portfolio lecture videos. They use the existing project photos as presenter cutaways. The AI/ML example is a realistic field workflow and is clearly framed as a teaching scenario rather than a claim that the site already ships that exact system.

## 01 — From field photo to useful crop alert

**Track:** AI/ML project · computer vision · responsible deployment  
**Target length:** 4–5 minutes  
**Problem:** A field team needs to triage crop photos when specialists cannot inspect every image immediately.

### Narration

**Opening**  
A field worker takes a photo of a crop that may be under stress. The real problem is not just asking a model to name a disease. A wrong confident answer can waste a farmer’s time, while a useful system needs to say what it saw, how sure it is, and when a person should take over. In this lesson, we’ll design a small image-triage pipeline around that real constraint.

**Define the task**  
Start with a narrow, testable goal: identify a short list of visible symptoms and route uncertain photos for human review. Do not promise a diagnosis from one photo. Define the classes with an agronomist, collect examples across farms, phones, lighting, and growth stages, and record the image’s location and date only when the user has agreed to that collection.

**Build a trustworthy dataset**  
The split matters as much as the model. If near-identical photos from the same plant land in both training and test sets, your test score can look excellent while the model fails on a new farm. Split by farm or collection session first. Keep a final untouched test set, inspect class balance, and label uncertain examples for review instead of quietly forcing a label.

**Train and evaluate**  
For object detection, each example needs a class and a bounding box around the visible symptom. Train a baseline detector, then inspect precision and recall per class. If missing a severe symptom is costly, monitor recall; if false alarms overwhelm the field team, monitor precision too. A single overall accuracy number hides both failure modes. Review the confusion matrix and sample false positives and false negatives with a domain expert.

**Make uncertainty useful**  
At inference time, do not turn every prediction into an alert. Apply a confidence threshold chosen on validation data. High-confidence results can show the detected region and a cautious next step. Low-confidence or out-of-distribution photos should say “needs review.” The safe fallback is part of the product, not a failure of the model.

**Ship the service**  
A production request can carry an image and a request ID. Validate file type and size, reject unreadable images, run inference in a worker, and return the model version with each result. Store only the image and metadata the user has consented to retain. Log latency and review outcomes so the team can spot drift without treating a model score as ground truth.

**Close**  
The useful deliverable is a measured triage workflow: a carefully split dataset, per-class metrics, a human-review path, and a service that exposes uncertainty. Start with one crop and one field partner, learn from reviewed examples, and expand only when the system helps people make a better decision.

### On-screen code / graphic

```text
photo → validate → detector → confidence + image-quality checks
                              ├─ clear result → cautious guidance
                              └─ uncertain → human review
```

Show the decision flow, then a sample result card with `class`, `confidence`, `model_version`, and `review_required`. Label sample values as illustrative.

## 02 — Build a low-stock alert API that does not spam

**Track:** Coding project · Node.js · Express · MongoDB  
**Target length:** 4–5 minutes  
**Problem:** A small shop needs to flag low inventory without creating duplicate alerts or accepting invalid stock updates.

### Narration

**Opening**  
A shop owner discovers an item is out of stock only after a customer orders it. We’ll build the first slice of a low-stock alert API. The goal is simple: safely update stock, return the current item, and create an alert only when stock crosses the threshold. The edge cases are where the useful engineering happens.

**Model the resource**  
Represent an item with a name, nonnegative integer quantity, and nonnegative integer reorder threshold. Keep the MongoDB model responsible for stored shape, and validate requests at the API boundary so bad input gets a clear response before it reaches the database.

**Write the route and controller**  
Keep the route thin. It declares the URL and middleware; the controller handles the request and response; the model handles persistence. This split makes it easier to test each rule and add authentication later without mixing business logic into the route file.

**Validate updates**  
Accept a quantity update only when it is an integer greater than or equal to zero. Do not use a truthiness check: zero is a valid quantity. Validate the item ID, return 404 for a missing item, and return 400 for malformed input. Use an atomic database update so two requests do not overwrite one another’s stock changes.

**Detect a threshold crossing**  
An alert should be created when quantity moves from above the threshold to at or below it. If every edit while an item stays low creates another alert, the system will spam the owner. Compare the previous and updated state, and attach a stable idempotency key such as item ID plus the inventory change ID. A unique index can prevent retries from creating duplicate alerts.

**Protect and observe it**  
Require authentication for stock changes, limit request size, and never expose secrets in the repository. Add structured logs with the request ID and outcome, but do not log passwords or sensitive customer data. Test the important cases: quantity zero, negative quantity, missing item, a threshold crossing, an update that stays below threshold, and a retried request.

**Close**  
The finished slice is more than a POST endpoint. It has clear validation, atomic persistence, deliberate alert rules, and predictable errors. That is the difference between code that works in one demo and an API a shop can rely on.

### On-screen code / graphic

```js
const quantity = Number(req.body.quantity);
if (!Number.isInteger(quantity) || quantity < 0) {
  return res.status(400).json({ error: 'quantity must be a non-negative integer' });
}
```

Then show the state transition: `12 → 4` (crosses threshold 5: create one alert), `4 → 3` (still low: no duplicate alert), `3 → 0` (valid stock update).
