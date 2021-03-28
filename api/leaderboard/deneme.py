def get_this(boole):
    if boole:
        print("yes")
    else:
        print("no")

x = True
y = False
get_this(x if 5==6 else y)
