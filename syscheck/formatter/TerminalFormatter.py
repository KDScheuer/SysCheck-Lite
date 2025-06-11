def to_terminal(results) -> None:
    GREEN = "\033[92m"
    RESET = "\033[0m"
    print(f"\n{GREEN}System Info:{RESET}")
    for key, value in results.items():
        if isinstance(value, dict):
            print(f"{GREEN}{key.capitalize()}{RESET}:")
            for sub_key, sub_value in value.items():
                print(f"{GREEN} - {sub_key}{RESET}: {sub_value}")
        elif isinstance(value, list):
            print(f"{GREEN}{key.capitalize()}{RESET}:")
            for line in value:
                print(f"    {line}")
        else:
            print(f"{GREEN}{key}{RESET}: {value}")