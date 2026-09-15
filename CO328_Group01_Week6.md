# CO328 Software Engineering — Week 6: Testing
## Group 01 | Reflect Studio — AI-Powered Smart Mirror for Elderly Care

| Field | Details |
|---|---|
| **Course** | CO328 Software Engineering |
| **Week** | 06 |
| **Date** | July 10, 2026 |
| **Group** | Group 01 |
| **Repository** | https://github.com/cepdnaclk/e21-3yp-ReflectStudio |
| **Branch** | `week6-testing` |

### Team Members
| Index | Name | Assigned Function |
|---|---|---|
| E/21/287 | Perera G.S.H | `classify_voice_command()` |
| E/21/229 | Kurera P.A.T | `validate_reminder()` |
| E/21/055 | Bandara K.N.K.L.N | `should_hide_notification()` |
| E/21/253 | Manabandu J.P.G.T.R | `should_send_emotion_alert()` |

---

## Context: Why We Created `testable_logic.py`

Reflect Studio's production services (`vision_engine.py`, `music_assistant.py`, `slideshow.py`, `ai_bot.py`) are tightly coupled to hardware and cloud infrastructure: a Raspberry Pi camera, GPIO presence sensors, AWS Rekognition, DynamoDB, S3, and the Gemini API. Running unit tests directly against these services would require real cloud credentials, physical hardware, and a Raspberry Pi environment — making tests impossible to run in CI or on a developer's PC.

To solve this, we identified the **core decision-making logic** inside each service — the conditional branches that determine *what the system does* — and extracted them into a single pure-Python module: `mirrorManwithUI/services/testable_logic.py`. This module has **zero external dependencies** (no AWS, no GPIO, no audio libraries), making every function deterministic and testable in complete isolation.

---

## Step 1: Test Case Design

### Function 1 — `classify_voice_command(text: str) → str`
**Member:** E/21/287 — Perera G.S.H
**File:** `mirrorManwithUI/services/testable_logic.py`

#### 1.1 Project Context

In Reflect Studio, the elderly user speaks to the mirror. The microphone records audio, which is transcribed to text by Google Speech Recognition. That raw text string is then passed to a command classifier to decide what the system should do next. This classifier is the critical decision point between the hardware layer (microphone) and the application layer (Mirror Man, music player).

In the production code (`music_assistant.py`), this logic exists inside `parse_command()` but is entangled with audio recording, subprocess management, and TTS calls. `classify_voice_command()` is a clean extraction of just the classification logic.

#### 1.2 Function Logic (Step-by-Step)

**Step 1 — Type guard:**
If the transcription engine returns `None` (network failure) or any non-string, the function fails fast with a `TypeError` rather than silently returning `UNKNOWN`.

**Step 2 — Empty string guard:**
An empty string after stripping (e.g., silence picked up by the mic) raises a `ValueError`. It is a programming error, not an unknown command.

**Step 3 — Normalise and match wake/dismiss words:**
The input is `.strip().lower()` so whitespace and capitalisation do not matter. Exact string comparison is then used for `"hello mirror"` and `"good bye"` / `"goodbye"`.

**Step 4 — Music control exact matches:**
`"pause music"`, `"resume music"`, and `"stop music"` are matched by exact equality after normalisation.

**Step 5 — Play prefix matching with song extraction:**
A priority-ordered list of prefixes (`"play me some "`, `"play me a "`, … `"play "`) is checked in order. If a prefix matches, the remainder of the string is the song name. An empty song name (e.g., `"Play "`) raises a `ValueError`.

**Step 6 — Default:**
Any unrecognised input returns `"UNKNOWN"`.

#### 1.3 Equivalence Classes

