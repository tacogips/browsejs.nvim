# flake8: noqa
import neovim
import context  # noqa
import sys

from browsejs.parser import Lexer, SectionType

import unittest


class TestLexer(unittest.TestCase):
    def test_lexer_funcs(self):
        test_input = """
not in comment here
 //  comment1
  /* some
     comment  */
        """
        lexer = Lexer(test_input.split("\n"))
        self.assertEqual(lexer.current_line_idx, 0)
        self.assertEqual(lexer.current_offset, 0)

        # line:1 empty line
        lexer._skip_until_comment()
        self.assertEqual(lexer.current_line_idx, 0)
        self.assertEqual(lexer.current_offset, 0)
        self.assertEqual(lexer._at_end_of_current_line(), True)
        self.assertEqual(lexer._get_current_char(), None)

        # line:2 not in comment
        lexer._feed_line()
        self.assertEqual(lexer.current_line_idx, 1)
        self.assertEqual(lexer.current_offset, 0)
        self.assertEqual(lexer._at_end_of_current_line(), False)
        self.assertEqual(lexer._get_current_char(), "n")
        lexer._skip_until_comment()

        self.assertEqual(lexer._at_end_of_current_line(), True)
        self.assertEqual(lexer._get_current_char(), None)

        # line:3 in line comment
        lexer._feed_line()
        self.assertEqual(lexer.current_line_idx, 2)
        self.assertEqual(lexer.current_offset, 0)
        self.assertEqual(lexer._at_end_of_current_line(), False)
        self.assertEqual(lexer._get_current_char(), " ")
        lexer._skip_until_comment()

        self.assertEqual(lexer._at_end_of_current_line(), False)
        self.assertEqual(lexer.current_offset, 3)
        self.assertEqual(lexer._get_current_char(), " ")
        self.assertEqual(lexer.in_line_comment, True)
        lexer._skip_white_space()

        self.assertEqual(lexer.current_offset, 5)
        self.assertEqual(lexer._get_current_char(), "c")
        self.assertEqual(lexer.in_line_comment, True)
        self.assertEqual(lexer._read_identifier(), "comment1")
        self.assertEqual(lexer._at_end_of_current_line(), True)

        # line:4 in block comment
        lexer._feed_line()

        self.assertEqual(lexer._in_comment(), False)
        self.assertEqual(lexer.current_line_idx, 3)
        self.assertEqual(lexer.current_offset, 0)
        self.assertEqual(lexer._at_end_of_current_line(), False)
        lexer._skip_until_comment()

        self.assertEqual(lexer._at_end_of_current_line(), False)
        self.assertEqual(lexer.current_offset, 4)
        self.assertEqual(lexer._get_current_char(), " ")
        self.assertEqual(lexer.in_line_comment, False)
        self.assertEqual(lexer.in_block_comment, True)
        lexer._skip_white_space()

        self.assertEqual(lexer.current_offset, 5)
        self.assertEqual(lexer._get_current_char(), "s")
        self.assertEqual(lexer._read_identifier(), "some")
        self.assertEqual(lexer._at_end_of_current_line(), True)

        # line:5  in block comment 2
        lexer._feed_line()

        self.assertEqual(lexer._in_comment(), True)
        self.assertEqual(lexer.current_line_idx, 4)
        self.assertEqual(lexer.current_offset, 0)
        self.assertEqual(lexer._at_end_of_current_line(), False)

        lexer._skip_until_comment()  # do nothing
        self.assertEqual(lexer.current_offset, 0)
        self.assertEqual(lexer._at_end_of_current_line(), False)

        lexer._skip_white_space()
        self.assertEqual(lexer._read_identifier(), "comment")
        lexer._skip_white_space()

        self.assertEqual(lexer._at_end_of_block_comment(), True)
        self.assertEqual(lexer._at_end_of_sentence(), True)
        self.assertEqual(lexer._at_end_of_current_line(), False)

    def test_lexer_section_1(self):
        test_input = """
var thisIsJs1 = 123.3;
//
//  {% start header_tag %}
//   <script></script>
 /*  <meta></meta>*/
//  {% end %}

//  {% start custom_tag %}
/*
  <div id="custom">
  </div>
  {% end %} */

/* {% start style %} <br> {% end %} */
// {% start copy %} {"from":"/some/path"} {% end %}
//  function bbb(){}
var thisIsJs2 = "123.3";
function some(){
}
        """.split(
            "\n"
        )

        lexer = Lexer(test_input)
        section = lexer._next_section()
        self.assertEqual(section.section_type, SectionType.CUSTOM_HEADER_TAG)
        self.assertEqual(len(section.body), 2)
        self.assertEqual(section.body[0], "<script></script>")
        self.assertEqual(section.body[1], "<meta></meta>")
        self.assertEqual(len(section.section_infos), 4)
        self.assertEqual(section.section_infos[0].line_idx, 3)
        self.assertEqual(section.section_infos[0].start_offset, 4)
        self.assertEqual(section.section_infos[0].end_offset, 26)

        self.assertEqual(section.section_infos[1].line_idx, 4)
        self.assertEqual(section.section_infos[1].start_offset, 2)
        self.assertEqual(section.section_infos[1].end_offset, 22)

        self.assertEqual(section.section_infos[2].line_idx, 5)
        self.assertEqual(section.section_infos[2].start_offset, 3)
        self.assertEqual(section.section_infos[2].end_offset, 18)

        self.assertEqual(section.section_infos[3].line_idx, 6)
        self.assertEqual(section.section_infos[3].start_offset, 2)
        self.assertEqual(section.section_infos[3].end_offset, 13)

        section = lexer._next_section()
        self.assertEqual(section.section_type, SectionType.CUSTOM_TAG)
        self.assertEqual(len(section.body), 2)
        self.assertEqual(section.body[0], '<div id="custom">')
        self.assertEqual(section.body[1], "</div>")

        self.assertEqual(len(section.section_infos), 4)
        self.assertEqual(section.section_infos[0].line_idx, 8)
        self.assertEqual(section.section_infos[0].start_offset, 4)
        self.assertEqual(section.section_infos[0].end_offset, 26)

        self.assertEqual(section.section_infos[1].line_idx, 10)  # <div id="custom">
        self.assertEqual(section.section_infos[1].start_offset, 0)
        self.assertEqual(section.section_infos[1].end_offset, 19)

        self.assertEqual(section.section_infos[2].line_idx, 11)
        self.assertEqual(section.section_infos[2].start_offset, 0)  # </div>
        self.assertEqual(section.section_infos[2].end_offset, 8)

        self.assertEqual(section.section_infos[3].line_idx, 12)  # {% end %} */
        self.assertEqual(section.section_infos[3].start_offset, 0)
        self.assertEqual(section.section_infos[3].end_offset, 11)

        section = lexer._next_section()
        self.assertEqual(section.section_type, SectionType.STYLE)
        self.assertEqual(len(section.body), 1)
        self.assertEqual(section.body[0], "<br> ")

        # /* {% start style %} <br> {% end %} */
        self.assertEqual(len(section.section_infos), 1)
        self.assertEqual(section.section_infos[0].line_idx, 14)
        self.assertEqual(section.section_infos[0].start_offset, 3)
        self.assertEqual(section.section_infos[0].end_offset, 35)

        section = lexer._next_section()
        self.assertEqual(section.section_type, SectionType.COPY)
        self.assertEqual(len(section.body), 1)
        self.assertEqual(section.body[0], '{"from":"/some/path"} ')

        # read all
        lexer = Lexer(test_input)
        self.assertEqual(len(lexer.all_sections()), 4)

    def test_lexer_tricky(self):
        test_input = """
var thisIsJs1 = 123.3;
//
//  {% start header_tag%}
var notInComment = 1111;
/*   <script></script>
//  <meta></meta> */

//{% start header_tag%}
//  {%end %}
var thisIsJs2 = "123.3";
        """.split(
            "\n"
        )

        lexer = Lexer(test_input)
        section = lexer._next_section()
        self.assertEqual(section.section_type, SectionType.CUSTOM_HEADER_TAG)
        self.assertEqual(len(section.body), 2)
        self.assertEqual(section.body[0], "<script></script>")
        self.assertEqual(section.body[1], "//  <meta></meta> ")

        # read all
        lexer = Lexer(test_input)
        self.assertEqual(len(lexer.all_sections()), 1)

    def test_lexer_invalid1(self):
        test_input = """
var thisIsJs1 = 123.3;
//
//  {% start header_tag
//   <script></script>
//  <meta></meta>
//  {%end %}
var thisIsJs2 = "123.3";
        """.split(
            "\n"
        )

        lexer = Lexer(test_input)
        section = lexer._next_section()
        self.assertEqual(section, None)

        # read all
        lexer = Lexer(test_input)
        self.assertEqual(len(lexer.all_sections()), 0)

    def test_lexer_invalid1(self):
        test_input = """
var thisIsJs1 = 123.3;
//
//  {%  start header_tag
//   <script></script>
//  <meta></meta>
//  {%end %}
var thisIsJs2 = "123.3";
        """.split(
            "\n"
        )

        lexer = Lexer(test_input)
        section = lexer._next_section()
        self.assertEqual(section, None)

        # read all
        lexer = Lexer(test_input)
        self.assertEqual(len(lexer.all_sections()), 0)

    def test_lexer_invalid2(self):
        test_input = """
var thisIsJs1 = 123.3;
//
//  {%  start header_tag  %}
//   <script></script>
//  <meta></meta>
//
var thisIsJs2 = "123.3";
        """.split(
            "\n"
        )

        lexer = Lexer(test_input)
        section = lexer._next_section()
        self.assertEqual(section, None)

        # read all
        lexer = Lexer(test_input)
        self.assertEqual(len(lexer.all_sections()), 0)

    def test_lexer_invalid3(self):
        test_input = """
var thisIsJs1 = 123.3;
//  {%  start XXXX_invalid  %}
//  {%  end  %}
//  {%  start header_tag  %}
//   <script src="https://cdn.jsdelivr.net/npm/p5@1.1.9/lib/p5.js"></script>
//  <meta></meta>
// {%  end  %}
var thisIsJs2 = "123.3";
        """.split(
            "\n"
        )

        lexer = Lexer(test_input)
        section = lexer._next_section()
        self.assertEqual(section.section_type, SectionType.CUSTOM_HEADER_TAG)
        self.assertEqual(
            section.body[0],
            '<script src="https://cdn.jsdelivr.net/npm/p5@1.1.9/lib/p5.js"></script>',
        )

        # read all
        lexer = Lexer(test_input)
        self.assertEqual(len(lexer.all_sections()), 1)


if __name__ == "__main__":
    unittest.main()
