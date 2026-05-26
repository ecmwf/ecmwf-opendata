import logging

LOG = logging.getLogger(__name__)

ONCE = set()

_ATTRIBUTION_SHOWN = False  # module-level guard to avoid spamming


def _show_attribution_message():
    global _ATTRIBUTION_SHOWN
    if not _ATTRIBUTION_SHOWN:
        print(
            "By downloading data from the ECMWF open data dataset, you agree to "
            "the terms: Attribution 4.0 International (CC BY 4.0). Please "
            "attribute ECMWF when downloading this data."
        )
        _ATTRIBUTION_SHOWN = True


def warning_once(*args, did_you_mean=None):
    if repr(args) in ONCE:
        return

    LOG.warning(*args)

    ONCE.add(repr(args))

    if did_you_mean:
        words, vocabulary = did_you_mean

        def levenshtein(a, b):
            if len(a) == 0:
                return len(b)

            if len(b) == 0:
                return len(a)

            if a[0].lower() == b[0].lower():
                return levenshtein(a[1:], b[1:])

            return 1 + min(
                [
                    levenshtein(a[1:], b[1:]),
                    levenshtein(a[1:], b),
                    levenshtein(a, b[1:]),
                ]
            )

        if not isinstance(words, (list, tuple)):
            words = [words]

        for word in words:
            distance, best = min((levenshtein(word, w), w) for w in vocabulary)
            if distance < min(len(word), len(best)):
                LOG.warning(
                    "Did you mean %r instead of %r?",
                    best,
                    word,
                )
