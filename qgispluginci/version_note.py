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

    def increment_pre_release(self) -> str:
        """Increment the pre-release string."""
        items = self.prerelease.split(".")

        numbers = "".join([i for i in self.prerelease if i.isdigit()])

        if len(items) == 1:
            if numbers:
                return f"{self.prerelease[0:-len(numbers)]}{int(numbers) + 1}"
            else:
                return f"{self.prerelease}.1"

        return f"{items[0]}.{int(numbers) + 1}"

    def next_version(self) -> NamedTuple:
        """Increment the pre-release string or the patch."""
        # "pre" is not supported by QGIS
        # https://github.com/qgis/QGIS/blob/master/python/pyplugin_installer/version_compare.py
        if not self.prerelease:
            return VersionNote(
                major=self.major,
                minor=self.minor,
                patch=str(int(self.patch) + 1),
                prerelease="alpha",
            )

        return VersionNote(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            prerelease=self.increment_pre_release(),
        )
