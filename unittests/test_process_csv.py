import pandas as pd
import pytest
from pandas.core.frame import DataFrame
from pandas.testing import assert_frame_equal

from ahb_diff.main import align_columns
from unittests.conftest import FormatVersions


class TestSingleColumnDataframes:
    """
    test cases for dataframes containing only a `Segmentname` column.
    """

    formatversions: FormatVersions

    @pytest.fixture(autouse=True)
    def setup(self, formatversions: FormatVersions) -> None:
        self.formatversions = formatversions

    def test_align_columns(self) -> None:
        previous_pruefid = pd.DataFrame({"Segmentname": ["1", "2", "3", "4", "5", "6", "9", "10"]})
        subsequent_pruefid = pd.DataFrame({"Segmentname": ["1", "2", "3", "5", "6", "7", "8", "9", "10"]})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "",
                    "",
                    "9",
                    "10",
                ],
                "Änderung": ["", "", "", "ENTFÄLLT", "", "", "NEU", "NEU", "", ""],
                "changed_entries": ["", "", "", "", "", "", "", "", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": [
                    "1",
                    "2",
                    "3",
                    "",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                ],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_empty_dataframes(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": []})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": []})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": pd.Series([], dtype="float64"),
                "Änderung": pd.Series([], dtype="float64"),
                "changed_entries": [],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": pd.Series([], dtype="float64"),
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_one_empty_dataframe(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "3"]})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": []})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "3"],
                "Änderung": ["ENTFÄLLT", "ENTFÄLLT", "ENTFÄLLT"],
                "changed_entries": ["", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["", "", ""],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_full_offset(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "3"]})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["4", "5", "6"]})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "3", "", "", ""],
                "Änderung": ["ENTFÄLLT", "ENTFÄLLT", "ENTFÄLLT", "NEU", "NEU", "NEU"],
                "changed_entries": ["", "", "", "", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["", "", "", "4", "5", "6"],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_duplicate_segments(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "2"]})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "4"]})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "2", ""],
                "Änderung": ["", "", "ENTFÄLLT", "NEU"],
                "changed_entries": ["", "", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["1", "2", "", "4"],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_repeating_segments(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "3", "3", "2"]})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "3", "4"]})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "3", "3", "2", ""],
                "Änderung": ["", "", "", "ENTFÄLLT", "ENTFÄLLT", "NEU"],
                "changed_entries": ["", "", "", "", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["1", "2", "3", "", "", "4"],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)


