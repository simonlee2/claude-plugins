#!/usr/bin/env python3
"""
Seedance Video Generation Script

Generate videos using ByteDance's Seedance 1.5 Pro model via Replicate API.
Supports text-to-video, image-to-video, and audio-synchronized generation.
"""

import argparse
import os
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import replicate
except ImportError:
    print("Error: replicate package not installed.")
    print("Install with: pip install replicate")
    sys.exit(1)


MODEL_ID = "bytedance/seedance-1.5-pro"

VALID_ASPECT_RATIOS = ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "9:21"]


def upload_image_to_replicate(image_path: str) -> str:
    """Upload a local image file to Replicate's file hosting."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    print(f"Uploading image: {path.name}...")

    with open(path, "rb") as f:
        file_output = replicate.files.create(f, filename=path.name)

    print(f"Image uploaded successfully")
    return file_output.urls["get"]


def get_image_input(image_arg: str) -> str:
    """Process image argument - upload if local file, return URL if already URL."""
    if image_arg.startswith(("http://", "https://")):
        return image_arg
    return upload_image_to_replicate(image_arg)


def generate_video(
    prompt: str,
    duration: int = 5,
    aspect_ratio: str = "16:9",
    image: str = None,
    last_frame_image: str = None,
    camera_fixed: bool = False,
    generate_audio: bool = True,
    seed: int = None,
) -> str:
    """
    Generate a video using Seedance 1.5 Pro.

    Args:
        prompt: Scene description
        duration: Video length in seconds (2-12)
        aspect_ratio: Output aspect ratio
        image: Optional input image for image-to-video
        last_frame_image: Optional target end frame
        camera_fixed: Lock camera position
        generate_audio: Include synchronized audio
        seed: Random seed for reproducibility

    Returns:
        URL of the generated video
    """
    # Validate parameters
    if duration < 2 or duration > 12:
        raise ValueError(f"Duration must be between 2 and 12 seconds, got {duration}")

    if aspect_ratio not in VALID_ASPECT_RATIOS:
        raise ValueError(
            f"Invalid aspect ratio: {aspect_ratio}. "
            f"Valid options: {', '.join(VALID_ASPECT_RATIOS)}"
        )

    # Build input parameters
    input_params = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "generate_audio": generate_audio,
    }

    if camera_fixed:
        input_params["camera_fixed"] = True

    if seed is not None:
        input_params["seed"] = seed

    # Handle image inputs
    if image:
        input_params["image"] = get_image_input(image)

    if last_frame_image:
        input_params["last_frame_image"] = get_image_input(last_frame_image)

    print(f"\nGenerating video...")
    print(f"  Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print(f"  Duration: {duration}s")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"  Audio: {'enabled' if generate_audio else 'disabled'}")
    print(f"  Camera: {'fixed' if camera_fixed else 'dynamic'}")
    if image:
        print(f"  Input image: provided")
    print()

    # Run the model
    start_time = time.time()

    output = replicate.run(MODEL_ID, input=input_params)

    elapsed = time.time() - start_time
    print(f"\nGeneration completed in {elapsed:.1f} seconds")

    return output


def download_video(url: str, output_path: str) -> str:
    """Download video from URL to local file."""
    print(f"Downloading video to: {output_path}")

    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    urllib.request.urlretrieve(url, output_path)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Downloaded: {file_size:.2f} MB")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using Seedance 1.5 Pro via Replicate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic text-to-video
  %(prog)s "a sunset over mountains" --output sunset.mp4

  # Vertical video for TikTok
  %(prog)s "trendy dance moves" --aspect-ratio 9:16 --output dance.mp4

  # Image-to-video
  %(prog)s "gentle motion" --image portrait.jpg --output animated.mp4

  # Longer video with fixed camera
  %(prog)s "person talking" --duration 10 --camera-fixed --output talking.mp4

  # Silent video (no audio)
  %(prog)s "abstract visuals" --no-audio --output silent.mp4
        """,
    )

    parser.add_argument("prompt", help="Scene description for video generation")

    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: generated_video_TIMESTAMP.mp4)",
    )

    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=5,
        choices=range(2, 13),
        metavar="2-12",
        help="Video duration in seconds (default: 5)",
    )

    parser.add_argument(
        "--aspect-ratio",
        "-a",
        default="16:9",
        choices=VALID_ASPECT_RATIOS,
        help="Output aspect ratio (default: 16:9)",
    )

    parser.add_argument(
        "--image",
        "-i",
        help="Input image for image-to-video (local path or URL)",
    )

    parser.add_argument(
        "--last-frame",
        help="Target end frame image (local path or URL)",
    )

    parser.add_argument(
        "--camera-fixed",
        action="store_true",
        help="Lock camera position (no movement)",
    )

    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio generation",
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible results",
    )

    args = parser.parse_args()

    # Check for API key
    if not os.environ.get("REPLICATE_API_KEY"):
        print("Error: REPLICATE_API_KEY environment variable not set.")
        print("\nTo set it:")
        print("  export REPLICATE_API_KEY='your-api-key-here'")
        print("\nGet your API key at: https://replicate.com/account/api-tokens")
        sys.exit(1)

    # Generate default output filename if not specified
    output_path = args.output
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"generated_video_{timestamp}.mp4"

    # Ensure .mp4 extension
    if not output_path.lower().endswith(".mp4"):
        output_path += ".mp4"

    try:
        # Generate video
        video_url = generate_video(
            prompt=args.prompt,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio,
            image=args.image,
            last_frame_image=args.last_frame,
            camera_fixed=args.camera_fixed,
            generate_audio=not args.no_audio,
            seed=args.seed,
        )

        # Download to local file
        download_video(video_url, output_path)

        print(f"\n✓ Video saved to: {output_path}")

    except replicate.exceptions.ReplicateError as e:
        print(f"\nReplicate API error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\nInvalid parameter: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled.")
        sys.exit(130)


if __name__ == "__main__":
    main()
