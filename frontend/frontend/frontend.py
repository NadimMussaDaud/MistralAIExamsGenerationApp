import reflex as rx
from frontend.components.chat import chat_area, chat_input
from frontend.components.navbar import navbar


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            navbar(),
            chat_area(),
            chat_input(),
            class_name="h-screen w-full flex flex-col",
        ),
        class_name="font-['Inter'] bg-[#F7F7F8]",
    )


app = rx.App(
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400..700&display=swap",
            rel="stylesheet",
        ),
    ],
    theme=rx.theme(appearance="light"),
)
app.add_page(index)