class TestMultiColumnDataFrames:
    """
    test cases for dataframes containing multiple columns in addition to `Segmentname`.
    """

    formatversions: FormatVersions

    @pytest.fixture(autouse=True)
    def setup(self, formatversions: FormatVersions) -> None:
        self.formatversions = formatversions

    def test_align_columns(self) -> None:
        previous_pruefid = pd.DataFrame(
            {
                "Segmentname": ["1", "2", "3", "4", "5", "6", "9", "10"],
                "Segmentgruppe": ["a", "b", "c", "", "e", "f", "g", "h"],
            }
        )
        subsequent_pruefid = pd.DataFrame(
            {
                "Segmentname": ["1", "2", "3", "5", "6", "7", "8", "9", "10"],
                "Segmentgruppe": ["a", "b", "d", "d", "d", "e", "f", "a", "b"],
            }
        )

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "",
                    "",
                    "9",
                    "10",
                ],
                f"Segmentgruppe_{self.formatversions.previous_formatversion}": [
                    "a",
                    "b",
                    "c",
                    "",
                    "e",
                    "f",
                    "",
                    "",
                    "g",
                    "h",
                ],
                "Änderung": [
                    "",
                    "",
                    "ÄNDERUNG",
                    "ENTFÄLLT",
                    "ÄNDERUNG",
                    "ÄNDERUNG",
                    "NEU",
                    "NEU",
                    "ÄNDERUNG",
                    "ÄNDERUNG",
                ],
                "changed_entries": [
                    "",
                    "",
                    "Segmentgruppe_FV2410|Segmentgruppe_FV2504",
                    "",
                    "Segmentgruppe_FV2410|Segmentgruppe_FV2504",
                    "Segmentgruppe_FV2410|Segmentgruppe_FV2504",
                    "",
                    "",
                    "Segmentgruppe_FV2410|Segmentgruppe_FV2504",
                    "Segmentgruppe_FV2410|Segmentgruppe_FV2504",
                ],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": [
                    "1",
                    "2",
                    "3",
                    "",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                ],
                f"Segmentgruppe_{self.formatversions.subsequent_formatversion}": [
                    "a",
                    "b",
                    "d",
                    "",
                    "d",
                    "d",
                    "e",
                    "f",
                    "a",
                    "b",
                ],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_empty_dataframes(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": [], "Segmentgruppe": []})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": [], "Segmentgruppe": []})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": [],
                f"Segmentgruppe_{self.formatversions.previous_formatversion}": [],
                "Änderung": [],
                "changed_entries": [],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": [],
                f"Segmentgruppe_{self.formatversions.subsequent_formatversion}": [],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_one_empty_dataframe(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "3"], "Segmentgruppe": ["a", "b", "c"]})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": [], "Segmentgruppe": []})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "3"],
                f"Segmentgruppe_{self.formatversions.previous_formatversion}": ["a", "b", "c"],
                "Änderung": ["ENTFÄLLT", "ENTFÄLLT", "ENTFÄLLT"],
                "changed_entries": ["", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["", "", ""],
                f"Segmentgruppe_{self.formatversions.subsequent_formatversion}": ["", "", ""],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_full_offset(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "3"], "Segmentgruppe": ["a", "b", "c"]})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["4", "5", "6"], "Segmentgruppe": ["d", "e", "f"]})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "3", "", "", ""],
                f"Segmentgruppe_{self.formatversions.previous_formatversion}": ["a", "b", "c", "", "", ""],
                "Änderung": ["ENTFÄLLT", "ENTFÄLLT", "ENTFÄLLT", "NEU", "NEU", "NEU"],
                "changed_entries": ["", "", "", "", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["", "", "", "4", "5", "6"],
                f"Segmentgruppe_{self.formatversions.subsequent_formatversion}": ["", "", "", "d", "e", "f"],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_duplicate_segments(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "2"], "Segmentgruppe": ["a", "b", "c"]})
        subsequent_pruefid: DataFrame = pd.DataFrame({"Segmentname": ["1", "2", "4"], "Segmentgruppe": ["a", "b", "d"]})

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "2", ""],
                f"Segmentgruppe_{self.formatversions.previous_formatversion}": ["a", "b", "c", ""],
                "Änderung": ["", "", "ENTFÄLLT", "NEU"],
                "changed_entries": ["", "", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["1", "2", "", "4"],
                f"Segmentgruppe_{self.formatversions.subsequent_formatversion}": ["a", "b", "", "d"],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_repeating_segments(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame(
            {"Segmentname": ["1", "2", "3", "3", "2"], "Segmentgruppe": ["a", "b", "c", "d", "e"]}
        )
        subsequent_pruefid: DataFrame = pd.DataFrame(
            {"Segmentname": ["1", "2", "3", "4"], "Segmentgruppe": ["a", "b", "c", "d"]}
        )

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", "3", "3", "2", ""],
                f"Segmentgruppe_{self.formatversions.previous_formatversion}": ["a", "b", "c", "d", "e", ""],
                "Änderung": ["", "", "", "ENTFÄLLT", "ENTFÄLLT", "NEU"],
                "changed_entries": ["", "", "", "", "", ""],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["1", "2", "3", "", "", "4"],
                f"Segmentgruppe_{self.formatversions.subsequent_formatversion}": ["a", "b", "c", "", "", "d"],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)

    def test_align_columns_different_column_sets(self) -> None:
        previous_pruefid: DataFrame = pd.DataFrame(
            {
                "Segmentname": ["1", "2"],
                "Segmentgruppe": ["a", "b"],
                "Datenelement": ["x", "y"],
                "Qualifier": ["XY", "YZ"],
            }
        )
        subsequent_pruefid: DataFrame = pd.DataFrame(
            {
                "Segmentname": ["2", "3"],
                "Segmentgruppe": ["b", "c"],
                "Datenelement": ["m", "n"],
                "Qualifier": ["XY", ""],
            }
        )

        expected_output: DataFrame = pd.DataFrame(
            {
                f"Segmentname_{self.formatversions.previous_formatversion}": ["1", "2", ""],
                f"Segmentgruppe_{self.formatversions.previous_formatversion}": ["a", "b", ""],
                f"Datenelement_{self.formatversions.previous_formatversion}": ["x", "y", ""],
                f"Qualifier_{self.formatversions.previous_formatversion}": ["XY", "YZ", ""],
                "Änderung": ["ENTFÄLLT", "ÄNDERUNG", "NEU"],
                "changed_entries": [
                    "",
                    "Datenelement_FV2410|Datenelement_FV2504|Qualifier_FV2410|Qualifier_FV2504",
                    "",
                ],
                f"Segmentname_{self.formatversions.subsequent_formatversion}": ["", "2", "3"],
                f"Segmentgruppe_{self.formatversions.subsequent_formatversion}": ["", "b", "c"],
                f"Datenelement_{self.formatversions.subsequent_formatversion}": ["", "m", "n"],
                f"Qualifier_{self.formatversions.subsequent_formatversion}": ["", "XY", ""],
            }
        )

        output_df = align_columns(
            previous_pruefid,
            subsequent_pruefid,
            previous_formatversion=self.formatversions.previous_formatversion,
            subsequent_formatversion=self.formatversions.subsequent_formatversion,
        )
        assert_frame_equal(output_df, expected_output)
