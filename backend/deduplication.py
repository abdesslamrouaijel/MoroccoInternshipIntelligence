from urllib.parse import urlsplit, urlunsplit


def canonical_url(url):
    parts = urlsplit((url or "").strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower().removeprefix("www."), parts.path.rstrip("/"), "", ""))


def is_duplicate(candidate, existing):
    candidate_url = canonical_url(candidate.get("url", ""))
    if candidate_url and any(canonical_url(row.get("url", "")) == candidate_url for row in existing):
        return True
    title = " ".join(candidate.get("title", "").lower().split())
    company = candidate.get("company_name", "").lower().strip()
    return any(
        title and title == " ".join(row.get("title", "").lower().split())
        and company == row.get("company_name", "").lower().strip()
        and candidate.get("location", "").lower().strip() == row.get("location", "").lower().strip()
        for row in existing
    )
