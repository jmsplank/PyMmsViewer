from enum import Enum


class INSTRUMENT(str, Enum):
    FGM = "fgm"
    FPI = "fpi"


class DRATE(str, Enum):
    FAST = "fast"
    SURVEY = "srvy"
