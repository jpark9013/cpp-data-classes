class Member:
    def __init__(self, name: str, datatype: str):
        self.name = name
        self.datatype = datatype

    def __str__(self) -> str:
        return f"{self.datatype} {self.name}"

    def get_init(self) -> str:
        return f"const {self.datatype} &_{self.name}"


class Text:
    def __init__(self, spaces: int) -> None:
        self._data = []
        self._spaces = spaces

    def add(self, *lines, **kwargs) -> None:
        try:
            indent = kwargs.pop("indent")
        except KeyError:
            raise Exception("Expected indent argument")

        buffer = kwargs.get("buffer", False)
        block = "\n".join(" " * (self._spaces * indent) + line for line in lines)

        if buffer:
            if len(self._data) == 0:
                self._data.append([])
            self._data[-1].append(block)
        else:
            self._data.append([block])

    def __str__(self) -> str:
        return "\n\n".join("\n".join(line) for line in self._data)


def join(*strings):
    return "".join(strings)


class ClassText:

    def __init__(
            self,
            name: str,
            spaces: int,
            init: bool,
            to_string: bool,
            printable: bool,
            eq: bool,
            order: bool,
            getter_and_setter: bool,
            *members: Member
    ) -> None:

        self._name = name
        self._spaces = spaces
        self._init = init
        self._to_string = to_string
        self._printable = printable
        self._eq = eq
        self._order = order
        self._getter_and_setter = getter_and_setter
        self._members = members

        self._data = Text(self._spaces)
        self._data.add(f"class {self._name} {{", indent=0)

        if self._getter_and_setter:
            self._data.add(*[f"{str(member)};" for member in self._members], indent=1)
            self._data.add("public: ", indent=1)
        else:
            self._data.add("public: ", indent=1)
            self._data.add(*[f"{str(member)};" for member in self._members], indent=1)

        if self._init:
            self._add_init()

        if self._eq:
            self._add_eq()

        if self._order:
            self._add_order()

        if self._getter_and_setter:
            self._add_getter_and_setter()

        # finish the closing brace
        self._data.add("};", indent=0)

        if self._to_string:
            self._add_to_string()

        if self._printable:
            self._add_printable()

    def __str__(self) -> str:
        return str(self._data)

    def _add_function(self, statement: str, *rest: str, **kwargs):
        indent = kwargs.pop("indent")
        self._data.add(f"{statement} {{", indent=indent, buffer=False)
        self._data.add(*rest, indent=indent+1, buffer=True)
        self._data.add("}", indent=indent, buffer=True)

    def _add_init(self) -> None:
        # default constructor
        self._add_function(f"{self._name}()", indent=1)

        statement = join(
            f"{self._name}(",
            ", ".join(member.get_init() for member in self._members),
            ") : ",
            ", ".join(f"{member.name}(_{member.name})" for member in self._members),
        )

        self._add_function(statement=statement, indent=1)

    def _add_return_op(self, op: str, indent: int, body_text: str = None):
        statement = f"friend bool operator {op} (const {self._name} &a, const {self._name} &b)"

        if body_text is None:
            body = join("return ",
                        " && ".join(f"a.{member.name} {op} b.{member.name}" for member in self._members),
                        ";")
        else:
            body = body_text

        self._add_function(statement, body, indent=indent)

    def _add_eq(self) -> None:
        self._add_return_op("==", 1)
        self._add_return_op("!=", 1, "return !(a == b);")

    def _add_order(self) -> None:
        # check if we already added == and !=
        if not self._eq:
            self._add_eq()

        self._add_return_op("<", 1)
        self._add_return_op("<=", 1, "return !(a > b);")
        self._add_return_op(">", 1)
        self._add_return_op(">=", 1, "return !(a < b);")

    def _add_getter_and_setter(self) -> None:
        for member in self._members:
            self._add_function(f"{member.datatype} get_{member.name}()", f"return {member.name};", indent=1)
            self._add_function(f"void set_{member.name}(const {member.datatype} &x)", f"{member.name} = x;", indent=1)

    def _add_to_string(self) -> None:
        body = join("return ", " + \" \" + ".join(f"to_string({member.name})" for member in self._members), ";")
        self._add_function(f"std::string to_string(const {self._name} &x)", body, indent=0)

    def _add_printable(self) -> None:
        body = join("return ", "out << ' ' << ", " << ' ' << ".join(member.name for member in self._members), ";")
        self._add_function(f"template<typename U>\nU& operator << (U& out, const {self._name} &x)", body, indent=0)
