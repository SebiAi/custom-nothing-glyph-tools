#!/usr/bin/env python3
import json
import os
import sys

# LED mappings from docs/9_Technical Details.md
PHONE4APRO_VISIBLE_LEDS = []
for start, end in [
    (4, 8),
    (15, 23),
    (27, 37),
    (40, 50),
    (52, 116),
    (118, 128),
    (131, 141),
    (145, 153),
    (160, 164)
]:
    PHONE4APRO_VISIBLE_LEDS.extend(range(start, end + 1))

def map_visible_to_matrix(visible_vals):
    matrix = [0] * 169
    for i, val in enumerate(visible_vals):
        if i < len(PHONE4APRO_VISIBLE_LEDS):
            scaled = int(val * 4095.0 / 255.0)
            scaled = max(0, min(4095, scaled))
            matrix[PHONE4APRO_VISIBLE_LEDS[i]] = scaled
    return matrix

def matrix_to_csv_string(matrix):
    return ",".join(map(str, matrix)) + ","

def main():
    json_path = "glyph_data_4_frame_test.json"
    nglyph_expected_path = "glyph_animation_4_frame_test.nglyph"
    
    if not os.path.exists(json_path) or not os.path.exists(nglyph_expected_path):
        print("Missing test files in current directory.")
        return 1

    with open(json_path, 'r') as f:
        data = json.load(f)
        
    with open(nglyph_expected_path, 'r') as f:
        expected = json.load(f)
        
    frames = data['frames']
    num_input_frames = len(frames)
    total_output_frames = 26 # As in example
    
    # Distribute 26 frames over 4 input frames equally
    base_frames = total_output_frames // num_input_frames
    remainder = total_output_frames % num_input_frames
    allocated_counts = []
    for k in range(num_input_frames):
        allocated_counts.append(base_frames + (1 if k < remainder else 0))
        
    interpolated_pixel_frames = []
    for k, count in enumerate(allocated_counts):
        p_data = frames[k]['p']
        for _ in range(count):
            interpolated_pixel_frames.append(list(p_data))
            
    generated_author = []
    for pixel_frame in interpolated_pixel_frames:
        matrix = map_visible_to_matrix(pixel_frame)
        csv_str = matrix_to_csv_string(matrix)
        generated_author.append(csv_str)
        
    # Compare
    print(f"Comparing generated nglyph with {nglyph_expected_path}...")
    errors = 0
    
    if expected['VERSION'] != 1:
        print(f"Version mismatch: expected 1, got {expected['VERSION']}")
        errors += 1
    if expected['PHONE_MODEL'] != 'PHONE4APRO':
        print(f"Phone model mismatch: expected PHONE4APRO, got {expected['PHONE_MODEL']}")
        errors += 1
    if expected['CUSTOM1'] != '':
        print(f"CUSTOM1 mismatch: expected '', got {expected['CUSTOM1']}")
        errors += 1
        
    expected_author = expected['AUTHOR']
    if len(expected_author) != len(generated_author):
        print(f"Frame count mismatch: expected {len(expected_author)}, got {len(generated_author)}")
        errors += 1
        
    for idx, (exp, gen) in enumerate(zip(expected_author, generated_author)):
        if exp != gen:
            print(f"Frame {idx} mismatch!")
            # Find differing values
            exp_vals = exp.strip().split(',')
            gen_vals = gen.strip().split(',')
            diffs = []
            for pixel_idx, (ev, gv) in enumerate(zip(exp_vals, gen_vals)):
                if ev != gv:
                    diffs.append((pixel_idx, ev, gv))
            print(f"  First 5 differences: {diffs[:5]}")
            errors += 1
            
    if errors == 0:
        print("Verification SUCCESS! The generated NGLYPH data matches the expected test file exactly.")
    else:
        print(f"Verification FAILED with {errors} errors.")
        
if __name__ == '__main__':
    sys.exit(main())