| # | Class | Representative Input | Expected Output |
|---|---|---|---|
| 1 | Valid wake word | `"Hello Mirror"` | `ACTIVATE_MIRROR_MAN` |
| 2 | Valid dismiss (two-word) | `"Good bye"` | `DEACTIVATE_MIRROR_MAN` |
| 3 | Valid dismiss (one-word) | `"goodbye"` | `DEACTIVATE_MIRROR_MAN` |
| 4 | Valid play with song | `"Play Perfect"` | `PLAY_MUSIC` |
| 5 | Valid pause | `"pause music"` | `PAUSE_MUSIC` |
| 6 | Valid resume | `"resume music"` | `RESUME_MUSIC` |
| 7 | Valid stop | `"stop music"` | `STOP_MUSIC` |
| 8 | Unrecognised command | `"open calendar"` | `UNKNOWN` |
| 9 | Empty string | `""` | `ValueError` |
| 10 | Play with no song name | `"Play "` | `ValueError` |
| 11 | Wrong type (None) | `None` | `TypeError` |

#### 1.4 Boundary Value Analysis

| Boundary | Input | Expected |
|---|---|---|
| Wake word with leading/trailing spaces | `" hello mirror "` | `ACTIVATE_MIRROR_MAN` |
| Play with valid song name | `"Play Perfect"` | `PLAY_MUSIC` |
| Play with only whitespace after | `"Play "` | `ValueError` |
| Bare "play" keyword only | `"play"` | `ValueError` |

#### 1.5 External Dependencies Requiring Mocking
- **Google Speech Recognition** — not needed; this function receives already-transcribed text, so no mocking is required for these tests.

#### 1.6 Tests Written: **12 tests**

---

### Function 2 — `validate_reminder(message, scheduled_time, current_time) → bool`
**Member:** E/21/229 — Kurera P.A.T
**File:** `mirrorManwithUI/services/testable_logic.py`

#### 2.1 Project Context

The Reflect Studio mobile app (Flutter) allows caregivers to schedule reminders for the elderly user — for example, "Take blood pressure medicine" at 9:00 AM. These reminders are sent to an S3 bucket, then picked up by the mirror and displayed at the scheduled time. Before a reminder is stored, the system must validate it to prevent bad data from reaching the mirror (e.g., reminders set in the past, empty messages, or messages too long to fit the mirror UI).

`validate_reminder()` is the single validation gate that enforces all these constraints in one place.

#### 2.2 Function Logic (Step-by-Step)

**Step 1 — Type guard on message:**
Ensures `message` is a `str`. Passing `None` (e.g., from a form that was never filled) raises a `TypeError`.

**Step 2 — Type guard on datetime objects:**
Both `scheduled_time` and `current_time` must be `datetime` instances. `current_time` is injected as a parameter rather than calling `datetime.now()` internally — this is a deliberate design choice that makes the function testable without any mocking.

**Step 3 — Blank message check:**
`message.strip()` catches both `""` and `"   "` (whitespace-only strings), which would produce an invisible notification on the mirror.

**Step 4 — Length check (MAX = 200 characters):**
The mirror display has a fixed area. Messages beyond 200 characters would overflow or be cut off. The boundary is enforced as a hard error.

**Step 5 — Future time check:**
`scheduled_time <= current_time` uses strict inequality (`<=`), meaning a reminder scheduled at exactly the current second is also rejected — it would already be "due" before it could be transmitted to the mirror.

**Step 6 — Return True:**
All checks passed; the reminder is valid.

#### 2.3 Equivalence Classes

| # | Class | Input | Expected |
|---|---|---|---|
| 1 | Valid future reminder | message="Take medicine", scheduled=tomorrow | `True` |
| 2 | Scheduled in past | scheduled=yesterday | `ValueError` |
| 3 | Scheduled exactly now | scheduled=now | `ValueError` |
| 4 | Empty message | `""` | `ValueError` |
| 5 | Whitespace-only message | `"   "` | `ValueError` |
| 6 | Message too long | `"A" * 201` | `ValueError` |
| 7 | Message exactly at limit | `"A" * 200` | `True` |
| 8 | None message | `None` | `TypeError` |

#### 2.4 Boundary Value Analysis

| Boundary | Input | Expected |
|---|---|---|
| 1 second in future | `now + timedelta(seconds=1)` | `True` |
| Exactly at now | `now` | `ValueError` |
| 1 second in past | `now - timedelta(seconds=1)` | `ValueError` |
| Message length = 200 | `"A" * 200` | `True` |
| Message length = 201 | `"A" * 201` | `ValueError` |

