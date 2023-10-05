# context_processors.py


def set_section(request):
    path = request.path
    section = None

    if path == "/":
        section = "home"
    elif path == "/about":
        section = "about"
    elif path == "/contact":
        section = "contact"

    return {"section": section}
