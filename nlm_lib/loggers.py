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
                 skip_frames: int = 0,
                 rotate: units.Angle = units.Angle('0 deg'),
                 **kwargs):
        super().__init__(upstream, **kwargs) # type: ignore
        self._acquisition: FrameAcquisition

        self.file_ext = "png"

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

        finally:
            if self._processor is not None:
                # Remove self as subscriber to upstream processor (can be a Display)
                self._processor.remove_subscriber(self)

    def save_data(self, product: DisplayProduct):
        img = product.data.copy()
        img = np.rot90(img, 
                       k    = -self._rotate_k,    # Negative to match CW rotation used by Qt
                       axes = (0,1))
        
        height, width = img.shape[:2]
        bgrx_bytes = img.tobytes(order='C')   # bytes-like object, len == width * height * 4

        img = Image.frombuffer("RGB",          # output mode: R-G-B, 3 bytes/pixel
                              (width, height),
                              bgrx_bytes,
                              "raw",           # use the raw decoder
                              "BGRX",          # how the *input* is organised
                              0, 1)            # stride 0 = tightly packed, 1 = top-to-bottom
        fp = self._file_path()
        img.save(fp = fp,
                 pnginfo=self._meta,
                 dpi=(self._dpi, self._dpi))
        self.last_saved_file_path = fp

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
        return 1/1 # TODO fix this
    