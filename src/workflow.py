def basis(shell) -> None:
    try:
        shell.do_api("select OpenMeteoAPI")
        shell.do_config("fetch open-meteo")
        shell.do_api("up")
    except Exception as e:
        print(f"An error occurred: {e}")
