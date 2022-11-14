"""
LibreOffice plugin to insert a new row.
Presumptions:
- first column is a date;
- an empty line at the end of a table;
- named styles.
"""

from datetime import date
import uno
from com.sun.star.sheet.CellInsertMode import DOWN


class Row(object):
    """
    A table row (a piece of a sheet with a height = 1).
    """

    MAX_LENGTH = 15

    def __init__(self, sheet, row: int, start_column: int, end_column: int):
        self.sheet = sheet
        self.row = row
        self.start_column = start_column
        self.end_column = end_column


    def is_table_top(self):
        """
        Returns: whatever the row is a top of a table.
        """
        cell_bellow = self.sheet.getCellByPosition(self.start_column, self.row + 1)
        return cell_bellow.getString() != ""


    def insert_new_row(self, above):
        """
        Returns new row.
        """
        target = uno.createUnoStruct("com.sun.star.table.CellRangeAddress")
        target.Sheet = self.sheet.RangeAddress.Sheet
        target.StartColumn = self.start_column
        target.EndColumn = self.end_column
        target.StartRow = self.row if above else self.row + 1
        target.EndRow = target.StartRow
        self.sheet.insertCells(target, DOWN)

        if above:
            new_row = Row(self.sheet, self.row, self.start_column, self.end_column)
            self.row += 1
        else:
            new_row = Row(self.sheet, self.row + 1, self.start_column, self.end_column)

        # Fix style.
        for i in range(len(self)):
            new_row[i].setPropertyValue(
                "CellStyle",
                self[i].getPropertyValue("CellStyle")
            )
        return new_row

    def __getitem__(self, i: int):
        """
        Returns a cell.
        """
        assert(i >= 0)
        assert(self.start_column + i <= self.end_column)
        return self.sheet.getCellByPosition(self.start_column + i, self.row)

    def __len__(self):
        return self.end_column - self.start_column + 1

    @classmethod
    def find_end_column(cls, sheet, row: int, start_column: int):
        """
        Finds last column of the table using border width.
        """

        for i in range(cls.MAX_LENGTH):
            cell = sheet.getCellByPosition(start_column + i, row)
            right_border = cell.getPropertyValue("RightBorder")
            if right_border.OuterLineWidth > 0:
                return start_column + i

        return start_column + cls.MAX_LENGTH


def NewRowPython():
    desktop = XSCRIPTCONTEXT.getDesktop()
    doc = desktop.getCurrentComponent()
    sheet = doc.CurrentController.ActiveSheet
    if not doc.CurrentController.getSelection().supportsService("com.sun.star.sheet.SheetCell"):
        print("WTF?")
        return
    current_pos = doc.CurrentController.getSelection().getCellAddress()
    row = Row(
        sheet,
        current_pos.Row,
        current_pos.Column,
        Row.find_end_column(sheet, current_pos.Row, current_pos.Column)
    )
    new_row = row.insert_new_row(row.is_table_top())
    new_row[0].setString(date.today().strftime("%d.%m.%Y"))
