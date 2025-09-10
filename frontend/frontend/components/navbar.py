import reflex as rx
from frontend.states.state import State


def navbar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("file-text", class_name="size-6"),
            rx.el.p("PDF Assistant & Exam Generator", class_name="font-semibold text-lg"),
            class_name="flex items-center gap-3",
        ),
        # Right side: Generate Exam button
        rx.el.button(
            rx.icon("file-text", class_name="size-6 mr-2 text-white"),
            "Generate Exam",
            class_name="p-2 text-white rounded-lg bg-gray-900 hover:bg-gray-700 flex items-center",
            variant="solid",
            on_click=State.generate_exam,
            disabled=(State.uploaded_pdf.strip() == "" | State.processing | State.is_uploading),
        ),
        class_name="w-full flex justify-between items-center py-3 px-6 border-b border-gray-200",
    )