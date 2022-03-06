import PySimpleGUI as sg

from core import ClassText, Member

column_layout = [[
    sg.Text("Datatype: "),
    sg.InputText(key=("datatype", 0)),
    sg.Text("Name: "),
    sg.InputText(key=("name", 0)),
    sg.Button("Add Variable", key="add")
]]

layout = [
    [sg.Multiline(size=(100, 10), key="output")],
    [sg.Text("Class Name"), sg.InputText("my_class", key="class")],
    [sg.Text("Spaces per tab"), sg.InputText("2", key="spaces")],
    [sg.Checkbox("Constructor", key="binit", default=True),
     sg.Checkbox("to_string", key="bto_string", default=True),
     sg.Checkbox("Printable", key="bprintable", default=True),
     sg.Checkbox("Equals Operators", key="beq", default=True),
     sg.Checkbox("Comparison Operators", key="border", default=True),
     sg.Checkbox("Getters and Setters", key="bgetter_and_setter", default=True)],
    [sg.Column(column_layout, key="column")],
    [sg.Button("Generate Class", key="gen"), sg.Exit()]
]

current_count = 0
window = sg.Window("C++ Class Generator", layout)


def add_row():
    global current_count
    current_count += 1
    row = [[sg.Text("Datatype: "),
           sg.InputText(key=("datatype", current_count)),
           sg.Text("Name: "),
           sg.InputText(key=("name", current_count))]]
    window.extend_layout(window["column"], row)


while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    elif event == "add":
        add_row()
    elif event == "gen":
        if not values["class"]:
            continue

        class_name = values["class"]
        members_list = []

        for i in range(current_count + 1):
            datatype = values.get(("datatype", i), "")
            name = values.get(("name", i), "")
            if not datatype or not name:
                continue
            members_list.append(Member(name, datatype))

        if not members_list:
            continue

        try:
            spaces = int(values["spaces"])
        except ValueError:
            continue

        init = values["binit"]
        to_string = values["bto_string"]
        printable = values["bprintable"]
        eq = values["beq"]
        order = values["border"]
        getter_and_setter = values["bgetter_and_setter"]

        class_text = ClassText(class_name,
                               spaces,
                               init,
                               to_string,
                               printable,
                               eq,
                               order,
                               getter_and_setter,
                               *members_list)

        window["output"].update(str(class_text))

window.close()