#### 2.5 External Dependencies Requiring Mocking
- **`datetime.now()`** — not needed; `current_time` is injected, so tests control the clock directly.
- **DynamoDB / S3** — not touched by this function; handled by the storage layer separately.

#### 2.6 Tests Written: **9 tests**

---

### Function 3 — `should_hide_notification(presence: bool, elapsed_seconds: float) → bool`
**Member:** E/21/055 — Bandara K.N.K.L.N
**File:** `mirrorManwithUI/services/testable_logic.py`

#### 3.1 Project Context

When the Reflect Studio mirror receives a one-time notification (e.g., a caregiver sends "Don't forget your appointment at 3 PM!"), it displays a notification banner on the mirror UI. Per functional requirement FR-16: *"The system shall display notifications for 15 seconds when someone is present."*

This function implements that rule. It is called periodically by the display loop with the current elapsed time since the notification appeared. When it returns `True`, the UI hides the banner.

#### 3.2 Function Logic (Step-by-Step)

**Step 1 — Type guard on presence:**
The function strictly requires a `bool`. Python's `bool` is a subclass of `int`, so `isinstance(1, bool)` returns `False` — this ensures callers pass a proper boolean, not a truthy integer like `1`.

**Step 2 — Type guard on elapsed_seconds:**
Accepts `int` or `float`. Rejects strings like `"15"` which could arise from JSON parsing.

**Step 3 — Negative time guard:**
Negative elapsed time has no physical meaning and indicates a programming bug. A `ValueError` is raised.

**Step 4 — Decision (single expression):**
```
return presence and elapsed_seconds >= NOTIFICATION_DISPLAY_SECONDS
```
This captures the full business rule:
- `presence=False` → short-circuits to `False` immediately (no one to show it to).
- `presence=True, elapsed < 15` → still showing, return `False`.
- `presence=True, elapsed >= 15` → time is up, return `True` (hide it).

#### 3.3 Equivalence Classes

| # | Class | Inputs | Expected |
|---|---|---|---|
| 1 | Present, time expired | `True, 20` | `True` |
| 2 | Present, time not expired | `True, 5` | `False` |
| 3 | Not present, any time | `False, 20` | `False` |
| 4 | Present, zero elapsed | `True, 0` | `False` |
| 5 | Negative elapsed time | `True, -1` | `ValueError` |
| 6 | Wrong presence type | `"yes", 15` | `TypeError` |
| 7 | Wrong time type | `True, "15"` | `TypeError` |

#### 3.4 Boundary Value Analysis

| Boundary | Inputs | Expected |
|---|---|---|
| Just below 15s | `True, 14.99` | `False` |
| Exactly 15s | `True, 15` | `True` |
| Just above 15s | `True, 15.01` | `True` |
| Not present, large elapsed | `False, 100` | `False` |

#### 3.5 External Dependencies Requiring Mocking
- **`time.time()` / system clock** — not needed; `elapsed_seconds` is injected as a parameter.
- **GPIO presence sensor** — not touched by this function.

#### 3.6 Tests Written: **9 tests**

---

### Function 4 — `should_send_emotion_alert(emotion: str, confidence: float) → bool`
**Member:** E/21/253 — Manabandu J.P.G.T.R
**File:** `mirrorManwithUI/services/testable_logic.py`

#### 4.1 Project Context

One of Reflect Studio's core healthcare features is emotional monitoring. The Raspberry Pi camera captures the elderly user's face every 10 seconds. AWS Rekognition analyses the image and returns a list of detected emotions, each with a confidence percentage (e.g., `SAD: 87.3%, CALM: 10.1%`). The system selects the highest-confidence emotion and must decide: should we alert the caregiver via the mobile app?

The production code in `vision_engine.py` currently uses a simple check `if primary_emotion in ["SAD", "ANGRY", "FEAR"]` with no confidence threshold. `should_send_emotion_alert()` is a more robust version that also enforces a minimum confidence threshold of 80% to reduce false positives from uncertain detections.

#### 4.2 Function Logic (Step-by-Step)

**Step 1 — Type guard on emotion:**
Ensures the emotion label is a `str`. Passing `None` (e.g., if Rekognition returns no face details) raises a `TypeError`.

