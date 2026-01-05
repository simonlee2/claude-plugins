#!/usr/bin/env python3
"""
Nanobanana Image Generation Script

Generates or edits images using Google's Nanobanana model via Replicate API.
Supports text-to-image generation, image-to-image transformation, and multi-image input.
"""

import argparse
import os
import sys
import time
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

try:
    import replicate
    from replicate.exceptions import ReplicateError
except ImportError:
    print("Error: replicate package not installed")
    print("Install it with: pip install replicate")
    sys.exit(1)

# Model configuration
MODEL_ID = "google/nano-banana"
POLLING_INTERVAL = 1  # seconds
TIMEOUT = 300  # seconds (5 minutes)

# Valid aspect ratios
VALID_ASPECT_RATIOS = [
    "match_input_image", "1:1", "2:3", "3:2", "3:4", "4:3",
    "4:5", "5:4", "9:16", "16:9", "21:9"
]

# Valid output formats
VALID_OUTPUT_FORMATS = ["jpg", "png"]


def validate_environment():
    """Validate that required environment variables are set."""
    # Check for either REPLICATE_API_KEY or REPLICATE_API_TOKEN
    api_key = os.environ.get("REPLICATE_API_KEY") or os.environ.get("REPLICATE_API_TOKEN")
    if not api_key:
        print("Error: REPLICATE_API_KEY or REPLICATE_API_TOKEN environment variable not set")
        print("Get an API key from: https://replicate.com/account/api-tokens")
        print("Then set it with: export REPLICATE_API_KEY='your-api-key'")
        print("Or: export REPLICATE_API_TOKEN='your-api-token'")
        sys.exit(1)
    return api_key


def is_url(path: str) -> bool:
    """Check if a path is a URL."""
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def upload_image_to_replicate(image_path: str, client: replicate.Client) -> str:
    """
    Upload an image to Replicate's file hosting.

    Args:
        image_path: Local file path or URL
        client: Replicate client instance

    Returns:
        Replicate-hosted image URL
    """
    try:
        print(f"  Uploading image: {image_path}")

        if is_url(image_path):
            # Download from URL and re-upload to Replicate
            import requests
            response = requests.get(image_path, timeout=30)
            response.raise_for_status()

            # Determine filename from URL
            filename = os.path.basename(urlparse(image_path).path) or "image"

            # Create file object
            from io import BytesIO
            content_type = response.headers.get("content-type", "application/octet-stream")
            file_data = BytesIO(response.content)
            file_data.name = filename

            # Upload to Replicate
            uploaded_file = client.files.create(file_data, metadata={"original_url": image_path})

        else:
            # Upload local file
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            with open(image_path, "rb") as f:
                uploaded_file = client.files.create(f)

        print(f"  ✓ Uploaded successfully")
        return uploaded_file.urls.get

    except Exception as e:
        print(f"  ✗ Upload failed: {e}")
        raise


def generate_image(
    prompt: str,
    image_inputs: Optional[List[str]] = None,
    aspect_ratio: str = "1:1",
    output_format: str = "jpg",
    output_path: Optional[str] = None,
) -> str:
    """
    Generate or edit an image using Nanobanana.

    Args:
        prompt: Text description of the desired image
        image_inputs: Optional list of input image paths or URLs
        aspect_ratio: Aspect ratio of the output image
        output_format: Output format (jpg or png)
        output_path: Path to save the generated image

    Returns:
        URL of the generated image
    """
    # Validate environment
    api_key = validate_environment()

    # Create Replicate client
    client = replicate.Client(api_token=api_key)

    # Prepare input parameters
    input_params = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": output_format,
    }

    # Upload input images if provided
    if image_inputs:
        print(f"Uploading {len(image_inputs)} input image(s)...")
        hosted_images = []
        for img in image_inputs:
            hosted_url = upload_image_to_replicate(img, client)
            hosted_images.append(hosted_url)
        input_params["image_input"] = hosted_images
        print()

    # Run the model
    print(f"Generating image with Nanobanana...")
    print(f"  Prompt: {prompt}")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"  Output format: {output_format}")
    if image_inputs:
        print(f"  Input images: {len(image_inputs)}")
    print()

    try:
        start_time = time.time()

        # Run prediction with polling
        print("  Starting prediction...")
        output = client.run(
            MODEL_ID,
            input=input_params,
        )

        elapsed_time = time.time() - start_time
        print(f"✓ Generation completed in {elapsed_time:.1f}s")

        # Extract image URL - Replicate returns a FileOutput object or string
        if isinstance(output, str):
            image_url = output
        elif hasattr(output, 'url') and callable(output.url):
            image_url = output.url()
        elif hasattr(output, 'url'):
            image_url = output.url
        else:
            # Try to get URL from dict-like object
            image_url = str(output)
        print(f"  Image URL: {image_url}")

        # Download and save if output path specified
        if output_path:
            print(f"\nDownloading image to: {output_path}")
            import requests
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✓ Image saved successfully")

        return image_url

    except ReplicateError as e:
        print(f"✗ Replicate API error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate or edit images using Google's Nanobanana model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic text-to-image
  python generate_image.py "a sunset over mountains" --output sunset.jpg

  # Image-to-image transformation
  python generate_image.py "make it look like a watercolor painting" \\
    --image-input photo.jpg --output watercolor.jpg

  # Multiple input images
  python generate_image.py "combine these styles" \\
    --image-input style1.jpg --image-input style2.jpg --output combined.jpg

  # Custom aspect ratio
  python generate_image.py "a wide landscape" \\
    --aspect-ratio 21:9 --output landscape.jpg

  # PNG output
  python generate_image.py "a logo design" \\
    --output-format png --output logo.png
        """
    )

    parser.add_argument(
        "prompt",
        help="Text description of the image to generate or transformation to apply"
    )

    parser.add_argument(
        "--image-input",
        action="append",
        dest="image_inputs",
        help="Input image path or URL (can be specified multiple times for multi-image input)"
    )

    parser.add_argument(
        "--aspect-ratio",
        choices=VALID_ASPECT_RATIOS,
        default="1:1",
        help="Aspect ratio of the output image (default: 1:1)"
    )

    parser.add_argument(
        "--output-format",
        choices=VALID_OUTPUT_FORMATS,
        default="jpg",
        help="Output format (default: jpg)"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Path to save the generated image (default: generated_image_<timestamp>.jpg)"
    )

    args = parser.parse_args()

    # Generate default output path if not specified
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"generated_image_{timestamp}.{args.output_format}"

    # Adjust aspect ratio default for image inputs
    if args.image_inputs and args.aspect_ratio == "1:1":
        args.aspect_ratio = "match_input_image"

    # Generate the image
    print("=" * 60)
    print("Nanobanana Image Generation")
    print("=" * 60)
    print()

    try:
        image_url = generate_image(
            prompt=args.prompt,
            image_inputs=args.image_inputs,
            aspect_ratio=args.aspect_ratio,
            output_format=args.output_format,
            output_path=args.output,
        )

        print()
        print("=" * 60)
        print("✓ Success!")
        print(f"Image URL: {image_url}")
        print(f"Saved to: {args.output}")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
