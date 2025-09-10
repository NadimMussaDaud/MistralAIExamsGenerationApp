import reflex as rx

config = rx.Config(
    app_name="frontend",
    frontend_port=3000,
       plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)