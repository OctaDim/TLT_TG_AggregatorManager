import qrcode
from PIL import Image

from configs.enums import QR_CODE_ERROR_CORRECTION


def save_qrcode_to_disk(
        qr_code_url: str,
        full_file_path: str,
        qrcode_image_size: int = None
) -> str | None:
    try:
        print("Generating QR code in console:")
        qr_code_obj = qrcode.main.QRCode(
            version=None,
            error_correction=QR_CODE_ERROR_CORRECTION.LEVEL_M.value,
            box_size=10,
            border=4,
            image_factory=None,
            mask_pattern=None, )
        qr_code_obj.add_data(qr_code_url, optimize=20)
        qr_code_obj.make(fit=True)
        qr_code_image = qr_code_obj.make_image(fill_color="blue",
                                               back_color="white")

        if qrcode_image_size:
            qr_code_image = qr_code_image.resize(
                (qrcode_image_size, qrcode_image_size),
                Image.Resampling.LANCZOS)
        qr_code_image.save(stream=full_file_path, kind="PNG")
        return full_file_path
    except Exception as error:
        print(f"Saving QR Code image to file [ERROR]:\n"
              f"error: {error}\n"
              f"qr_code_url: {qr_code_url}\n"
              f"full_file_path: {full_file_path}\n"
              f"qrcode_image_size: {qrcode_image_size}\n")
        return None
