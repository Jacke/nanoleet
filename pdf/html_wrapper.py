from airium import Airium # type: ignore

def wrap() -> str:
    a = Airium() # type: ignore
    a('<!DOCTYPE html>')
    with a.html(lang="pl"):
        with a.head():
            a.meta(charset="utf-8")
            a.title(_t="Airium example")

        with a.body():
            with a.h3(id="id23409231", klass='main_header'):
                a("Hello World.")

    html = str(a)  # casting to string extracts the value
    # or directly to UTF-8 encoded bytes:
    html_bytes = bytes(a)  # casting to bytes is a shortcut to str(a).encode('utf-8')
    print(html)
    return html
