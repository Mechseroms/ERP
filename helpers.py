import string, random,database
from PyQt5.QtWidgets import QMessageBox

def random_tag(length):
    characters = string.digits
    return ''.join(random.choice(characters) for i in range(length))

def check_barcode(barcode):
    linked, data = database.check_linked_lists(barcode)
    if linked:
        barcode = data['linked_barcode']

    success, data = database.check_pantry_database(barcode)
    if success:
        return True, data

    return False, {}


def barcode_changed(barcode):
    # check the pantry
    linked, data = database.check_linked_lists(barcode)
    if linked:
        _barcode = data['linked_barcode']
        # warn that the item is linked and that the parent will be substituted
        msgbox = QMessageBox()
        msgbox.setText(f"Barcode {barcode} is linked to {_barcode}, your data will be repopulated, do you wish to continue or cancel and revert?")
        msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        accepted = msgbox.exec_()

        if accepted == QMessageBox.Cancel:
            return -1, {}

        barcode = _barcode

    success, data = database.check_pantry_database(barcode)
    if success:
        return 0, data

    return 1, {}
