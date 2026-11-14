from enum import Enum
from io import StringIO
from typing import List, Tuple


class Contents:
    def __init__(
        self, js_lines, custom_header_tags, custom_tags, custom_styles, copy_files
    ):
        self.js_lines = js_lines
        self.custom_header_tags = custom_header_tags
        self.custom_tags = custom_tags
        self.custom_styles = custom_styles
        self.copy_files = copy_files


class SectionType(str, Enum):
    CUSTOM_HEADER_TAG = "header_tag"
    CUSTOM_TAG = "custom_tag"
    STYLE = "style"
    COPY = "copy"

    @classmethod
    def from_str(cls, s: str):
        for each in cls:
            if each.value == s:
                return each

        return None


class SectionLineInfo:
    def __init__(
        self, line_idx, start_offset=None, end_offset=None,
    ):
        self.line_idx = line_idx
        self.start_offset = start_offset
        self.end_offset = end_offset


class Section:
    def __init__(self, section_type: SectionType):
        self.section_type = section_type
        self.body = []
        self.section_infos: SectionLineInfo = []

    def add_line(self, line):
        self.body.append(line)

    def is_same_line_idx_as_latest(self, line_idx):
        if not self.section_infos:
            return False
        return self.section_infos[-1].line_idx == line_idx

    def latest_section_info(self):
        if not self.section_infos:
            return None
        return self.section_infos[-1]


class Lexer:
    def __init__(self, lines):
        self.lines = lines
        self.current_line_idx = 0
        self.current_offset = 0
        self.in_line_comment = False
        self.in_block_comment = False
        self.current_section = None

    def all_sections(self) -> List[Section]:
        result = []
        while True:
            section = self._next_section()
            if not section:
                return result

            result.append(section)

    def _skip_white_space(self):
        line = self._current_line()
        if not line:
            return

        while True:
            current_char = self._get_current_char()
            if not current_char:
                return

            if current_char.isspace():
                self._forward_current_offset(1)
                continue
            else:
                return

    def _skip_until_comment(self):
        if self._in_comment():
            return
        self._skip_white_space()
        line = self._current_line()
        if not line:
            return

        while True:
            if self._at_end_of_current_line():
                return

            current_char = self._get_current_char()
            if current_char == "/":
                peek_char = self._peek()
                if not peek_char:
                    self.current_offset = len(line)  # end of line
                    return

                if peek_char == "/":
                    self.in_line_comment = True
                    self._forward_current_offset(2)
                    return

                if peek_char == "*":
                    self.in_block_comment = True
                    self._forward_current_offset(2)
                    return

            self._forward_current_offset()

    def _read_identifier(self):
        self._skip_white_space()

        s = StringIO()
        while True:
            c = self._get_current_char()
            if c is None or self._at_end_of_sentence() or c.isspace():
                return s.getvalue()

            s.write(c)
            self._forward_current_offset(1)

    def _forward_current_offset(self, forward=1):
        self.current_offset += forward

    def _feed_line(self):
        self.current_line_idx += 1
        self.current_offset = 0
        if self.in_line_comment:
            self.in_line_comment = False

    def _in_comment(self):
        return self.in_line_comment or self.in_block_comment

    def _at_end_of_current_line(self):
        if self.current_offset >= len(self.lines[self.current_line_idx]):
            return True
        return False

    def _get_current_char(self):
        line = self._current_line()
        if not line:
            return
        return line[self.current_offset]

    def _peek(self, size=1):
        peek_offset = self.current_offset + size
        if peek_offset >= len(self.lines[self.current_line_idx]):
            return None

        return self._current_line()[peek_offset]

    def _peek_section_line(self):
        # Peek forward to end of sentence and return the value and last index.
        # If current line ends with `*/` the last index points at before the `*/`
        buf_offset = self.current_offset
        section_line = self._read_section_line()
        section_line_end_offset = self.current_offset
        self.current_offset = buf_offset
        return (section_line, section_line_end_offset)

    def _current_line(self):
        if self._at_end_of_current_line():
            return None
        return self.lines[self.current_line_idx]

    def _last_idx_of_current_line(self):
        if self._at_end_of_current_line():
            return None
        return len(self.lines[self.current_line_idx]) - 1

    def _at_end_of_sentence(self):
        """
        in the cases
        - end of block comment
        - `{% %}` found
        return True

        """
        c = self._get_current_char()
        if not c:
            return
        elif c == "{":
            peek_char = self._peek()
            if peek_char == "%":
                return True

        elif c == "%":
            peek_char = self._peek()
            if peek_char == "}":
                return True
        elif self._at_end_of_block_comment():
            return True

        return False

    def _at_end_of_block_comment(self):
        if not self.in_block_comment:
            return
        current_char = self._get_current_char()
        if not current_char:
            return
        if current_char == "*":
            peek_char = self._peek()
            if peek_char == "/":
                return True
        return False

    def _read_section_line(self):
        """ Read string until end of the line of the section.
            `section` means the lines surrounded by {% start_xxxx %} and {% end %}.
            Its not garanteed to self._at_end_of_current_line() is always True after this function has called.
            If the close of block comment appears in middle of the line, this function will stop reading at the point.

             e.g.
             ```
             /*
             {% start_xxxx %}
                "whole of this line will read"
                "this line will read until end of block comment char `*`" */
             ```

             ...

        """
        s = StringIO()
        while True:
            c = self._get_current_char()

            section_end = self._at_end_of_sentence()
            if section_end or c is None:
                return s.getvalue()

            s.write(c)
            self._forward_current_offset(1)

    def _at_end_of_section_closing_mark(self):
        """ detect closing `%} mark """
        if self._get_current_char() == "%":
            # detect closing `%}
            peek_char = self._peek()
            if peek_char == "}":
                return True

        return False

    def _next_section(self):
        while True:
            if self.current_line_idx >= len(self.lines):
                return None

            head_offset_of_comment_line = 0
            if not self._in_comment():
                self._skip_until_comment()
                head_offset_of_comment_line = self.current_offset

            self._skip_white_space()
            current_char = self._get_current_char()
            peek_char = self._peek()

            if not current_char:
                self._feed_line()
                continue

            elif self._at_end_of_block_comment():
                self.in_block_comment = False
                self._forward_current_offset(2)
                self._feed_line()
                continue

            elif current_char == "{" and peek_char == "%":
                maybe_start_offset = self.current_offset
                self._forward_current_offset(2)
                identifier = self._read_identifier()

                if identifier == "start":
                    self._skip_white_space()
                    section_name = self._read_identifier()
                    section_type = SectionType.from_str(section_name)
                    if not section_type:
                        continue
                    self._skip_white_space()
                    if self._at_end_of_section_closing_mark():
                        self._forward_current_offset(2)
                        if not self.current_section:
                            # open section
                            self.current_section = Section(section_type)
                            buf_offset = self.current_offset
                            self._read_section_line()
                            section_line_end_offset = self.current_offset
                            self.current_offset = buf_offset
                            (_, section_end_idx) = self._peek_section_line()

                            self.current_section.section_infos.append(
                                SectionLineInfo(
                                    self.current_line_idx,
                                    maybe_start_offset,
                                    section_end_idx,
                                )
                            )
                            continue

                # close section
                elif identifier == "end":
                    self._skip_white_space()
                    if self._at_end_of_section_closing_mark():

                        if self.current_section:

                            self._forward_current_offset(2)
                            current_offset = self.current_offset
                            if self.current_section.is_same_line_idx_as_latest(
                                self.current_line_idx
                            ):
                                self.current_section.latest_section_info().end_offset = (
                                    current_offset
                                )

                            else:
                                self.current_section.section_infos.append(
                                    SectionLineInfo(
                                        self.current_line_idx,
                                        head_offset_of_comment_line,
                                        current_offset,
                                    )
                                )

                            result = self.current_section
                            self.current_section = None
                            return result
            else:
                if self.current_section:
                    line = self._read_section_line()
                    self.current_section.add_line(line)

                    if self.current_section.is_same_line_idx_as_latest(
                        self.current_line_idx
                    ):
                        self.current_section.latest_section_info().end_offset = (
                            self.current_offset
                        )

                    else:
                        self.current_section.section_infos.append(
                            SectionLineInfo(
                                self.current_line_idx,
                                head_offset_of_comment_line,
                                self.current_offset,
                            )
                        )

                    continue

                self._forward_current_offset(1)


