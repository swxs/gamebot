"""客户区图像上的 Windows.Media.Ocr。找不到字时返回空结果。"""

from typing import Optional

import numpy as np

from gamebot.protocols.types import OcrHit, Rect


def recognize_win(image: np.ndarray) -> list[OcrHit]:
    import asyncio

    import cv2
    from winsdk.windows.graphics.imaging import BitmapDecoder
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.storage.streams import DataWriter, InMemoryRandomAccessStream

    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        return []
    payload = bytes(encoded)

    async def _run():
        stream = InMemoryRandomAccessStream()
        writer = DataWriter(stream)
        writer.write_bytes(list(payload))
        await writer.store_async()
        await writer.flush_async()
        stream.seek(0)
        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        engine = OcrEngine.try_create_from_user_profile_languages()
        if engine is None:
            return []
        result = await engine.recognize_async(bitmap)
        hits = []
        for line in result.lines:
            for word in line.words:
                box = word.bounding_rect
                hits.append(
                    OcrHit(
                        text=word.text,
                        rect=Rect(int(box.x), int(box.y), int(box.width), int(box.height)),
                    )
                )
        return hits

    return asyncio.run(_run())


class Win32OcrHandler:
    def __init__(self, recognize=None):
        self._recognize = recognize or recognize_win

    def read(self, image: np.ndarray) -> list[OcrHit]:
        return list(self._recognize(image))

    def find_text(self, image: np.ndarray, text: str) -> Optional[OcrHit]:
        for hit in self.read(image):
            if text in hit.text:
                return hit
        return None
