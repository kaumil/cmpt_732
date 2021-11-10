class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_numbers(text: str) -> list:
        """
        [
            Function to fetch numbers from string
        ]

        Args:
            text ([str]): [Input String]

        Returns:
            list: [List of fetched numbers]
        """
        return re.findall("[0-9]+", text)

    @staticmethod
    def clean_text(text: str) -> str:
        """
        [
            Function to clean string
        ]

        Args:
            text (str): [Input String]

        Returns:
            str: [Clearned String]
        """
        return text.strip()
