class BaseExtractor(object):
    """
    Base class for email extractors. Subclass this class to make new extractors to extract new types of information.
    Each extractor should be responsible for extracting different pieces of information (no stable conflict resolution mechanism as of yet).
    """

    @staticmethod
    def extract(data):
        """
        Examine email content and metadata to extract information.

        Argument: a dict with email metadata and raw email content.
        Returns: a new dict with only the extracted data.
        """

        raise NotImplementedError
