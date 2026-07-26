from pdf2image import convert_from_path
import os


def pdf_to_image(pdf_path):
    """
    Converts the first page of a PDF into a JPEG image
    and returns the image path.
    """

    # Create uploads folder if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    try:
        # Convert first page of PDF to image
        images = convert_from_path(
            pdf_path,
            first_page=1,
            last_page=1
        )

        output_image = os.path.join(
            "uploads",
            "temp_pdf_page.jpg"
        )

        # Save as JPEG
        images[0].save(output_image, "JPEG")

        return output_image

    except Exception as e:
        raise Exception(f"PDF Conversion Error: {str(e)}")