# -*- coding: utf-8 -*-
"""
created on 24/07/2019 14:07
@author: fgiely
"""
import pytest

from CoreNLGMod.NlgTools import NlgTools
from CoreNLGMod.tests.fixtures import list_elem, long_list_elem, long_list_with_empty_elem, iter_elem_with_post_treatment_fr


class TestIterElem:

    nlg = NlgTools(lang="en")
    iter_elems = nlg.enum

    @pytest.mark.parametrize(
        "input",
        [
            None,
            [],
            [""],
            [None],
            [[]],
            [[""]],
            [["", ""], ""],
            [[None], None],
            [[None, ""], "", None],
        ],
    )
    def test_empty(self, input):
        assert self.iter_elems(input) == ""

    @pytest.mark.parametrize(
        "input",
        [
            None,
            [],
            [""],
            [None],
            [[]],
            [[""]],
            [["", ""], ""],
            [[None], None],
            [[None, ""], "", None],
        ],
    )
    def test_empty_begin_with(self, input):
            assert self.iter_elems(input, begin_w="begin") == ""

    @pytest.mark.parametrize(
        "input",
        [
            None,
            [],
            [""],
            [None],
            [[]],
            [[""]],
            [["", ""], ""],
            [[None], None],
            [[None, ""], "", None],
        ],
    )
    def test_empty_end_with(self, input):
        assert self.iter_elems(input, end_w="end") == ""

    @pytest.mark.parametrize(
        "input",
        [
            [],
            [""],
            [None],
            [[]],
            [[""]],
            [["", ""], ""],
            [[None], None],
            [[None, ""], "", None],
        ],
    )
    def test_none_text_empty(self, input):
        assert self.iter_elems(input, text_if_empty_list="empty") == "empty"

    def test_single_sentence(self, list_elem):
        assert self.iter_elems([[e for e in list_elem]]) == "elem1 , elem2 and elem3"

    def test_bullet_points(self, list_elem):
        text = self.iter_elems([[e for e in list_elem]], nb_elem_bullet=0)
        assert text == "<ul><li>Elem1</li><li>Elem2</li><li>Elem3</li></ul>"

    def test_bullet_points_no_capitalize(self, list_elem):
        text = self.iter_elems([[e for e in list_elem]], nb_elem_bullet=0, capitalize_bullets=False)
        assert text == "<ul><li>elem1</li><li>elem2</li><li>elem3</li></ul>"

    def test_long_list_elem(self, long_list_elem):
        text = self.iter_elems([[e for e in long_list_elem]], )
        assert text == "elem1 , elem2 , elem3 , elem4 , elem5 and elem6"

    def test_bullet_long_list_elem(self, long_list_elem):
        text = self.iter_elems([[e for e in long_list_elem]], nb_elem_bullet=0)
        assert text == "<ul><li>Elem1</li><li>Elem2</li><li>Elem3</li><li>Elem4</li><li>Elem5</li><li>Elem6</li></ul>"

    def test_long_list_limit_elem(self, long_list_elem):
        text = self.iter_elems([[e for e in long_list_elem]], max_elem=4)
        assert text == "elem1 , elem2 , elem3 and elem4"

    def test_bullet_long_list_limit_elem(self, long_list_elem):
        text = self.iter_elems([[e for e in long_list_elem]], nb_elem_bullet=0, max_elem=4)
        assert text == "<ul><li>Elem1</li><li>Elem2</li><li>Elem3</li><li>Elem4</li></ul>"

    def test_long_list_limit_no_more_bullet_elem(self, long_list_elem):
        text = self.iter_elems([[e for e in long_list_elem]], nb_elem_bullet=3, max_elem=2)
        assert text == "elem1 and elem2"

    def test_long_list_with_empty_elem(self, long_list_with_empty_elem):
        text = self.iter_elems([[e for e in long_list_with_empty_elem]], max_elem=4)
        assert text == "elem1 , elem2 , elem4 and elem6"

    def test_bullet_long_list_with_empty_elem(self, long_list_with_empty_elem):
        text = self.iter_elems([[e for e in long_list_with_empty_elem]], nb_elem_bullet=0)
        assert text == "<ul><li>Elem1</li><li>Elem2</li><li>Elem4</li><li>Elem6</li></ul>"

    def test_complete_bullet(self, long_list_elem, long_list_with_empty_elem):
        text = self.iter_elems([
            [e for e in long_list_elem],
            [e for e in long_list_with_empty_elem]
        ], begin_w="start", nb_elem_bullet=0, end_w="end")
        assert text == "start <ul><li>Elem1 elem1</li><li>Elem2 elem2</li><li>Elem3</li><li>Elem4 elem4</li>" \
                       "<li>Elem5</li><li>Elem6 elem6</li></ul> end"

    def test_complete(self, long_list_elem, long_list_with_empty_elem):
        text = self.iter_elems([
            [e for e in long_list_elem],
            [e for e in long_list_with_empty_elem]
        ], begin_w="start", end_w="end")
        assert text == "start elem1 elem1 , elem2 elem2 , elem3 , elem4 elem4 , elem5 and elem6 elem6 end"


class TestIterElemPostTreatment:
    def test_single_sentence_with_post_treatment(self, list_elem):
        text = iter_elem_with_post_treatment_fr([[e for e in list_elem]])
        assert text == "Elem1, elem2 et elem3"

    def test_bullet_points_with_post_treatment(self, list_elem):
        text = iter_elem_with_post_treatment_fr([[e for e in list_elem]], nb_elem_bullet=0)
        assert text == "Elem1Elem2Elem3"
