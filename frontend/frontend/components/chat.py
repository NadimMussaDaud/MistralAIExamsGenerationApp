import reflex as rx
from frontend.states.state import State


def message_bubble(message: dict, index: int) -> rx.Component:
    is_user = message["role"] == "user"
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=rx.cond(
                    is_user,
                    f"https://api.dicebear.com/9.x/notionists/svg?seed=user",
                    f"https://api.dicebear.com/9.x/initials/svg?seed=AI",
                ),
                class_name="size-8 rounded-full",
            ),
            rx.el.div(
                rx.el.p(
                    rx.cond(is_user, "You", "Assistant"),
                    class_name="font-semibold text-sm",
                ),
                rx.cond(
                    is_user,
                    rx.el.p(message["content"], class_name="text-sm font-medium"),
                    rx.markdown(message["content"], class_name="text-sm font-medium"),
                ),
                class_name="flex flex-col gap-1",
            ),
            class_name="flex items-start gap-3",
        ),
        class_name=rx.cond(is_user, "self-end bg-gray-50", "self-start bg-white"),
        width="fit-content",
        max_width="80%",
        padding="12px",
        border_radius="12px",
    )


def chat_area() -> rx.Component:
    return rx.el.div(
        rx.foreach(State.chat_history, message_bubble),
        class_name="flex flex-col gap-4 p-6 overflow-y-auto flex-grow",
    )


def chat_input() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.cond(
                        State.is_uploading,
                        rx.el.div(rx.spinner(class_name="size-5"), class_name="p-2.5"),
                        rx.upload.root(
                            rx.el.div(
                                rx.icon("paperclip", class_name="size-5 text-gray-600"),
                                class_name="p-2.5 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 cursor-pointer",
                            ),
                            id="upload-pdf",
                            on_drop=State.handle_upload(
                                rx.upload_files(upload_id="upload-pdf")
                            ),
                            border="0px",
                            padding="0px",
                        ),
                    )
                ),
                rx.el.input(
                    placeholder=rx.cond(
                        State.is_uploading,
                        "Uploading file...",
                        rx.cond(
                            State.uploaded_pdf,
                            f"Ask a question about {State.uploaded_pdf}",
                            "Upload a PDF to begin...",
                        ),
                    ),
                    name="question",
                    class_name="w-full text-sm font-medium focus:outline-none bg-transparent",
                    key=State.current_question,
                ),
                rx.el.button(
                    rx.icon(
                        "arrow-up",
                        class_name=rx.cond(
                            State.processing
                            | (State.current_question.strip() == "")
                            | State.is_uploading,
                            "text-gray-400",
                            "text-white",
                        ),
                        width=20,
                        height=20,
                    ),
                    type_="submit",
                    class_name="p-2 rounded-lg bg-gray-900 hover:bg-gray-700",
                    #disabled=State.processing
                    #| (State.current_question.strip() == "")
                    #| State.is_uploading,
                ),
                class_name="flex items-center gap-3 w-full",
            ),
            on_submit=State.answer,
            width="100%",
            reset_on_submit=True,
        ),
        class_name="p-6 flex items-center bg-white border-t border-gray-200",
    )


def chat_topbar() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("file-text", class_name="mr-2", width=18, height=18),
            "Generate Exam",
            type_="button",
            class_name="p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 flex items-center",
            on_click=State.generate_exam,
            disabled=State.processing | State.is_uploading,
        ),
        class_name="flex justify-end items-center p-4 border-b border-gray-200 bg-white",
    )

