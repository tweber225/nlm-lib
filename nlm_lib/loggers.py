from typing import Optional
from pathlib import Path
import re

from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np

from dirigo import units
from dirigo.sw_interfaces.worker import EndOfStream
from dirigo.sw_interfaces.display import Display, DisplayProduct
from dirigo.sw_interfaces import Logger
from dirigo.plugins.acquisitions import FrameAcquisition




class PngLogger(Logger):

    def __init__(self,
                 upstream: Display,
                 skip_frames: int,
                 rotate: units.Angle = units.Angle('0 deg'),
                 **kwargs):
        super().__init__(upstream, **kwargs) # type: ignore
        self._acquisition: FrameAcquisition

        self._skip_frames = skip_frames
        self._rotate = rotate

        self._frames_received = 0

    def _receive_product(self) ->  DisplayProduct:
        return super()._receive_product(self) # type: ignore

    def run(self):
        try:
            while self._frames_received < self._skip_frames:
                with self._receive_product():
                    self._frames_received += 1

            with self._receive_product() as product:
                self.save_data(product)

        except EndOfStream:
            self._publish(None)


    def save_data(self, product: DisplayProduct):
        img = product.data.copy()
        img = np.rot90(img, k = self._rotate_k, axes=(0,1))
        
        height, width = img.shape[:2]
        bgrx_bytes = img.tobytes(order='C')   # bytes-like object, len == width * height * 4

        img = Image.frombuffer("RGB",          # output mode: R-G-B, 3 bytes/pixel
                              (width, height),
                              bgrx_bytes,
                              "raw",           # use the raw decoder
                              "BGRX",          # how the *input* is organised
                              0, 1)            # stride 0 = tightly packed, 1 = top-to-bottom

        img.save(fp = self._file_path(),
                 pnginfo=self._meta,
                 dpi=(self._dpi, self._dpi))
        
        print("Saved frame")

    @property
    def _rotate_k(self) -> int:
        return round(self._rotate / units.Angle("90 deg"))

    @property
    def _meta(self):
        meta = PngInfo()
        if hasattr(self._acquisition.spec, 'pixel_size'):
            pixel_size = float(self._acquisition.spec.pixel_size)
            meta.add_itxt("PixelSizeX", str(pixel_size), lang="", tkey="MICROMETERS")
            meta.add_itxt("PixelSizeY", str(pixel_size), lang="", tkey="MICROMETERS")
        # stage position
        # digital gain levels
        # channel labels
        # Image description
        # software versions: dirigo, mph_acquisition
        # hardware details?
        return meta
    
    @property
    def _dpi(self) -> float:
        return 1/1
    
    def _file_path(self, image_index: Optional[int] = None) -> Path:
        """
        Build a PNG output path that never overwrites an existing file.

        If ``image_index`` is None, scan ``self.save_path`` for files that already
        match ``f"{self.basename}_<n>.png"`` and return the next free index.
        If ``image_index`` is given, raise ``FileExistsError`` if that specific
        file already exists.
        """
        # Regex that captures the numeric suffix of files like "<basename>_123.png"
        pattern = re.compile(rf"{re.escape(self.basename)}_(\d+)\.png$")

        if image_index is None:
            # Collect any numeric suffixes on existing files
            existing = [
                int(m.group(1))
                for p in self.save_path.glob(f"{self.basename}_*.png")
                if (m := pattern.match(p.name))
            ]

            next_index = (max(existing) + 1) if existing else 0
            proposed_file_path = self.save_path / f"{self.basename}_{next_index}.png"

        else:
            # check that we won't overwrite something
            proposed_file_path = self.save_path / f"{self.basename}_{image_index}.png"
            if proposed_file_path.exists():
                raise FileExistsError(f"File already exists: {proposed_file_path}")

        return proposed_file_path