class Parser:
    @classmethod
    def parse(cls, all_lines) -> Contents:
        lexer = Lexer(all_lines)

        custom_header_tags = []
        custom_tags = []
        custom_styles = []
        copy_files = []
        all_sections = lexer.all_sections()
        for each_section in all_sections:
            tpe = each_section.section_type
            if tpe == SectionType.CUSTOM_HEADER_TAG:
                custom_header_tags += each_section.body
            elif tpe == SectionType.CUSTOM_TAG:
                custom_tags += each_section.body
            elif tpe == SectionType.STYLE:
                custom_styles += each_section.body
            elif tpe == SectionType.COPY:
                copy_files += each_section.body

        return Contents(
            js_lines=Parser.omit_section_area_from_lines(all_lines, all_sections),
            custom_header_tags=custom_header_tags,
            custom_tags=custom_tags,
            custom_styles=custom_styles,
            copy_files=copy_files,
        )

    @classmethod
    def omit_section_area_from_lines(cls, all_lines, sections: List[Section]):
        def emit_from_line(line, section_info: SectionLineInfo):
            i = section_info.start_offset
            line_list = list(line)
            for i in range(section_info.end_offset - section_info.start_offset):
                offset = section_info.start_offset + i
                line_list[offset] = " "
            return "".join(line_list)

        for each_section in sections:
            for each_sec_info in each_section.section_infos:
                line = all_lines[each_sec_info.line_idx]
                all_lines[each_sec_info.line_idx] = emit_from_line(line, each_sec_info)
        return all_lines
