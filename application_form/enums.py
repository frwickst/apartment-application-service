from enum import Enum


class ApplicationState(str, Enum):
    SUBMITTED = "submitted"
    RESERVED = "reserved"


class ApplicationType(str, Enum):
    HITAS = "hitas"
    PUOLIHITAS = "puolihitas"
    HASO = "haso"
