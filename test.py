if __name__ == "__main__":
    from core import ClassText, Member

    cls = ClassText("modnum", 2, True, True, True, True, True, True, Member("v", "int"), Member("msg", "string"))
    print(str(cls))
