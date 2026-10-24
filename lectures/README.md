# Portfolio lectures

The videos use Aamir's existing work photos and a generated en-IN English voice (Microsoft `en-IN-PrabhatNeural`). The generated narration is included both in each MP4 and as a separate MP3. Each lecture also has a Markdown transcript and an SRT caption file.

## Re-render

From the portfolio root, install the Python dependencies and run the renderer:

```powershell
python -m pip install -r lectures/requirements.txt
python lectures/create_lectures.py
```

The renderer sends narration text to the Edge text-to-speech service, so it needs an internet connection. Outputs go to `assets/lectures/`.

## Lessons

- **From field photo to useful crop alert:** a practical computer-vision triage workflow, with farm-aware data splits, per-class evaluation, uncertainty handling, and a human-review path.
- **Build a low-stock alert API that does not spam:** a Node.js API lesson about validation, atomic updates, threshold transitions, idempotency, and alert deduplication.
