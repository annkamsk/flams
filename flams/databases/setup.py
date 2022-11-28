from pathlib import Path
import subprocess
import os
from typing import List
from flams.modifications import MODIFICATIONS, ModificationType
from flams.utils import get_data_dir


def update_db_for_modifications(list_of_mods_to_check: List[str]):
    for m in list_of_mods_to_check:
        _generate_blastdb_if_not_up_to_date(MODIFICATIONS[m])


# Check if data dir contains a BLASTDB with name {modification}-{version}
# If not, download FASTAs and generate BLASTDB.
def _generate_blastdb_if_not_up_to_date(modification: ModificationType):
    data_dir = get_data_dir()

    BLASTDB_PATH = get_blastdb_name_for_modification(
        modification.type, modification.version
    )

    # If an up-to-date BLASTDB for the given modification already exists, do nothing.
    if Path(f"{data_dir}/{BLASTDB_PATH}.pdb").exists():
        return

    fasta_location = f"{data_dir}/{modification.type}.fasta"

    if os.path.exists(fasta_location):
        os.remove(fasta_location)

    _get_fasta_from_dbs(modification, fasta_location)

    # Generate local BLASTDB from FASTA in fasta_location
    _generate_blastdb(data_dir, modification)


def _get_fasta_from_dbs(modification: ModificationType, fasta_location):
    for db in modification.dbs:
        db.module.get_fasta(db.descriptor, fasta_location)


def _generate_blastdb(data_dir, modification: ModificationType):
    # Generate local BLASTDB
    try:
        # We presume that the FASTA is stored in a file {modification.type}.fasta inside the data_dir.
        # We will write the local BLASTDB to out_path
        out_db_name = get_blastdb_name_for_modification(
            modification.type, modification.version
        )
        subprocess.call(
            f'cd "{data_dir}" && makeblastdb -in {modification.type}.fasta -dbtype prot -input_type fasta -parse_seqids'
            f" -out {out_db_name}",
            shell=True,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "You need to install BLAST and include it in system PATH."
        ) from e


# Gets the name of the local BLASTDB for a given modification.
def get_blastdb_name_for_modification(modification: str, version=None):
    # If version was not specified, get the current
    if not version:
        version = MODIFICATIONS[modification].version

    return f"{modification}-{version}"
