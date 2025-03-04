import unittest
from pathlib import Path
from tempfile import gettempdir

import FreeCAD as fc  # noqa: N813
import FreeCADGui as fcg  # noqa: N813

TEMPDIR = Path(gettempdir())
DOC_NAME = "GridfinityDocument"

SIMPLE_COMMANDS = [
    "CreateBinBlank",
    "CreateBinBase",
    "CreateSimpleStorageBin",
    "CreateEcoBin",
    "CreatePartsBin",
    "CreateBaseplate",
    "CreateMagnetBaseplate",
    "CreateScrewTogetherBaseplate",
    "CreateLBinBlank",
]

CUSTOM_BIN_COMMANDS = [
    "CreateCustomBin",
]


fcg.activateWorkbench("GridfinityWorkbench")


class TestCommands(unittest.TestCase):
    def test_commands_active(self) -> None:
        commands = SIMPLE_COMMANDS + CUSTOM_BIN_COMMANDS

        for command_name in commands:
            self.assertFalse(fcg.Command.get(command_name).isActive())

        fc.newDocument(DOC_NAME)

        for command_name in commands:
            self.assertTrue(fcg.Command.get(command_name).isActive())

        fc.closeDocument(DOC_NAME)


class TestSave(unittest.TestCase):
    def setUp(self) -> None:
        self.filepath = str(TEMPDIR / self.__class__.__name__) + ".FCStd"

    def test_serialization(self) -> None:
        commands = SIMPLE_COMMANDS

        doc = fc.newDocument(DOC_NAME)

        for command_name in commands:
            fcg.Command.get(command_name).run()
        self.assertEqual(len(doc.Objects), len(commands))

        doc.saveAs(str(self.filepath))
        fc.closeDocument(DOC_NAME)

    def test_reopen(self) -> None:
        command_name = SIMPLE_COMMANDS[0]

        doc = fc.newDocument(DOC_NAME)
        fcg.Command.get(command_name).run()
        doc.saveAs(str(self.filepath))
        fc.closeDocument(DOC_NAME)
        doc = fc.openDocument(self.filepath)

        self.assertEqual(len(doc.Objects), 1)
        obj = doc.Objects[0]

        # change something, so `recompute` is not optimized out
        # (even force=True doesn't guarantee this)
        obj.xGridUnits = 3
        recomputed_count = doc.recompute((obj,), True)  # noqa: FBT003
        self.assertEqual(recomputed_count, 1)

        fc.closeDocument(doc.Name)
