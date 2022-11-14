import sublime_plugin
from datetime import datetime


class InsertDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        today = datetime.today().strftime("%d.%m.%Y")
        self.view.insert(edit, self.view.sel()[0].begin(), "===== {} =====\n".format(today))


class MarkCodeCommand(sublime_plugin.TextCommand):
    """
    Markdown plugin to mark symbols as a code using ` or ```.
    """

    SEPARATORS = [" ", " ", "\t", "\r", "\n"]

    def _get_word_bounds(self, line: str, pos: int):
        if len(line) == 0:
            return (0, 0)
        assert(pos < len(line))
        begin = 0
        end = len(line) - 1
        for i in range(len(line)):
            if line[i] in self.SEPARATORS:
                if i < pos:
                    begin = i
                else:
                    end = i
                    break
        return (begin + 1, end)

    def run(self, edit):
        region = self.view.sel()[0]
        if region.begin() == region.end():
            # Let's mark single word as a code.
            # Note: View::word() is not good enough.
            line_region = self.view.line(region.begin())
            line = self.view.substr(line_region)
            begin, end = self._get_word_bounds(line, region.begin() - line_region.begin())
            self.view.insert(edit, end + line_region.begin(), "`")
            self.view.insert(edit, begin + line_region.begin(), "`")
        else:
            # Let's mark several lines as a code.
            self.view.insert(edit, region.end(), "\n```")
            self.view.insert(edit, region.begin(), "```\n")


class InsertDashCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, self.view.sel()[0].begin(), "—")


class InsertLeftQuoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, self.view.sel()[0].begin(), "«")


class InsertRightQuoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, self.view.sel()[0].begin(), "»")


class InsertLeftBraceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, self.view.sel()[0].begin(), "⟨")


class InsertRightBraceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, self.view.sel()[0].begin(), "⟩")
