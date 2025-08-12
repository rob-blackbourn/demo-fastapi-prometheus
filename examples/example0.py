from fast_api_ex1.constants import APP_NAME, VERSION, HOST, FQDN


def main() -> None:
    print(APP_NAME, FQDN, HOST, VERSION)


if __name__ == "__main__":
    main()
