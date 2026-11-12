#!/usr/bin/env python3
"""Private, offline visual regression comparison for opt-in localhost screenshots.

Uses Pillow when installed. No screenshots or image pixels are included in output.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

MAX_BYTES = 16_000_000
MAX_PIXELS = 12_000_000
VIEWPORTS = ('mobile', 'desktop')


def open_image(path: Path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError('Screenshots must be regular files, <=16 MB, without symlinks')
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('Install optional image dependency: pip install Pillow') from exc
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    with Image.open(path) as source:
        if source.width * source.height > MAX_PIXELS:
            raise ValueError('Screenshots cannot exceed 12 megapixels')
        if source.format != 'PNG':
            raise ValueError('Only PNG screenshots are supported')
        image = source.convert('RGBA')
        background = Image.new('RGBA', image.size, 'white')
        background.alpha_composite(image)
        return background.convert('RGB')


def compare_pair(baseline: Path, candidate: Path, threshold: int = 15) -> dict:
    if type(threshold) is not int or not 1 <= threshold <= 255:
        raise ValueError('threshold must be 1..255')
    from PIL import ImageChops
    before = open_image(Path(baseline))
    after = open_image(Path(candidate))
    if before.size != after.size:
        return {'status': 'dimension_mismatch', 'baseline_size': list(before.size),
                'candidate_size': list(after.size), 'changed_percent': None, 'bounding_box': None}
    diff = ImageChops.difference(before, after)
    channels = diff.split()
    strongest = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    mask = strongest.point(lambda v: 255 if v >= threshold else 0)
    count = mask.histogram()[255]
    pixels = before.width * before.height
    bbox = mask.getbbox()
    return {'status': 'changed' if count else 'identical', 'size': list(before.size),
            'changed_pixels': count, 'total_pixels': pixels,
            'changed_percent': round(100 * count / pixels, 4) if pixels else 0,
            'bounding_box': list(bbox) if bbox else None}


def compare_directories(baseline: Path, candidate: Path, threshold: int = 15,
                        max_change_percent: float = 1.0) -> dict:
    if not 0 <= max_change_percent <= 100:
        raise ValueError('max_change_percent must be within 0..100')
    rows = {}
    failed = False
    for viewport in VIEWPORTS:
        filename = f'guardian-{viewport}.png'
        a = Path(baseline) / filename
        b = Path(candidate) / filename
        result = compare_pair(a, b, threshold)
        rows[viewport] = result
        if result['status'] == 'dimension_mismatch' or (result['changed_percent'] or 0) > max_change_percent:
            failed = True
    return {'tool': 'kattour-guardian-visual-regression', 'status': 'review_required' if failed else 'within_threshold',
            'pixel_channel_threshold': threshold, 'allowed_changed_percent_per_viewport': max_change_percent,
            'viewports': rows,
            'notice': 'Pixel differences detect changes, not whether the UI improved. Manual review required; screenshots stay local.'}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-dir', type=Path, required=True)
    parser.add_argument('--candidate-dir', type=Path, required=True)
    parser.add_argument('--pixel-threshold', type=int, default=15)
    parser.add_argument('--max-change-percent', type=float, default=1.0)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        result = compare_directories(args.baseline_dir, args.candidate_dir, args.pixel_threshold, args.max_change_percent)
        data = json.dumps(result, indent=2) + '\n'
        if args.output:
            args.output.write_text(data, encoding='utf-8')
        else:
            print(data, end='')
        return 1 if result['status'] == 'review_required' else 0
    except (OSError, ValueError, RuntimeError) as exc:
        print('Cannot compare screenshots: ' + type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
