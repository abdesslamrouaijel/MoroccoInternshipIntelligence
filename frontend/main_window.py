import sys
import webbrowser

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QMainWindow, QMessageBox, QPushButton, QProgressBar, QStackedWidget,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)
from urllib.parse import quote

from backend.exports import export_opportunities
from backend.search import PublicWebSearch
from config.settings import REGIONS, SEARCH_TERMS
from database.connection import SessionLocal, initialize_database
from database.models import CandidateProfile, Company, Opportunity
from services.opportunity_service import (
    add_manual_opportunity, list_opportunities, mark_opportunities_seen, save_company,
    save_search_results, update_opportunity,
)


class SearchWorker(QThread):
    results_ready = Signal(str, object)
    failed = Signal(str)
    finished_search = Signal()

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            results = PublicWebSearch().search(self.query, limit=30, timeout=20)
            if not self.isInterruptionRequested():
                self.results_ready.emit(self.query, results)
        except Exception as exc:
            self.failed.emit(f"Public web search failed: {exc}")
        finally:
            self.finished_search.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        initialize_database()
        self.setWindowTitle("Morocco Internship Intelligence")
        self.resize(1380, 860)
        self.setMinimumSize(1080, 700)
        self.search_results = []
        root = QWidget()
        root.setObjectName("mainShell")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(258)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 24, 18, 20)
        sidebar_layout.setSpacing(12)
        brand = QHBoxLayout()
        brand_mark = QLabel("M")
        brand_mark.setObjectName("brandMark")
        brand_copy = QVBoxLayout()
        brand_title = QLabel("MOROCCO")
        brand_title.setObjectName("brandTitle")
        brand_subtitle = QLabel("INTERNSHIP INTELLIGENCE")
        brand_subtitle.setObjectName("brandSubtitle")
        brand_copy.addWidget(brand_title)
        brand_copy.addWidget(brand_subtitle)
        brand.addWidget(brand_mark)
        brand.addLayout(brand_copy)
        brand.addStretch()
        sidebar_layout.addLayout(brand)
        sidebar_layout.addSpacing(20)
        section_label = QLabel("WORKSPACE")
        section_label.setObjectName("navSection")
        sidebar_layout.addWidget(section_label)
        self.navigation = QListWidget()
        self.navigation.addItems([
            "Dashboard", "Internship Market Search", "LinkedIn & Recruitment Monitoring",
            "Companies by Region", "Recruitment Analysis", "Saved Opportunities",
            "Company Database", "Reports & Exports", "Settings",
        ])
        self.navigation.setFrameShape(QFrame.Shape.NoFrame)
        self.navigation.setSpacing(5)
        self.navigation.setUniformItemSizes(True)
        self.navigation.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sidebar_layout.addWidget(self.navigation, 1)
        sidebar_footer = QLabel("LOCAL WORKSPACE\nYour research stays on this device.")
        sidebar_footer.setObjectName("sidebarFooter")
        sidebar_layout.addWidget(sidebar_footer)

        self.pages = QStackedWidget()
        for builder in (
            self.dashboard_page, self.market_page, self.linkedin_page,
            self.region_page, self.analysis_page, self.opportunities_page,
            self.companies_page, self.reports_page, self.settings_page,
        ):
            self.pages.addWidget(builder())
        self.navigation.currentRowChanged.connect(self.on_navigation_changed)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(32, 16, 32, 16)
        self.breadcrumb = QLabel("DASHBOARD")
        self.breadcrumb.setObjectName("breadcrumb")
        self.workspace_badge = QLabel("●  LOCAL DATABASE")
        self.workspace_badge.setObjectName("workspaceBadge")
        topbar_layout.addWidget(self.breadcrumb)
        topbar_layout.addStretch()
        topbar_layout.addWidget(self.workspace_badge)
        content_layout.addWidget(topbar)
        content_layout.addWidget(self.pages, 1)
        layout.addWidget(sidebar)
        layout.addWidget(content, 1)
        self.setCentralWidget(root)
        self.statusBar().showMessage("Ready")
        self.statusBar().setSizeGripEnabled(False)
        self.navigation.setCurrentRow(0)
        self.setStyleSheet("""
            * { font-family: "Segoe UI"; font-size: 10pt; }
            QWidget#mainShell { background: #f3f6fb; }
            QFrame#sidebar { background: #12243a; }
            QLabel#brandMark {
                background: #2d80d3; color: white; border-radius: 9px;
                font-size: 17pt; font-weight: 700; min-width: 42px; max-width: 42px;
                min-height: 42px; max-height: 42px; qproperty-alignment: AlignCenter;
            }
            QLabel#brandTitle { color: white; font-size: 10pt; font-weight: 700; letter-spacing: 1px; }
            QLabel#brandSubtitle { color: #8ea5bf; font-size: 7pt; letter-spacing: 1px; }
            QLabel#navSection { color: #7188a4; font-size: 8pt; font-weight: 700; padding-left: 9px; }
            QListWidget { background: transparent; color: #b7c5d6; border: 0; outline: 0; }
            QListWidget::item { padding: 13px 12px; border-radius: 7px; min-height: 20px; }
            QListWidget::item:hover { background: #1d3550; color: white; }
            QListWidget::item:selected { background: #245486; color: white; font-weight: 600; }
            QLabel#sidebarFooter {
                color: #7f94ad; font-size: 8pt; line-height: 1.6;
                padding: 13px 10px; border-top: 1px solid #283b52;
            }
            QFrame#topbar { background: white; border-bottom: 1px solid #e6ebf2; }
            QLabel#breadcrumb { color: #60738b; font-size: 8pt; font-weight: 700; letter-spacing: 1px; }
            QLabel#workspaceBadge {
                color: #277554; background: #eaf6ef; border-radius: 12px;
                padding: 7px 11px; font-size: 8pt; font-weight: 700;
            }
            QWidget#page { background: #f3f6fb; }
            QLabel#pageTitle { color: #162a43; font-size: 23pt; font-weight: 650; }
            QLabel#pageSubtitle { color: #718198; font-size: 10pt; }
            QLabel#eyebrow { color: #397bb8; font-size: 8pt; font-weight: 700; letter-spacing: 1px; }
            QLabel#statCard {
                background: white; color: #1a2e47; border: 1px solid #e6ebf2;
                border-radius: 10px; padding: 18px; font-size: 13pt; font-weight: 600;
            }
            QLabel#sectionTitle { color: #1b2f48; font-size: 13pt; font-weight: 650; }
            QPushButton {
                background: #256eaf; color: white; border: 1px solid #256eaf;
                padding: 10px 15px; border-radius: 6px; font-weight: 600;
            }
            QPushButton:hover { background: #1b5d98; border-color: #1b5d98; }
            QPushButton:pressed { background: #154b7d; }
            QPushButton:disabled { background: #a9bed1; border-color: #a9bed1; color: #eef3f8; }
            QPushButton[secondary="true"] { background: white; color: #38536f; border-color: #d7e0ea; }
            QPushButton[secondary="true"]:hover { background: #f3f7fb; border-color: #9eb4ca; }
            QLineEdit, QTextEdit, QComboBox {
                background: white; color: #24364c; padding: 9px 11px;
                border: 1px solid #dce4ee; border-radius: 6px;
                selection-background-color: #cfe4f8;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #3985c5; }
            QTableWidget {
                background: white; alternate-background-color: #f8fafd;
                color: #27394f; border: 1px solid #e5eaf1; border-radius: 8px;
                gridline-color: transparent; selection-background-color: #e7f1fb;
                selection-color: #173c60; outline: 0;
            }
            QHeaderView::section {
                background: #f5f8fc; color: #62758d; padding: 11px 9px;
                border: 0; border-bottom: 1px solid #e5eaf1; font-size: 8pt; font-weight: 700;
            }
            QTableWidget::item { padding: 7px; border-bottom: 1px solid #eef1f5; }
            QProgressBar { background: #e4ecf5; border: 0; border-radius: 4px; min-height: 7px; max-height: 7px; }
            QProgressBar::chunk { background: #3985c5; border-radius: 4px; }
            QStatusBar { background: white; color: #718198; border-top: 1px solid #e6ebf2; }
        """)
        self.refresh_dashboard()

    @staticmethod
    def page(title, subtitle=""):
        widget = QWidget()
        widget.setObjectName("page")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(34, 30, 34, 24)
        layout.setSpacing(18)
        eyebrow = QLabel("MOROCCO INTERNSHIP INTELLIGENCE")
        eyebrow.setObjectName("eyebrow")
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        heading.setWordWrap(True)
        layout.addWidget(eyebrow)
        layout.addWidget(heading)
        if subtitle:
            description = QLabel(subtitle)
            description.setObjectName("pageSubtitle")
            description.setWordWrap(True)
            layout.addWidget(description)
        return widget, layout

    def dashboard_page(self):
        page, layout = self.page("Dashboard", "Your saved recruitment intelligence at a glance.")
        stats = QHBoxLayout()
        stats.setSpacing(14)
        self.opportunity_stat = QLabel()
        self.company_stat = QLabel()
        self.new_stat = QLabel()
        for card in (self.opportunity_stat, self.company_stat, self.new_stat):
            card.setObjectName("statCard")
            card.setMinimumHeight(78)
            stats.addWidget(card, 1)
        layout.addLayout(stats)
        section_heading = QLabel("Recently discovered")
        section_heading.setObjectName("sectionTitle")
        layout.addWidget(section_heading)
        self.dashboard_table = QTableWidget(0, 4)
        self.dashboard_table.setHorizontalHeaderLabels(["Title", "Company", "Location", "Status"])
        self.configure_table(self.dashboard_table)
        layout.addWidget(self.dashboard_table)
        return page

    def refresh_dashboard(self):
        if not hasattr(self, "opportunity_stat"):
            return
        rows = list_opportunities()
        session = SessionLocal()
        try:
            companies = session.query(Company).count()
        finally:
            session.close()
        new_count = sum(1 for row in rows if row.is_new)
        self.opportunity_stat.setText(f"{len(rows)}\nOpportunities")
        self.company_stat.setText(f"{companies}\nCompany leads")
        self.new_stat.setText(f"{new_count}\nNew discoveries")
        self.fill_table(self.dashboard_table, [
            [row.title, row.company_name, row.location, row.status] for row in rows[:12]
        ])

    def on_navigation_changed(self, index):
        if index < 0:
            return
        self.pages.setCurrentIndex(index)
        page_name = self.navigation.item(index).text()
        self.breadcrumb.setText(page_name.upper())
        self.statusBar().showMessage(f"{page_name}  ·  Local data")
        if page_name == "Saved Opportunities":
            self.refresh_opportunities()
            try:
                mark_opportunities_seen()
                self.refresh_dashboard()
            except Exception as exc:
                QMessageBox.warning(self, "Database error", f"Could not mark offers as seen: {exc}")
        elif page_name == "Company Database":
            session = SessionLocal()
            try:
                rows = session.query(Company).order_by(Company.name).all()
                self.fill_table(self.companies_table, [
                    [r.name, r.city, r.region, r.size, "Yes" if r.verified else "No"] for r in rows
                ])
            finally:
                session.close()

    def market_page(self):
        page, layout = self.page("Explore the Moroccan Internship Market",
                                  "Search publicly indexed pages. Results are source links, not verified job postings.")
        row = QHBoxLayout()
        self.market_query = QLineEdit(SEARCH_TERMS[0])
        self.market_query.setPlaceholderText("Search jobs, skills, locations...")
        row.addWidget(self.market_query, 1)
        search_button = QPushButton("GO EXPLORE THE MARKET")
        search_button.clicked.connect(lambda: self.start_search(self.market_query.text()))
        self.market_start = search_button
        row.addWidget(search_button)
        self.market_stop = QPushButton("Stop")
        self.market_stop.clicked.connect(self.stop_search)
        self.market_stop.setEnabled(False)
        row.addWidget(self.market_stop)
        layout.addLayout(row)
        self.market_progress = QProgressBar()
        self.market_progress.setRange(0, 0)
        self.market_progress.hide()
        layout.addWidget(self.market_progress)
        self.market_table = QTableWidget(0, 4)
        self.market_table.setHorizontalHeaderLabels(["Title", "Source", "Link", "Snippet"])
        self.market_table.horizontalHeader().setStretchLastSection(True)
        self.configure_table(self.market_table)
        self.market_table.cellDoubleClicked.connect(lambda r, c: self.open_result(self.market_table, r, 2))
        layout.addWidget(self.market_table)
        return page

    def start_search(self, query):
        if hasattr(self, "worker") and self.worker.isRunning():
            return
        if not query.strip():
            QMessageBox.warning(self, "Search", "Enter a search phrase.")
            return
        self.market_progress.show()
        self.market_start.setEnabled(False)
        self.market_stop.setEnabled(True)
        self.worker = SearchWorker(query.strip())
        self.worker.results_ready.connect(self.on_search_results)
        self.worker.failed.connect(lambda message: QMessageBox.warning(self, "Search error", message))
        self.worker.finished_search.connect(self.on_search_finished)
        self.worker.start()

    def stop_search(self):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.quit()
            self.market_stop.setEnabled(False)
            self.market_progress.setFormat("Finishing current request…")

    def on_search_results(self, query, results):
        self.search_results = results
        self.fill_table(self.market_table, [[r.title, r.source, r.url, r.snippet] for r in results])
        try:
            added = save_search_results(query, results)
        except Exception as exc:
            QMessageBox.warning(self, "Database error", f"Search results were found but could not be saved: {exc}")
            return
        self.refresh_dashboard()
        QMessageBox.information(self, "Search complete", f"{len(results)} public results returned; {added} new links saved.")

    def on_search_finished(self):
        self.market_progress.hide()
        self.market_progress.setFormat("%p%")
        self.market_stop.setEnabled(False)
        self.market_start.setEnabled(True)

    def linkedin_page(self):
        page, layout = self.page(
            "LinkedIn & Recruitment Monitoring",
            "LinkedIn access is not automated. This app does not bypass login, CAPTCHA, or access restrictions.",
        )
        layout.addWidget(QLabel("Open a public LinkedIn job search in your browser, or paste a public job URL below."))
        query = QLineEdit("Stage PFE 2027 Morocco")
        open_button = QPushButton("Open LinkedIn search in browser")
        open_button.clicked.connect(lambda: webbrowser.open(
            "https://www.linkedin.com/jobs/search/?keywords=" + quote(query.text())
        ))
        layout.addWidget(query)
        layout.addWidget(open_button)
        form = QFormLayout()
        self.manual_title = QLineEdit()
        self.manual_company = QLineEdit()
        self.manual_location = QLineEdit()
        self.manual_url = QLineEdit()
        self.manual_text = QTextEdit()
        form.addRow("Offer title", self.manual_title)
        form.addRow("Company", self.manual_company)
        form.addRow("Location", self.manual_location)
        form.addRow("Public offer URL", self.manual_url)
        form.addRow("Copied announcement text", self.manual_text)
        layout.addLayout(form)
        import_button = QPushButton("Import manually")
        import_button.clicked.connect(self.import_manual)
        layout.addWidget(import_button)
        return page

    def import_manual(self):
        try:
            added = add_manual_opportunity(
                self.manual_title.text(), self.manual_url.text(), self.manual_company.text(),
                self.manual_location.text(), self.manual_text.toPlainText(),
            )
            if not added:
                QMessageBox.information(self, "Already saved", "This opportunity URL is already in your database.")
                return
            QMessageBox.information(self, "Imported", "Opportunity saved for tracking.")
            self.refresh_dashboard()
            self.refresh_opportunities()
        except Exception as exc:
            QMessageBox.warning(self, "Import failed", str(exc))

    def region_page(self):
        page, layout = self.page("Discover Companies by Region",
                                 "Search-engine listings are unverified leads; save only the companies you have reviewed.")
        form = QHBoxLayout()
        self.region_combo = QComboBox()
        self.region_combo.addItems(REGIONS)
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("City (optional)")
        form.addWidget(self.region_combo)
        form.addWidget(self.city_edit)
        button = QPushButton("FIND COMPANIES")
        button.clicked.connect(self.search_companies)
        form.addWidget(button)
        layout.addLayout(form)
        self.company_search_table = QTableWidget(0, 3)
        self.company_search_table.setHorizontalHeaderLabels(["Search result", "Source", "URL"])
        self.company_search_table.horizontalHeader().setStretchLastSection(True)
        self.configure_table(self.company_search_table)
        layout.addWidget(self.company_search_table)
        save_button = QPushButton("Save selected result as unverified company lead")
        save_button.clicked.connect(self.save_selected_company)
        layout.addWidget(save_button)
        return page

    def search_companies(self):
        city = self.city_edit.text().strip()
        region = self.region_combo.currentText()
        place = city or region
        query = f"large companies employers industry careers {place} Morocco"
        try:
            self.company_results = PublicWebSearch().search(query, limit=30)
            self.fill_table(self.company_search_table, [[r.title, r.source, r.url] for r in self.company_results])
        except Exception as exc:
            QMessageBox.warning(self, "Company search failed", str(exc))

    def save_selected_company(self):
        row = self.company_search_table.currentRow()
        if row < 0 or row >= len(getattr(self, "company_results", [])):
            QMessageBox.warning(self, "Select a result", "Choose a search result first.")
            return
        result = self.company_results[row]
        city = self.city_edit.text().strip()
        try:
            saved = save_company(result.title, city, self.region_combo.currentText(), result.url, result.snippet)
            QMessageBox.information(self, "Company lead", "Saved as unverified." if saved else "This lead already exists.")
        except Exception as exc:
            QMessageBox.warning(self, "Save failed", str(exc))

    def analysis_page(self):
        page, layout = self.page("Recruitment Analysis",
                                 "Rule-based relevance indicators; scores are not probabilities of recruitment.")
        layout.addWidget(QLabel("Opportunities are scored on explicit PFE wording, academic compatibility, and detected profile skills."))
        self.analysis_table = QTableWidget(0, 4)
        self.analysis_table.setHorizontalHeaderLabels(["Title", "PFE", "Score / 100", "Required skills"])
        self.configure_table(self.analysis_table)
        layout.addWidget(self.analysis_table)
        self.fill_analysis()
        return page

    def fill_analysis(self):
        if not hasattr(self, "analysis_table"):
            return
        rows = list_opportunities()
        self.fill_table(self.analysis_table, [[r.title, "Yes" if r.is_pfe else "Not identified", f"{r.score:.0f}", r.skills] for r in rows])

    def opportunities_page(self):
        page, layout = self.page("Saved Opportunities", "Track your applications and add private notes.")
        controls = QHBoxLayout()
        self.opportunity_filter = QLineEdit()
        self.opportunity_filter.setPlaceholderText("Filter saved offers")
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_opportunities)
        controls.addWidget(self.opportunity_filter, 1)
        controls.addWidget(refresh)
        layout.addLayout(controls)
        self.opportunity_table = QTableWidget(0, 7)
        self.opportunity_table.setHorizontalHeaderLabels(["ID", "Title", "Company", "Location", "Score", "Status", "URL"])
        self.opportunity_table.setColumnHidden(0, True)
        self.opportunity_table.setColumnHidden(6, True)
        self.configure_table(self.opportunity_table)
        self.opportunity_table.cellDoubleClicked.connect(lambda r, c: self.open_result(self.opportunity_table, r, 6))
        layout.addWidget(self.opportunity_table)
        actions = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Discovered", "To Apply", "Applied", "Interview", "Accepted", "Rejected", "Expired"])
        save_status = QPushButton("Update selected status")
        save_status.clicked.connect(self.change_status)
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Personal notes for selected offer")
        save_notes = QPushButton("Save notes")
        save_notes.clicked.connect(self.change_notes)
        actions.addWidget(self.status_combo)
        actions.addWidget(save_status)
        actions.addWidget(self.notes_edit, 1)
        actions.addWidget(save_notes)
        layout.addLayout(actions)
        self.refresh_opportunities()
        return page

    def refresh_opportunities(self):
        if not hasattr(self, "opportunity_table"):
            return
        self.opportunity_rows = list_opportunities(self.opportunity_filter.text())
        self.fill_table(self.opportunity_table, [
            [r.id, f"{'NEW · ' if r.is_new else ''}{r.title}", r.company_name, r.location, f"{r.score:.0f}", r.status, r.url]
            for r in self.opportunity_rows
        ])
        self.refresh_dashboard()
        self.fill_analysis()

    def change_status(self):
        row = self.opportunity_table.currentRow()
        if row < 0:
            return
        opportunity_id = int(self.opportunity_table.item(row, 0).text())
        update_opportunity(opportunity_id, status=self.status_combo.currentText())
        self.refresh_opportunities()

    def change_notes(self):
        row = self.opportunity_table.currentRow()
        if row < 0:
            return
        opportunity_id = int(self.opportunity_table.item(row, 0).text())
        update_opportunity(opportunity_id, notes=self.notes_edit.text())
        QMessageBox.information(self, "Saved", "Notes updated.")

    def companies_page(self):
        page, layout = self.page("Company Database", "Company size and verification are never inferred from search snippets.")
        self.companies_table = QTableWidget(0, 5)
        self.companies_table.setHorizontalHeaderLabels(["Company", "City", "Region", "Size", "Verified"])
        self.configure_table(self.companies_table)
        layout.addWidget(self.companies_table)
        session = SessionLocal()
        try:
            rows = session.query(Company).order_by(Company.name).all()
            self.fill_table(self.companies_table, [[r.name, r.city, r.region, r.size, "Yes" if r.verified else "No"] for r in rows])
        finally:
            session.close()
        return page

    def reports_page(self):
        page, layout = self.page("Reports & Exports", "Exports include saved opportunities; generated files are stored under data/exports.")
        button_row = QHBoxLayout()
        for fmt in ("xlsx", "csv", "json", "pdf"):
            button = QPushButton(f"Export {fmt.upper()}")
            button.clicked.connect(lambda checked=False, selected=fmt: self.export(selected))
            button_row.addWidget(button)
        layout.addLayout(button_row)
        self.export_status = QLabel("")
        layout.addWidget(self.export_status)
        return page

    def export(self, fmt):
        try:
            path = export_opportunities(list_opportunities(), fmt)
            self.export_status.setText(f"Exported: {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Export failed", str(exc))

    def settings_page(self):
        page, layout = self.page("Settings", "Candidate profile used by the local rule-based relevance analysis.")
        form = QFormLayout()
        self.level_edit = QLineEdit()
        self.graduation_edit = QLineEdit()
        self.specializations_edit = QTextEdit()
        self.skills_edit = QTextEdit()
        session = SessionLocal()
        try:
            profile = session.get(CandidateProfile, 1)
            if profile is None:
                profile = CandidateProfile(id=1)
                session.add(profile)
                session.commit()
            self.level_edit.setText(profile.academic_level)
            self.graduation_edit.setText(profile.graduation)
            self.specializations_edit.setPlainText(profile.specializations)
            self.skills_edit.setPlainText(profile.skills)
        finally:
            session.close()
        form.addRow("Academic level", self.level_edit)
        form.addRow("Expected graduation", self.graduation_edit)
        form.addRow("Target specializations", self.specializations_edit)
        form.addRow("Skills", self.skills_edit)
        layout.addLayout(form)
        button = QPushButton("Save candidate profile")
        button.clicked.connect(self.save_profile)
        layout.addWidget(button)
        layout.addWidget(QLabel("Search uses public DuckDuckGo HTML results. No paid API key is required; results may be limited by provider availability."))
        return page

    def save_profile(self):
        session = SessionLocal()
        try:
            profile = session.get(CandidateProfile, 1)
            profile.academic_level = self.level_edit.text()
            profile.graduation = self.graduation_edit.text()
            profile.specializations = self.specializations_edit.toPlainText()
            profile.skills = self.skills_edit.toPlainText()
            session.commit()
            QMessageBox.information(self, "Settings", "Candidate profile saved.")
        except Exception as exc:
            session.rollback()
            QMessageBox.warning(self, "Settings error", str(exc))
        finally:
            session.close()

    @staticmethod
    def configure_table(table):
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setWordWrap(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(42)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    @staticmethod
    def fill_table(table, rows):
        table.setRowCount(len(rows))
        for r, values in enumerate(rows):
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value or ""))
                item.setToolTip(str(value or ""))
                table.setItem(r, c, item)
        table.resizeColumnsToContents()

    @staticmethod
    def open_result(table, row, column):
        item = table.item(row, column)
        if item and item.text().startswith(("http://", "https://")):
            webbrowser.open(item.text())


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
