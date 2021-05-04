from typing import NamedTuple


class VersionNote(NamedTuple):
    major: str = None
    minor: str = None
    patch: str = None
    url: str = None
    prerelease: str = None
    separator: str = None
    date: str = None
    text_raw: str = None

    @property
    def text(self) -> str:
        """Remove many \n at the start and end of the string."""
        return self.text_raw.strip()

    @property
    def is_prerelease(self) -> bool:
        if self.prerelease and len(self.prerelease):
            return True
        else:
            return False

    @property
    def version(self) -> str:
        if self.prerelease:
            return f"{self.major}.{self.minor}.{self.patch}-{self.prerelease}"
        else:
            return f"{self.major}.{self.minor}.{self.patch}"
