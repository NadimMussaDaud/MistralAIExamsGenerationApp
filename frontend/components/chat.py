import reflex as rx
from ..state import State  # Import the central state

def qa(question: str, answer: str) -> rx.Component:
    """A component to display a single Q&A pair in a chat bubble."""
    return rx.box(
        rx.box(
            rx.text(question, text_align="right"),
            background="#F0F4F8",
            padding="1em",
            border_radius="8px",
            margin_left="20%",  # Push it to the right for the user
        ),
        rx.box(
            rx.text(answer, text_align="left"),
            background="#DBEAFE",  # A different color for the AI's answer
            padding="1em",
            border_radius="8px",
            margin_right="20%",  # Push it to the left for the AI
        ),
        width="100%",
        margin_y="1em",
    )

def chat_interface() -> rx.Component:
    """The main chat interface component."""
    return rx.box(
        # Header with a clear chat button
        rx.hstack(
            rx.heading("Chat with Your Notes", size="5"),
            rx.icon_button(
                rx.icon("trash"),  # Use a trash icon
                on_click=State.clear_chat,  # Connect to a handler in State
                color_scheme="red",  # Make it red for a destructive action
                variant="soft"
            ),
            justify="between",  # Put space between the title and button
            align="center",
            margin_bottom="2em",
            width="100%"
        ),
        
        # Scrollable chat history area
        rx.box(
            rx.cond(  # Show a message if the chat is empty
                State.chat_history.length() == 0,
                rx.center(
                    rx.vstack(
                        rx.icon("message-square", size=40),
                        rx.text("Your conversation will appear here."),
                        align="center",
                        color="gray",
                    ),
                    height="20em",
                ),
                rx.box(  # Show the chat history if not empty
                    rx.foreach(
                        State.chat_history,
                        lambda msg: qa(msg["question"], msg["answer"])
                    ),
                    padding="1em",
                    height="30em",  # Fixed height for the scroll area
                    overflow_y="auto",  # Make it scrollable
                ),
            ),
            width="100%",
            margin_bottom="2em",
        ),
        
        # Upload and Input Section
        rx.vstack(
            # File upload for PDFs
            rx.upload(
                rx.vstack(
                    rx.icon("upload", size=30),
                    rx.text("Drag and drop a PDF or click to browse"),
                    align="center",
                    spacing="2",
                ),
                border="1px dotted rgb(107, 99, 246)",
                padding="2em",
                border_radius="8px",
                on_drop=State.handle_upload,  # Handle file upload
                id="upload_area",
                width="100%",
            ),
            
            # Display the name of the uploaded file
            rx.cond(
                State.uploaded_file,
                rx.text(f"Ready: {State.uploaded_file}", size="2", color="green"),
            ),
            
            # Text input for questions
            rx.form(
                rx.hstack(
                    rx.input(
                        placeholder="Ask me anything about your notes...",
                        name="question",  # Important for form submission
                        width="100%",
                        is_disabled=State.is_loading,  # Disable while processing
                    ),
                    rx.icon_button(
                        rx.icon("arrow-up"),
                        type="submit",
                        is_loading=State.is_loading,  # Show spinner on loading
                    ),
                ),
                on_submit=State.answer_question,  # Handle form submission
                reset_on_submit=True,  # Clear the input after submit
                width="100%",
            ),
            width="100%",
            spacing="4",
        ),
        width="100%",
        padding="2em",
    )