#!/usr/bin/env python3
"""Compare equally sized UI captures without resizing or hiding alignment errors.

Requires Pillow. Keep captures and output containing account data outside git.
Masks are a JSON list of [left, top, width, height] rectangles.
"""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


def compare(reference, candidate, rectangles, threshold):
    if reference.size != candidate.size:
        raise ValueError(f"Image dimensions differ: {reference.size} vs {candidate.size}")
    width, height = reference.size
    mask = Image.new("L", reference.size)
    draw = ImageDraw.Draw(mask)
    for rectangle in rectangles:
        if (not isinstance(rectangle, list) or len(rectangle) != 4
                or any(type(value) is not int for value in rectangle)):
            raise ValueError("Each mask must be [left, top, width, height] in integer pixels")
        x, y, w, h = rectangle
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
            raise ValueError("Mask rectangle lies outside the image")
        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=255)

    difference = ImageChops.difference(reference, candidate)
    heat = bytearray(width * height * 3)
    compared = changed = total_error = maximum = 0
    # Bytes avoid allocating a second full set of RGB tuples for large captures.
    values, excluded = difference.tobytes(), mask.tobytes()
    for index, masked in enumerate(excluded):
        offset = index * 3
        if masked:
            heat[offset:offset + 3] = bytes((64, 64, 64))
            continue
        channels = values[offset:offset + 3]
        delta = max(channels)
        compared += 1
        changed += delta > threshold
        total_error += sum(channels)
        maximum = max(maximum, delta)
        heat[offset] = min(255, delta * 4)
    if compared == 0:
        raise ValueError("At least one unmasked pixel is required")
    report = {
        "width": width, "height": height, "threshold": threshold,
        "compared_pixels": compared, "masked_pixels": width * height - compared,
        "different_pixels": changed,
        "different_percent": round(100 * changed / compared, 6),
        "mean_absolute_error": round(total_error / (compared * 3), 6),
        "max_channel_difference": maximum,
        "mask_rectangles": rectangles,
        "note": "Raw RGB comparison; font rasterization and dynamic state may differ. "
                "Gray difference regions are masked. This is not a fidelity pass/fail score.",
    }
    return report, Image.blend(reference, candidate, 0.5), Image.frombytes("RGB", reference.size, bytes(heat))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mask", type=Path)
    parser.add_argument("--threshold", type=int, default=16,
                        help="A pixel differs when any RGB channel differs by more than this (default: 16)")
    args = parser.parse_args()
    try:
        if not 0 <= args.threshold <= 255:
            raise ValueError("Threshold must be between 0 and 255")
        rectangles = json.loads(args.mask.read_text()) if args.mask else []
        if not isinstance(rectangles, list):
            raise ValueError("Mask file must contain a list of rectangles")
        inputs = {path.resolve() for path in (args.reference, args.candidate, args.mask) if path}
        outputs = {args.output / name for name in ("overlay.png", "difference.png", "report.json")}
        if any(path.resolve() in inputs for path in outputs):
            raise ValueError("Output would overwrite an input file")
        with Image.open(args.reference) as first, Image.open(args.candidate) as second:
            report, overlay, difference = compare(first.convert("RGB"), second.convert("RGB"),
                                                   rectangles, args.threshold)
        args.output.mkdir(parents=True, exist_ok=True)
        overlay.save(args.output / "overlay.png")
        difference.save(args.output / "difference.png")
        report["reference"] = args.reference.name
        report["candidate"] = args.candidate.name
        (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
