from sqlalchemy import func

from backend.analysis import analyze_opportunity
from database.connection import SessionLocal
from database.models import CandidateProfile, Company, Opportunity, SearchHistory


def save_search_results(query, results):
    session = SessionLocal()
    added = 0
    try:
        profile = session.get(CandidateProfile, 1)
        profile_skills = (profile.skills.split(",") if profile and profile.skills else [])
        for result in results:
            if session.query(Opportunity).filter_by(url=result.url).first():
                continue
            analysis = analyze_opportunity(result.title, result.snippet, profile_skills)
            session.add(Opportunity(
                title=result.title,
                company_name="Unknown",
                location="",
                source=result.source,
                url=result.url,
                snippet=result.snippet,
                skills=", ".join(analysis["skills"]),
                is_pfe=analysis["is_pfe"],
                score=analysis["score"],
            ))
            added += 1
        session.add(SearchHistory(query=query, source="DuckDuckGo HTML", result_count=len(results), status="completed"))
        session.commit()
        return added
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def add_manual_opportunity(title, url, company_name="Unknown", location="", snippet="", source="Manual"):
    from backend.deduplication import canonical_url

    normalized_url = canonical_url(url)
    if not title.strip() or not normalized_url.startswith(("http://", "https://")):
        raise ValueError("A title and valid HTTP(S) URL are required.")
    session = SessionLocal()
    try:
        existing = session.query(Opportunity).filter_by(url=normalized_url).first()
        if existing:
            return False
        analysis = analyze_opportunity(title, snippet)
        session.add(Opportunity(
            title=title.strip(), url=normalized_url, company_name=company_name.strip() or "Unknown",
            location=location.strip(), snippet=snippet.strip(), source=source,
            skills=", ".join(analysis["skills"]), is_pfe=analysis["is_pfe"], score=analysis["score"],
        ))
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def list_opportunities(search_text=""):
    session = SessionLocal()
    try:
        query = session.query(Opportunity)
        if search_text.strip():
            like = f"%{search_text.strip()}%"
            query = query.filter((Opportunity.title.ilike(like)) | (Opportunity.company_name.ilike(like)) | (Opportunity.location.ilike(like)))
        return query.order_by(Opportunity.created_at.desc()).all()
    finally:
        session.close()


def update_opportunity(opportunity_id, **changes):
    session = SessionLocal()
    try:
        row = session.get(Opportunity, opportunity_id)
        if not row:
            return False
        for key in ("status", "notes"):
            if key in changes:
                setattr(row, key, changes[key])
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def mark_opportunities_seen():
    session = SessionLocal()
    try:
        session.query(Opportunity).filter(Opportunity.is_new.is_(True)).update(
            {Opportunity.is_new: False}, synchronize_session=False
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_company(name, city, region, source_url, description=""):
    session = SessionLocal()
    try:
        existing = session.query(Company).filter(func.lower(Company.name) == name.lower(), Company.city == city).first()
        if existing:
            return False
        session.add(Company(name=name, city=city, region=region, source_url=source_url, description=description, verified=False))
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
