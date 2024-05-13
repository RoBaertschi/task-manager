import pytermgui as ptg


CONFIG = ""
with open("ui.yaml") as CONFIG_FILE:
    CONFIG = CONFIG_FILE.read()


with ptg.YamlLoader() as loader:
    loader.load(CONFIG)

with ptg.WindowManager() as manager:
    window = (
        ptg.Window(
            "",
            ptg.Splitter(
                    [
                        ".---.",
                        "| x |",
                        "`---`",
                    ],
            
                    [
                        ".---.",
                        "| x |",
                        "`---`",
                    ]
            ),
            "",
            width=60,
            box="DOUBLE",
        )
        .set_title("[210 bold]New contact")
        .center()
    )

    manager.add(window)
