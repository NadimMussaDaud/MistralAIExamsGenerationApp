import reflex as rx


def navbar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("file-text", class_name="size-6"),
            rx.el.p("PDF Assistant", class_name="font-semibold text-lg"),
            class_name="flex items-center gap-3",
        ),
        class_name="w-full flex justify-between items-center py-3 px-6 border-b border-gray-200",
    )