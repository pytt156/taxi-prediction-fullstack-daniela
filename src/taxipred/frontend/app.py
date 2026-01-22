from __future__ import annotations

from taxipred.frontend import ui

MAX_DISTANCE_KM = 50.0


def main() -> None:
    ui.configure_page()
    ui.render_header()
    ui.render_app(MAX_DISTANCE_KM)


if __name__ == "__main__":
    main()
