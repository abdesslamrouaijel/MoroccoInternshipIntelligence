import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.analysis import analyze_opportunity
from backend.deduplication import canonical_url, is_duplicate
from backend.exports import export_opportunities
from backend.search import SearchResult
from database.connection import Base
from database.models import CandidateProfile, Opportunity
import services.opportunity_service as opportunity_service


def test_analysis_detects_pfe_and_profile_skills():
    result = analyze_opportunity(
        "Stage PFE Data Science",
        "Final year engineering internship using Python and Pandas",
        ["Python", "Pandas"],
    )
    assert result["is_pfe"] is True
    assert result["matching_skills"] == ["Python", "Pandas"]
    assert result["score"] > 0


def test_canonical_url_and_title_company_deduplication():
    assert canonical_url("https://www.example.ma/jobs/1/?utm_source=x") == "https://example.ma/jobs/1"
    existing = [{"url": "https://example.ma/jobs/1", "title": "Stage PFE", "company_name": "Acme", "location": "Rabat"}]
    assert is_duplicate({"url": "https://www.example.ma/jobs/1?ref=x"}, existing)
    assert is_duplicate({"title": "Stage PFE", "company_name": "Acme", "location": "Rabat"}, existing)


def test_database_saves_search_results_and_skips_duplicate(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(opportunity_service, "SessionLocal", TestSession)
    with TestSession() as session:
        session.add(CandidateProfile(id=1, skills="Python, Pandas"))
        session.commit()
    result = SearchResult("Stage PFE Python", "https://example.ma/job/1", "Stage PFE Python", "example.ma")
    assert opportunity_service.save_search_results("stage PFE", [result]) == 1
    assert opportunity_service.save_search_results("stage PFE", [result]) == 0
    with TestSession() as session:
        saved = session.query(Opportunity).one()
        assert saved.is_pfe is True
        assert saved.skills == "Python"
        assert saved.is_new is True
    opportunity_service.mark_opportunities_seen()
    with TestSession() as session:
        assert session.query(Opportunity).one().is_new is False


def test_export_csv_and_json(tmp_path):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    with TestSession() as session:
        row = Opportunity(title="Stage PFE", url="https://example.ma/job", company_name="Acme", score=80)
        session.add(row)
        session.flush()
        csv_path = export_opportunities([row], "csv", tmp_path)
        json_path = export_opportunities([row], "json", tmp_path)
    assert "Stage PFE" in csv_path.read_text(encoding="utf-8-sig")
    assert json.loads(json_path.read_text(encoding="utf-8"))[0]["score"] == 80


def test_export_xlsx_and_pdf(tmp_path):
    row = Opportunity(title="Stage PFE", url="https://example.ma/job", company_name="Acme", score=80)
    assert export_opportunities([row], "xlsx", tmp_path).stat().st_size > 0
    assert export_opportunities([row], "pdf", tmp_path).stat().st_size > 0


def test_manual_import_validates_and_normalizes_url(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'manual.db'}")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(opportunity_service, "SessionLocal", TestSession)
    assert opportunity_service.add_manual_opportunity(
        "PFE Python", "https://www.example.ma/job/1?ref=mail", "Acme", "Rabat", "Stage PFE Python"
    )
    assert not opportunity_service.add_manual_opportunity(
        "PFE Python", "https://example.ma/job/1", "Acme", "Rabat", "Stage PFE Python"
    )
    with TestSession() as session:
        assert session.query(Opportunity).one().url == "https://example.ma/job/1"


def test_public_search_extracts_result_fields(monkeypatch):
    class Response:
        text = """
        <div class="result">
          <a class="result__a" href="https://careers.example.ma/job/1">Stage PFE</a>
          <a class="result__snippet">Python engineering internship</a>
        </div>
        """

        def raise_for_status(self):
            pass

    monkeypatch.setattr("backend.search.requests.get", lambda *args, **kwargs: Response())
    from backend.search import PublicWebSearch

    results = PublicWebSearch().search("stage PFE")
    assert results == [SearchResult(
        title="Stage PFE",
        url="https://careers.example.ma/job/1",
        snippet="Python engineering internship",
        source="careers.example.ma",
    )]
