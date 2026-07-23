import argparse
import csv
import io
import json
import wave
from pathlib import Path

import numpy as np


DUR_BEATS = {
    "whole": 4.0,
    "half": 2.0,
    "quarter": 1.0,
    "eighth": 0.5,
    "sixteenth": 0.25,
}


SEMITONE_MAP = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


VALID_DURATIONS = set(DUR_BEATS.keys())


def normalize_note_entry(pitch: str, duration: str):
    pitch = pitch.strip().upper()
    duration = duration.strip().lower()

    if len(pitch) < 2:
        raise ValueError(f"Invalid pitch '{pitch}'.")

    note_name = pitch[:-1]
    octave = pitch[-1]
    if note_name not in SEMITONE_MAP or not octave.isdigit():
        raise ValueError(f"Invalid pitch '{pitch}'. Use values like C4, D#4, A5.")

    if duration not in VALID_DURATIONS:
        allowed = ", ".join(sorted(VALID_DURATIONS))
        raise ValueError(f"Invalid duration '{duration}'. Allowed: {allowed}")

    return {"pitch": pitch, "duration": duration}


def pitch_to_frequency(pitch: str) -> float:
    """
    예:
    C4 -> 261.63Hz
    A4 -> 440Hz
    """
    note = pitch[:-1]
    octave = int(pitch[-1])
    semitone_distance_from_a4 = SEMITONE_MAP[note] + (octave - 4) * 12 - 9
    return 440.0 * (2 ** (semitone_distance_from_a4 / 12))


def synthesize_note(freq, duration_sec, sr=44100):
    """
    단일 음 생성
    사인파 + 약한 배음으로 부드러운 학습용 소리 생성
    """
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    waveform = (
        0.65 * np.sin(2 * np.pi * freq * t)
        + 0.20 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.08 * np.sin(2 * np.pi * freq * 3 * t)
    )

    # 클릭 노이즈 방지용 envelope
    envelope = np.ones_like(waveform)
    attack = int(sr * 0.01)
    release = int(sr * 0.03)
    if attack > 0:
        envelope[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        envelope[-release:] = np.linspace(1, 0, release)

    waveform = waveform * envelope
    return waveform


def synthesize_score(notes, tempo=90, sr=44100):
    """
    notes = [{"pitch":"C4", "duration":"quarter"}, ...]
    전체 악보를 하나의 WAV 바이트로 반환
    """
    sec_per_beat = 60.0 / tempo
    parts = []

    for note in notes:
        beats = DUR_BEATS[note["duration"]]
        duration_sec = beats * sec_per_beat
        freq = pitch_to_frequency(note["pitch"])
        parts.append(synthesize_note(freq, duration_sec, sr=sr))

    if not parts:
        return None

    audio = np.concatenate(parts)

    # 볼륨 정규화
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    audio_int16 = np.int16(audio * 32767)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

    return buffer.getvalue()


def save_score_wav(notes, output_path="demo_score.wav", tempo=90, sr=44100):
    """
    notes를 합성해 실제 WAV 파일로 저장한다.
    반환값: 저장된 파일 경로(Path) 또는 None(노트 없음)
    """
    wav_bytes = synthesize_score(notes, tempo=tempo, sr=sr)
    if not wav_bytes:
        return None

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(wav_bytes)
    return path


def parse_notes_arg(notes_arg: str):
    """
    CLI notes 문자열을 내부 notes 포맷으로 변환한다.
    형식: "C4:quarter,D4:half,E4:eighth"
    """
    notes = []
    raw_items = [item.strip() for item in notes_arg.split(",") if item.strip()]
    if not raw_items:
        raise ValueError("--notes is empty. Example: C4:quarter,D4:quarter")

    for item in raw_items:
        if ":" not in item:
            raise ValueError(
                f"Invalid note token '{item}'. Use pitch:duration format, e.g. C4:quarter"
            )

        pitch, duration = [part.strip() for part in item.split(":", 1)]
        notes.append(normalize_note_entry(pitch, duration))

    return notes


def parse_notes_file(notes_file: str):
    """
    JSON 또는 CSV 파일에서 notes를 로드한다.

    JSON 형식:
      [
        {"pitch": "C4", "duration": "quarter"},
        {"pitch": "D4", "duration": "half"}
      ]
    CSV 형식(헤더 필요):
      pitch,duration
      C4,quarter
      D4,half
    """
    path = Path(notes_file)
    if not path.exists():
        raise ValueError(f"Notes file not found: {path}")

    suffix = path.suffix.lower()
    notes = []

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON notes file must be a list of note objects.")

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"JSON item at index {idx} must be an object.")
            if "pitch" not in item or "duration" not in item:
                raise ValueError(
                    f"JSON item at index {idx} must include 'pitch' and 'duration'."
                )
            notes.append(normalize_note_entry(str(item["pitch"]), str(item["duration"])))

    elif suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as fp:
            reader = csv.DictReader(fp)
            if not reader.fieldnames:
                raise ValueError("CSV notes file must include headers: pitch,duration")
            missing = {"pitch", "duration"} - set(reader.fieldnames)
            if missing:
                raise ValueError("CSV notes file must include headers: pitch,duration")

            for idx, row in enumerate(reader, start=2):
                pitch = row.get("pitch")
                duration = row.get("duration")
                if pitch is None or duration is None:
                    raise ValueError(f"CSV row {idx} must include pitch and duration.")
                notes.append(normalize_note_entry(pitch, duration))
    else:
        raise ValueError("Unsupported notes file type. Use .json or .csv")

    if not notes:
        raise ValueError("Notes file is empty.")

    return notes


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="악보 노트를 합성해 WAV 파일로 저장합니다."
    )
    parser.add_argument(
        "--notes",
        default=None,
        help="노트 목록. 형식: C4:quarter,D4:half,E4:eighth",
    )
    parser.add_argument(
        "--notes_file",
        default=None,
        help="노트 파일 경로(.json 또는 .csv). --notes보다 우선 적용",
    )
    parser.add_argument(
        "--tempo",
        type=float,
        default=90,
        help="템포(BPM). 예: 90",
    )
    parser.add_argument(
        "--output_path",
        default="demo_score.wav",
        help="출력 WAV 파일 경로",
    )
    parser.add_argument(
        "--sample_rate",
        type=int,
        default=44100,
        help="샘플레이트(Hz). 기본값: 44100",
    )
    return parser


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        if args.notes_file:
            notes = parse_notes_file(args.notes_file)
        elif args.notes:
            notes = parse_notes_arg(args.notes)
        else:
            notes = parse_notes_arg("C4:quarter,D4:quarter,E4:quarter,F4:quarter")
    except ValueError as err:
        raise SystemExit(f"Input error: {err}")

    if args.tempo <= 0:
        raise SystemExit("Input error: --tempo must be greater than 0")
    if args.sample_rate <= 0:
        raise SystemExit("Input error: --sample_rate must be greater than 0")

    saved_path = save_score_wav(
        notes,
        output_path=args.output_path,
        tempo=args.tempo,
        sr=args.sample_rate,
    )

    if saved_path is None:
        print("No notes to synthesize.")
    else:
        print(f"Saved WAV file: {saved_path.resolve()}")