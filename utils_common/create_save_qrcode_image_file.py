from typing import Union, Literal

import qrcode
from PIL import Image

from configs.enums import QR_CODE_ERROR_CORRECTION


def save_qrcode_image(
        qr_code_url: str,
        full_file_path: str,
        qrcode_image_size: int = None,
        qrcode_fill_color: Union[str, Literal["black", "#26282E"]] = "#26282E",
        qrcode_back_color: Union[str, Literal["white", "#FFFFFF"]] = "#FFFFFF"

) -> str | None:
    try:
        print("Generating QR code image:")
        qr_code_obj = qrcode.main.QRCode(
            version=None,
            error_correction=QR_CODE_ERROR_CORRECTION.LEVEL_M.value,
            box_size=10,
            border=4,
            image_factory=None,
            mask_pattern=None, )
        qr_code_obj.add_data(qr_code_url, optimize=20)
        qr_code_obj.make(fit=True)
        qr_code_image = qr_code_obj.make_image(fill_color=qrcode_fill_color,
                                               back_color=qrcode_back_color)
        if qrcode_image_size:
            print("Resizing QR code image:")
            qr_code_image = qr_code_image.resize(
                (qrcode_image_size, qrcode_image_size),
                Image.Resampling.LANCZOS)
        print("Saving QR code image:")
        qr_code_image.save(full_file_path, kind="PNG")
        return full_file_path
    except Exception as error:
        print(f"Saving QR Code image to file [ERROR]:\n"
              f"error: {error}\n"
              f"qr_code_url: {qr_code_url}\n"
              f"full_file_path: {full_file_path}\n"
              f"qrcode_image_size: {qrcode_image_size}\n")
        return None
