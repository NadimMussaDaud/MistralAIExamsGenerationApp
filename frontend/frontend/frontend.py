import reflex as rx
from frontend.components.chat import chat_area, chat_input
from frontend.components.navbar import navbar
from frontend.api import api
from fastapi.middleware.cors import CORSMiddleware


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
origins = [
    "https://supreme-disco-qgw5r6jj646hxwgp-3000.app.github.dev",  # Your frontend
    "https://supreme-disco-qgw5r6jj646hxwgp-8006.app.github.dev",  # Your backend
    "https://supreme-disco-qgw5r6jj646hxwgp-8000.app.github.dev",  # Your backend
    "https://supreme-disco-qgw5r6jj646hxwgp-8001.app.github.dev",  # Your backend
    "https://supreme-disco-qgw5r6jj646hxwgp-8002.app.github.dev",  # Your backend
    "https://supreme-disco-qgw5r6jj646hxwgp-8003.app.github.dev",  # Your backend
    "https://supreme-disco-qgw5r6jj646hxwgp-8004.app.github.dev",  # Your backend
    "https://supreme-disco-qgw5r6jj646hxwgp-8005.app.github.dev",  # Your backend
    "http://localhost:3000",  # Local frontend
    "http://localhost:8000",  # Local backend
]

def add_cors_middleware(app: rx.App):

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = rx.App(
    api_transformer=[api, add_cors_middleware],
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
app.add_page(index, route="/")

