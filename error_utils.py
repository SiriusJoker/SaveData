def show_error_window(error_message, message):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText("The script Save_data_to_json encountered an error. \n" + message)
    msg_box.setDetailedText(error_message)
    msg_box.exec_()