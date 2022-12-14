from pathlib import Path
import unittest
from Bio import SeqIO
from flams.input import parse_args, retrieve_protein_from_uniprot

from flams.input import create_args_parser


TEST_INPUT = Path(__file__).parent / "testfiles/sequence.fasta"
TEST_OUTPUT = Path(__file__).parent / "testfiles/out.csv"

DATA_PATH = Path(__file__).parents[1] / "data"



class ParserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = create_args_parser()

    def test_simple(self):
        self.parser.parse_args(["--in", "file.fasta", "2"])
        self.parser.parse_args(
            ["--id", "P57703", "2", "--range", "3", "-o", "file.out", "-t", "3"]
        )

    def test_fasta_or_id_required(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["2"])

    def test_fasta_id_mutually_exclusive(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["--in", "file.fasta", "--id", "P57703", "2"])

    def test_position_is_int(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["--in", "file.fa", "2.5"])

        with self.assertRaises(SystemExit):
            self.parser.parse_args(["--in", "file.fa", "abc"])

    def test_range_is_int(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["--in", "file.fa", "2", "--range", "2.5"])

        with self.assertRaises(SystemExit):
            self.parser.parse_args(["--in", "file.fa", "2", "--range", "abc"])


class ParseArgsTestCase(unittest.TestCase):
    def test_simple(self):
        parse_args(["--in", str(TEST_INPUT), "11", "--out", str(TEST_OUTPUT)])
        parse_args(["--id", "P57703", "19", "--range", "3", "-o", "file.out", "-t", "3"])

    def test_checks_input_exists(self):
        with self.assertRaises(SystemExit):
            parse_args(["--in", "file.fa", "11"])

        with self.assertRaises(SystemExit):
            parse_args(["--id", "hahahah", "11"])

    def test_checks_input_fasta(self):
        with self.assertRaises(SystemExit):
            directory = str(TEST_INPUT.parent)
            parse_args(["--in", directory, "2"])

    def test_checks_output_valid_path(self):
        non_existing_path = TEST_OUTPUT.parent / "void_dir" / "out.tsv"
        with self.assertRaises(TypeError):
            parse_args(["--in", str(TEST_INPUT), "2", "--out", non_existing_path])

    def test_check_output_writable(self):
        directory = str(TEST_OUTPUT.parent)
        with self.assertRaises(SystemExit):
            parse_args(["--in", str(TEST_INPUT), "2", "--out", directory])

    def test_checks_lysine_valid(self):
        with self.assertRaises(SystemExit):
            parse_args(["--in", str(TEST_INPUT), "2", "--out", str(TEST_OUTPUT)])
        
        with self.assertRaises(SystemExit):
            parse_args(["--id", "P57703", "18", "--out", str(TEST_OUTPUT)])


class GetProteinTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        for file in DATA_PATH.glob("*.tmp"):
            file.unlink()

    def test_retrieve_from_uniprot(self):
        # given
        protein_id = "P57703"
        expected_filename = DATA_PATH / f"{protein_id}.fasta.tmp"
        self.assertFalse(expected_filename.exists())

        # when
        filename = retrieve_protein_from_uniprot("P57703")

        # then
        self.assertEqual(filename, expected_filename)
        self.assertTrue(expected_filename.exists())
        with filename.open() as f:
            seq = SeqIO.read(f, "fasta")
        self.assertEqual(seq.id, "sp|P57703|METE_PSEAE")