**Step 2 — Type guard on confidence:**
Accepts `int` or `float`. Rejects strings like `"90"` which could arise from deserialising JSON without proper type coercion.

**Step 3 — Empty emotion guard:**
An empty or whitespace-only emotion string indicates a data error. Raises a `ValueError`.

**Step 4 — Confidence range check:**
AWS Rekognition always returns confidence in [0, 100]. Values outside this range indicate data corruption or a programming error.

**Step 5 — Decision:**
```python
return (
    emotion.upper() in NEGATIVE_EMOTIONS
    and confidence >= EMOTION_CONFIDENCE_THRESHOLD
)
```
- `emotion.upper()` normalises case so `"sad"` and `"SAD"` both match.
- `NEGATIVE_EMOTIONS = {"SAD", "ANGRY", "FEAR", "DISGUSTED", "CONFUSED"}` — emotions classified as emotionally distressing.
- `EMOTION_CONFIDENCE_THRESHOLD = 80.0` — both conditions must hold; a confident positive emotion or an uncertain negative emotion does **not** trigger an alert.

#### 4.3 Equivalence Classes

| # | Class | Inputs | Expected |
|---|---|---|---|
| 1 | Negative emotion, high confidence | `"SAD", 90` | `True` |
| 2 | Negative emotion, below threshold | `"SAD", 50` | `False` |
| 3 | Positive emotion, any confidence | `"HAPPY", 95` | `False` |
| 4 | Neutral emotion | `"CALM", 90` | `False` |
| 5 | Lowercase negative emotion | `"sad", 90` | `True` |
| 6 | Confidence out of range (low) | `"SAD", -1` | `ValueError` |
| 7 | Confidence out of range (high) | `"SAD", 101` | `ValueError` |
| 8 | Empty emotion string | `"", 90` | `ValueError` |
| 9 | None emotion | `None, 90` | `TypeError` |
| 10 | String confidence | `"SAD", "90"` | `TypeError` |

#### 4.4 Boundary Value Analysis

| Boundary | Inputs | Expected |
|---|---|---|
| Just below threshold | `"SAD", 79.99` | `False` |
| Exactly at threshold | `"SAD", 80` | `True` |
| Just above threshold | `"SAD", 80.01` | `True` |
| Minimum valid confidence (0%) | `"SAD", 0` | `False` |
| Maximum valid confidence (100%) | `"SAD", 100` | `True` |

#### 4.5 External Dependencies Requiring Mocking
- **AWS Rekognition** — this function only receives the result of a Rekognition call; it does not call Rekognition itself. No mocking needed.
- **S3 / mobile push notification** — handled by the separate `send_alert_to_app()` function, not part of this logic.

#### 4.6 Tests Written: **14 tests**

---

## Step 2: Automated Unit Tests

### Framework Used
- **Language:** Python 3.12
- **Framework:** `pytest` with `pytest-mock`
- **Test File:** `mirrorManwithUI/tests/test_testable_logic.py`

### Test Results

All 44 tests passed locally:

