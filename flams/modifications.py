from dataclasses import dataclass
from enum import Enum
from typing import Any, List

from flams.databases import cplmv4


class Modification(str, Enum):
    descriptor: str

    def __new__(cls, name: str, descriptor: str = "") -> "Modification":
        # override to set additional property
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj.descriptor = descriptor
        return obj

    ACE = ("acetylation", "Acetylation")
    LAC = ("lactylation", "Lactylation")
    FOR = ("formylation", "Formylation")
    SUC = ("succinylation", "Succinylation")
    HMG = ("hmgylation", "HMGylation")


@dataclass
class ModificationDatabase:
    module: Any
    descriptor: str


@dataclass
class ModificationType:
    type: Modification
    version: float
    dbs: List[ModificationDatabase]


# Here we store a dict of modifications that can be queried for.
# Each modification has a dbs and version attribute.
# Dbs is a list of tuples (module, label) where module is used to get a FASTA of the modifications using label
# TODO Add more modifications from CPLM
MODIFICATIONS = {
    Modification.ACE: ModificationType(
        Modification.ACE.value,
        1.0,
        [ModificationDatabase(cplmv4, Modification.ACE.descriptor)],
    ),
    Modification.LAC: ModificationType(
        Modification.LAC.value,
        1.0,
        [ModificationDatabase(cplmv4, Modification.LAC.descriptor)],
    ),
    Modification.FOR: ModificationType(
        Modification.FOR.value,
        1.0,
        [ModificationDatabase(cplmv4, Modification.FOR.descriptor)],
    ),
    Modification.SUC: ModificationType(
        Modification.SUC.value,
        1.0,
        [ModificationDatabase(cplmv4, Modification.SUC.descriptor)],
    ),
    Modification.HMG: ModificationType(
        Modification.HMG.value,
        1.0,
        [ModificationDatabase(cplmv4, Modification.HMG.descriptor)],
    ),
}
