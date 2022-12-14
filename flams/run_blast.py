from dataclasses import dataclass
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast.Record import Blast, Alignment
from Bio.Blast import NCBIXML
from flams.utils import get_data_dir
from pathlib import Path
import flams.databases.setup
import re
import os


def run_blast(
    input,
    modifications,
    lysine_pos,
    lysine_range=0,
    evalue=0.01,
    num_threads=1,
    **kwargs,
):
    # For each modification, run blast and flatten results to an array
    results = []
    for m in modifications:
        result = _run_blast(input, m, lysine_pos, lysine_range, evalue, num_threads)
        for r in result:
            results.append(r)
    return results


@dataclass
class ModificationHeader:
    plmd_id: str
    uniprot_id: str
    position: int
    modification: str
    species: str

    @staticmethod
    def parse(title: str) -> "ModificationHeader":
        # Parse modification from the alignment title of structure:
        # {PLMD id}|{Uniprot ID}|{modification position} {type of modification} [{species}]
        # Example: PLMD-7244|P25665|304 Acetylation [Escherichia coli (strain K12)]
        regex = (
            r"(?P<plmd_id>\S+)\|"
            r"(?P<uniprot_id>\S+)\|"
            r"(?P<position>\d+) (?P<modification>[A-Za-z]+) \[(?P<species>.+)\]"
        )
        vars = re.match(regex, title).groupdict()
        vars["position"] = int(vars["position"])
        return ModificationHeader(**vars)


def _run_blast(input, modification, lysine_pos, lysine_range, evalue, num_threads=1):
    # Get BLASTDB name for selected modification + get a temporary path for output
    BLASTDB = flams.databases.setup.get_blastdb_name_for_modification(modification)
    BLAST_OUT = "temp.xml"

    # Adjust working directory conditions and convert input file into absolute path
    input = _adjust_working_directory(input)

    # Run BLAST
    blast_exec = NcbiblastpCommandline(
        query=input,
        db=BLASTDB,
        evalue=evalue,
        outfmt=5,
        out=BLAST_OUT,
        num_threads=num_threads,
    )
    blast_exec()

    with open(BLAST_OUT) as handle:
        blast_records = list(NCBIXML.parse(handle))

    return [_filter_blast(i, lysine_pos, lysine_range, evalue) for i in blast_records]


def _adjust_working_directory(input: Path):
    """
    # BlastpCommandline does not like whitespaces in paths, which the database may contain on especially Mac OS.
    # Therefore, we will change our working directory to that of the data dir before running Blast.
    # Before doing this, we need to convert the relative path to the input file into an absolute path.
    :param input: relative path to query FASTA file
    :return: absolute path to query FASTA file
    """
    input = input.absolute()
    os.chdir(get_data_dir())
    return input


def _filter_blast(blast_record, lysine_pos, lysine_range, evalue) -> Blast:
    # Create new Blast Record where we append filtered matches.
    filtered = Blast()

    for a in blast_record.alignments:
        # Parse FASTA title where Posttranslational modification info is stored
        mod = ModificationHeader.parse(a.title)

        # Append matching High Scoring partners here, which will then be added to the 'filtered' BLAST frame
        filtered_hsps = []

        for hsp in a.hsps:
            if hsp.expect < evalue and does_hsp_match_query(
                mod, hsp, lysine_pos, lysine_range
            ):
                # WEE! we have a match.
                filtered_hsps.append(hsp)

        # If some HSPS matched, let's append that to the filtered BLAST frame for future processing.
        if filtered_hsps:
            new_alignment = Alignment()
            new_alignment.title = a.title
            new_alignment.hsps = filtered_hsps
            filtered.alignments.append(new_alignment)

    return filtered


def does_hsp_match_query(
    modification: ModificationHeader, hsp, query_pos, query_range
) -> bool:
    if not _is_modification_within_match(hsp, modification.position):
        return False

    if not _is_user_query_within_match(hsp, query_pos):
        return False

    return _is_modification_within_tolerated_range(
        hsp, modification.position, query_pos, query_range
    )


# Check 1. mod_pos must be within the match of the subject
def _is_modification_within_match(hsp, mod_pos) -> bool:
    return hsp.sbjct_start <= mod_pos <= hsp.sbjct_end


# Check 2. Our user queried position must be within the match of the query
def _is_user_query_within_match(hsp, query_pos) -> bool:
    return hsp.query_start <= query_pos <= hsp.query_end


# Check 3. Check if mod_pos is within range of low and high
def _is_modification_within_tolerated_range(hsp, mod_pos, query_pos, query_range):
    mod_pos, query_pos, limit_low, limit_high = _standardise_positions(
        hsp, mod_pos, query_pos, query_range
    )
    return limit_low <= mod_pos <= limit_high


def _standardise_positions(hsp, mod_pos, lysine_pos, lysine_range):
    # Standardise the position of the found modification to local alignment
    mod_pos = mod_pos - (hsp.sbjct_start - 1)

    # Standardise the position of the query to local alignment and set range
    query_pos = lysine_pos - (hsp.query_start - 1)
    limit_low = query_pos - lysine_range
    limit_high = query_pos + lysine_range

    return mod_pos, query_pos, limit_low, limit_high