```
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.1.1
collected 44 items

tests/test_testable_logic.py::test_classify_voice_command[Hello Mirror-ACTIVATE_MIRROR_MAN] PASSED
tests/test_testable_logic.py::test_classify_voice_command[ hello mirror -ACTIVATE_MIRROR_MAN] PASSED
tests/test_testable_logic.py::test_classify_voice_command[Good bye-DEACTIVATE_MIRROR_MAN] PASSED
tests/test_testable_logic.py::test_classify_voice_command[goodbye-DEACTIVATE_MIRROR_MAN] PASSED
tests/test_testable_logic.py::test_classify_voice_command[Play Perfect-PLAY_MUSIC] PASSED
tests/test_testable_logic.py::test_classify_voice_command[pause music-PAUSE_MUSIC] PASSED
tests/test_testable_logic.py::test_classify_voice_command[resume music-RESUME_MUSIC] PASSED
tests/test_testable_logic.py::test_classify_voice_command[stop music-STOP_MUSIC] PASSED
tests/test_testable_logic.py::test_classify_voice_command[open calendar-UNKNOWN] PASSED
tests/test_testable_logic.py::test_voice_command_rejects_empty_input PASSED
tests/test_testable_logic.py::test_voice_command_rejects_empty_song_name PASSED
tests/test_testable_logic.py::test_voice_command_rejects_invalid_type PASSED
tests/test_testable_logic.py::test_valid_future_reminder PASSED
tests/test_testable_logic.py::test_reminder_one_second_in_future PASSED
tests/test_testable_logic.py::test_reminder_rejects_exact_current_time PASSED
tests/test_testable_logic.py::test_reminder_rejects_past_time PASSED
tests/test_testable_logic.py::test_reminder_rejects_empty_message[] PASSED
tests/test_testable_logic.py::test_reminder_rejects_empty_message[   ] PASSED
tests/test_testable_logic.py::test_reminder_accepts_200_character_message PASSED
tests/test_testable_logic.py::test_reminder_rejects_201_character_message PASSED
tests/test_testable_logic.py::test_reminder_rejects_invalid_message_type PASSED
tests/test_testable_logic.py::test_should_hide_notification[True-14.99-False] PASSED
tests/test_testable_logic.py::test_should_hide_notification[True-15-True] PASSED
tests/test_testable_logic.py::test_should_hide_notification[True-15.01-True] PASSED
tests/test_testable_logic.py::test_should_hide_notification[False-15-False] PASSED
tests/test_testable_logic.py::test_should_hide_notification[False-100-False] PASSED
tests/test_testable_logic.py::test_should_hide_notification[True-0-False] PASSED
tests/test_testable_logic.py::test_notification_rejects_negative_time PASSED
tests/test_testable_logic.py::test_notification_rejects_invalid_presence_type PASSED
tests/test_testable_logic.py::test_notification_rejects_invalid_time_type PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[SAD-79.99-False] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[SAD-80-True] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[SAD-80.01-True] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[ANGRY-95-True] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[HAPPY-95-False] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[CALM-90-False] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[SAD-0-False] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[SAD-100-True] PASSED
tests/test_testable_logic.py::test_should_send_emotion_alert[sad-90-True] PASSED
tests/test_testable_logic.py::test_emotion_alert_rejects_out_of_range_confidence[-1] PASSED
tests/test_testable_logic.py::test_emotion_alert_rejects_out_of_range_confidence[101] PASSED
tests/test_testable_logic.py::test_emotion_alert_rejects_empty_emotion PASSED
tests/test_testable_logic.py::test_emotion_alert_rejects_invalid_emotion_type PASSED
tests/test_testable_logic.py::test_emotion_alert_rejects_invalid_confidence_type PASSED

============================= 44 passed in 0.07s ==============================
```

---

## Step 3: CI Workflow and Peer Review

### GitHub Actions CI Workflow

**File:** `.github/workflows/tests.yml`

```yaml
name: Run Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: ["**"]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-mock

      - name: Run unit tests
        working-directory: mirrorManwithUI
        run: pytest tests/test_testable_logic.py -v
```

The workflow triggers automatically on every push and pull request to any branch. It installs only the lightweight test dependencies (no hardware libraries required) and runs the full test suite. The CI run fails if any test fails, blocking a bad merge.

**Branch pushed:** `week6-testing`
*(Attach screenshot of GitHub Actions green pass here)*

---

### Peer Review — Gap Analysis

| Reviewer | Reviewed Function | Gap Found |
|---|---|---|
| Perera G.S.H | `should_send_emotion_alert` | Emotion label with leading/trailing whitespace (e.g., `" SAD "`) |
| Kurera P.A.T | `classify_voice_command` | Unicode or emoji input handling |
| Bandara K.N.K.L.N | `validate_reminder` | Year limit (e.g., 9999) |
| Manabandu J.P.G.T.R | `should_hide_notification` | Float precision edge cases |

---

## Summary

| Task | Status |
|---|---|
| Selected 4 testable functions | ✅ |
| Applied equivalence partitioning | ✅ |
| Applied boundary value analysis | ✅ |
| Documented error/negative cases | ✅ |
| Wrote 44 automated unit tests | ✅ |
| All tests passing locally | ✅ (44/44) |
| GitHub Actions CI workflow added | ✅ |
| Pushed to `week6-testing` branch | ✅ |
| Peer review completed | ✅ |
