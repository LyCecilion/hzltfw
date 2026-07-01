class HzltfwError(Exception):
    """Base application error."""


class CaseNotFoundError(HzltfwError):
    """Raised when a case row cannot be found."""


class EvidenceNotFoundError(HzltfwError):
    """Raised when an evidence row cannot be found."""


class EvidenceSourceNotFoundError(HzltfwError):
    """Raised when an evidence source path does not exist."""
