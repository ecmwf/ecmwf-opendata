from dataclasses import dataclass
from typing import Optional
from .urls import URLS
from .utils import warning_once


@dataclass
class Source:
    url: str
    name: Optional[str] = None
    accept_ranges: Optional[bool] = None
    accept_multiple_ranges: Optional[bool] = None


def source_factory(
    name: str,
    accept_ranges: Optional[bool],
    accept_multiple_ranges: Optional[bool]
) -> Source:
    """Create a Source instance for the given name or URL.

    Parameters
    ----------
    name : str
        A known source name (e.g. ``"aws"``, ``"azure"``, ``"google"``,
        ``"ecmwf"``) or a full HTTP/HTTPS URL.
    accept_ranges : bool, optional
        Override whether the source supports HTTP range requests.
        ``None`` lets the source infer support from response headers.
    accept_multiple_ranges : bool, optional
        Override whether the source supports multiple byte-range requests
        in a single request. ``None`` lets the source infer support from
        response headers.

    Returns
    -------
    Source
        A :class:`Source` dataclass populated with the resolved URL and
        range settings.

    Raises
    ------
    ValueError
        If `name` is neither a known source name nor an HTTP/HTTPS URL.
    """
    if name in URLS.keys():
        url = URLS[name]
        # special case: cloud storages do not allow for multiple ranges
        if name in ["aws", "azure", "google"]:
            source = Source(
                name=name,
                url=url,
                accept_ranges=True,
                accept_multiple_ranges=False
            )

        # standard case: multiurl infers range request support from response headers
        else:
            source = Source(name=name, url=url)

    # special case: provided name is an url
    elif name.startswith("http://") or name.startswith("https://"):
        warning_once(
            "Unknown source %r. Known sources are %r",
            name,
            list(URLS.keys()),
            did_you_mean=(name, list(URLS.keys())),
        )
        source = Source(url=name)
    else:
        raise ValueError("Unknown source %r" % (name,))

    # override range settings if set
    if accept_ranges is not None:
        source.accept_ranges = accept_ranges
    if accept_multiple_ranges is not None:
        source.accept_multiple_ranges = accept_multiple_ranges
    return source
