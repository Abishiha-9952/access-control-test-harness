import os
from datetime import datetime
from html import escape

import requests
import yaml

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


# ============================================================
# TARGET CONFIGURATION
# ============================================================

TARGETS = {
    "1": {
        "name": "Website Target 1",
        "url": "http://website-target-1"
    },
    "2": {
        "name": "Website Target 2",
        "url": "http://website-target-2"
    }
}
def select_target():

    print()
    print("=" * 60)
    print("       AUTOMATED ACCESS CONTROL TEST HARNESS")
    print("=" * 60)

    print()
    print("Available targets:")
    print()
    print("  1. Website Target 1")
    print("  2. Website Target 2")   
    print()

    while True:

        choice = input(
            "Select target [1/2]: "
        ).strip()

        if choice in TARGETS:

            target = TARGETS[choice]

            print()
            print(
                f"Selected target : {target['name']}"
            )

            print(
                f"Target URL      : {target['url']}"
            )

            print("=" * 60)

            return target["url"], target["name"]

        print()
        print("Invalid choice.")
        print("Please enter 1 or 2.")
        print()


# Select target when program starts
BASE_URL, TARGET_NAME = select_target()


# ============================================================
# CONFIGURATION
# ============================================================

ROLE_MATRIX = "../role_matrix.yaml"

REPORT_DIR = "reports"

HTML_REPORT = os.path.join(
    REPORT_DIR,
    "access_control_report.html"
)

PDF_REPORT = os.path.join(
    REPORT_DIR,
    "access_control_report.pdf"
)


USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",
    },

    "user": {
        "username": "user1",
        "password": "user123",
    },
}


# ============================================================
# COLOURS
# ============================================================

NAVY = "#172554"
BLUE = "#2563EB"
BLUE_DARK = "#1D4ED8"

GREEN = "#16A34A"
GREEN_DARK = "#166534"
LIGHT_GREEN = "#DCFCE7"

RED = "#DC2626"
RED_DARK = "#991B1B"
LIGHT_RED = "#FEE2E2"

LIGHT_BLUE = "#EFF6FF"
LIGHTER_BLUE = "#F8FAFC"

PURPLE = "#7C3AED"
LIGHT_PURPLE = "#EDE9FE"

ORANGE = "#EA580C"
LIGHT_ORANGE = "#FFEDD5"

DARK = "#0F172A"
SLATE = "#64748B"
BORDER = "#CBD5E1"
WHITE = "#FFFFFF"


# ============================================================
# LOAD ROLE MATRIX
# ============================================================

def load_role_matrix():

    with open(
        ROLE_MATRIX,
        "r",
        encoding="utf-8"
    ) as file:

        return yaml.safe_load(file)


# ============================================================
# CHECK TARGET
# ============================================================

def check_target():

    print()
    print("Checking target server...")
    print("-" * 60)

    try:

        response = requests.get(
            BASE_URL,
            timeout=5
        )

        print(
            f"Target response: HTTP {response.status_code}"
        )

        print(
            f"Target URL     : {BASE_URL}"
        )

        print("-" * 60)

        return True

    except requests.RequestException as error:

        print()
        print("ERROR: Target server is not reachable.")
        print()
        print(f"URL: {BASE_URL}")
        print()
        print("Make sure the selected target application")
        print("is running before starting the harness.")
        print()
        print(f"Details: {error}")
        print("-" * 60)

        return False


# ============================================================
# LOGIN
# ============================================================

def login(username, password):

    try:

        response = requests.post(
            f"{BASE_URL}/api/login",

            json={
                "username": username,
                "password": password,
            },

            timeout=5,
        )

        if response.status_code != 200:

            return None

        try:

            return response.json().get("token")

        except ValueError:

            return None

    except requests.RequestException:

        return None


# ============================================================
# REQUEST ENDPOINT
# ============================================================

def request_endpoint(
    method,
    path,
    token=None
):

    headers = {}

    if token:

        headers["Authorization"] = (
            f"Bearer {token}"
        )

    data = None

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if (
        method == "POST"
        and path == "/api/login"
    ):

        data = {
            "username": "admin",
            "password": "admin123",
        }

    # --------------------------------------------------------
    # PATCH
    # --------------------------------------------------------

    elif method == "PATCH":

        data = {
            "email": "updated@example.com",
        }

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    elif method == "POST":

        data = {}

    # --------------------------------------------------------
    # PUT
    # --------------------------------------------------------

    elif method == "PUT":

        data = {}

    try:

        response = requests.request(
            method,
            f"{BASE_URL}{path}",
            headers=headers,
            json=data,
            timeout=5,
        )

        return response.status_code

    except requests.RequestException:

        return 0


# ============================================================
# BUILD TESTS
# ============================================================

def build_tests():

    role_matrix = load_role_matrix()

    tests = []

    for role, endpoints in role_matrix["roles"].items():

        for endpoint, rule in endpoints.items():

            method, path = endpoint.split(
                " ",
                1
            )

            # ------------------------------------------------
            # Replace user ID
            # ------------------------------------------------

            if "{id}" in path:

                if "/users/" in path:

                    path = path.replace(
                        "{id}",
                        "2"
                    )

                elif "/orders/" in path:

                    path = path.replace(
                        "{id}",
                        "101"
                    )

            tests.append(
                {
                    "role": role,
                    "method": method,
                    "path": path,
                    "access": rule["access"],
                }
            )

    return tests


# ============================================================
# EXPECTED STATUS
# ============================================================

def expected_status(access):

    if access == "deny":

        return 403

    return 200


# ============================================================
# HTML REPORT
# ============================================================

def generate_html_report(
    results,
    passed,
    failed,
    generated_time
):

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    total = len(results)

    if failed == 0:

        overall_text = "✓ PASS"
        overall_class = "success"

    else:

        overall_text = "✗ FAIL"
        overall_class = "danger"

    rows = ""

    for result in results:

        if result["passed"]:

            status_text = "✓ PASS"
            status_class = "pass"

        else:

            status_text = "✗ FAIL"
            status_class = "fail"

        rows += f"""
        <tr>

            <td>
                <span class="role {escape(result['role'])}">
                    {escape(result['role'].upper())}
                </span>
            </td>

            <td>
                <span class="method">
                    {escape(result['method'])}
                </span>
            </td>

            <td class="endpoint">
                {escape(result['path'])}
            </td>

            <td>
                <span class="rule">
                    {escape(result['access'])}
                </span>
            </td>

            <td class="code">
                {result['expected']}
            </td>

            <td class="code">
                {result['actual']}
            </td>

            <td>
                <span class="result {status_class}">
                    {status_text}
                </span>
            </td>

        </tr>
        """

    html = f"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
    Access Control Security Report
</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #eef2ff,
            #f8fafc
        );

    color: {DARK};
}}

.container {{

    width: 94%;

    max-width: 1400px;

    margin: 35px auto;
}}


/* HEADER */

.header {{

    background:
        linear-gradient(
            135deg,
            {NAVY},
            {BLUE}
        );

    color: white;

    padding: 40px;

    border-radius: 22px;

    box-shadow:
        0 18px 40px
        rgba(37, 99, 235, 0.25);

    margin-bottom: 25px;
}}

.header h1 {{

    margin: 0;

    font-size: 34px;

    letter-spacing: 1px;
}}

.header h2 {{

    margin: 10px 0;

    font-size: 20px;

    font-weight: normal;

    opacity: 0.92;
}}

.header p {{

    margin-top: 15px;

    opacity: 0.85;

    line-height: 1.6;
}}

.target-badge {{

    display: inline-block;

    margin-top: 15px;

    padding: 8px 14px;

    background: rgba(255,255,255,0.15);

    border: 1px solid rgba(255,255,255,0.25);

    border-radius: 20px;

    font-weight: bold;
}}


/* SUMMARY */

.summary {{

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 18px;

    margin-bottom: 25px;
}}

.card {{

    background: white;

    padding: 25px;

    border-radius: 17px;

    box-shadow:
        0 8px 25px
        rgba(15, 23, 42, 0.08);

    text-align: center;

    border-top: 5px solid {BLUE};
}}

.card.passed {{
    border-top-color: {GREEN};
}}

.card.failed {{
    border-top-color: {RED};
}}

.card.overall {{
    border-top-color:
        {GREEN if failed == 0 else RED};
}}

.card h3 {{

    margin: 0;

    font-size: 12px;

    color: {SLATE};

    letter-spacing: 1px;
}}

.number {{

    margin-top: 8px;

    font-size: 36px;

    font-weight: bold;
}}

.blue {{
    color: {BLUE};
}}

.green {{
    color: {GREEN};
}}

.red {{
    color: {RED};
}}


/* SECTION */

.section {{

    background: white;

    border-radius: 17px;

    padding: 25px;

    margin-bottom: 25px;

    box-shadow:
        0 8px 25px
        rgba(15, 23, 42, 0.08);
}}

.section-title {{

    font-size: 21px;

    font-weight: bold;

    color: {NAVY};

    margin-bottom: 20px;
}}


/* COVERAGE */

.coverage {{

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 16px;
}}

.coverage-card {{

    padding: 20px;

    border-radius: 13px;

    background: {LIGHTER_BLUE};

    border-left:
        5px solid {GREEN};
}}

.coverage-card .icon {{

    font-size: 25px;

    color: {GREEN};

    float: left;

    margin-right: 12px;
}}

.coverage-card h3 {{

    margin: 0;

    color: {NAVY};
}}

.coverage-card p {{

    color: {SLATE};

    line-height: 1.5;

    margin-bottom: 0;
}}


/* TABLE */

.table-container {{

    overflow-x: auto;
}}

table {{

    width: 100%;

    border-collapse: collapse;

    font-size: 14px;
}}

thead {{

    background:
        linear-gradient(
            90deg,
            {NAVY},
            {BLUE}
        );

    color: white;
}}

th {{

    padding: 15px;

    text-align: left;

    font-size: 12px;

    letter-spacing: 0.5px;
}}

td {{

    padding: 13px 15px;

    border-bottom:
        1px solid #e2e8f0;
}}

tbody tr:hover {{

    background: {LIGHT_BLUE};
}}

.endpoint {{

    font-family:
        "Courier New",
        monospace;

    color: #1e3a8a;
}}

.code {{

    text-align: center;

    font-weight: bold;
}}


/* BADGES */

.role {{

    display: inline-block;

    padding: 6px 11px;

    border-radius: 20px;

    font-size: 10px;

    font-weight: bold;
}}

.role.admin {{

    background: #fee2e2;

    color: #991b1b;
}}

.role.user {{

    background: #dbeafe;

    color: #1d4ed8;
}}

.role.guest {{

    background: #f1f5f9;

    color: #475569;
}}

.method {{

    background: #e0e7ff;

    color: #3730a3;

    padding: 6px 10px;

    border-radius: 6px;

    font-size: 10px;

    font-weight: bold;
}}

.rule {{

    background: #f1f5f9;

    padding: 6px 10px;

    border-radius: 6px;

    font-size: 10px;
}}

.result {{

    display: inline-block;

    padding: 7px 13px;

    border-radius: 20px;

    font-size: 10px;

    font-weight: bold;
}}

.result.pass {{

    background: {LIGHT_GREEN};

    color: #166534;
}}

.result.fail {{

    background: {LIGHT_RED};

    color: #991b1b;
}}


/* CONCLUSION */

.conclusion {{

    padding: 25px;

    border-radius: 15px;

    background:
        {LIGHT_GREEN if failed == 0 else LIGHT_RED};

    border:
        1px solid
        {GREEN if failed == 0 else RED};

    color:
        {GREEN_DARK if failed == 0 else RED_DARK};

    margin-bottom: 25px;
}}

.conclusion h2 {{

    margin-top: 0;
}}


/* FOOTER */

.footer {{

    text-align: center;

    color: {SLATE};

    font-size: 13px;

    padding: 20px;
}}


/* RESPONSIVE */

@media (max-width: 900px) {{

    .summary {{

        grid-template-columns:
            repeat(2, 1fr);
    }}

    .coverage {{

        grid-template-columns:
            1fr;
    }}
}}

@media (max-width: 600px) {{

    .summary {{

        grid-template-columns:
            1fr;
    }}

    .header h1 {{

        font-size: 25px;
    }}
}}

</style>

</head>

<body>

<div class="container">


<div class="header">

    <h1>
        🔐 AUTOMATED ACCESS CONTROL
    </h1>

    <h2>
        SECURITY TEST REPORT
    </h2>

    <p>
        Role-Based Authorization
        • JWT Authentication
        • Horizontal Access Control
        • Vertical Access Control
    </p>

    <div class="target-badge">
        Testing: {escape(TARGET_NAME)}
        &nbsp; • &nbsp;
        {escape(BASE_URL)}
    </div>

    <p>
        <strong>Generated:</strong>
        {escape(generated_time)}
    </p>

</div>


<div class="summary">

    <div class="card">

        <h3>
            TOTAL TESTS
        </h3>

        <div class="number blue">
            {total}
        </div>

    </div>


    <div class="card passed">

        <h3>
            PASSED
        </h3>

        <div class="number green">
            {passed}
        </div>

    </div>


    <div class="card failed">

        <h3>
            FAILED
        </h3>

        <div class="number red">
            {failed}
        </div>

    </div>


    <div class="card overall">

        <h3>
            OVERALL STATUS
        </h3>

        <div class="number
            {'green' if failed == 0 else 'red'}">

            {overall_text}

        </div>

    </div>

</div>


<div class="section">

    <div class="section-title">
        🛡️ SECURITY COVERAGE
    </div>

    <div class="coverage">

        <div class="coverage-card">

            <div class="icon">
                ✓
            </div>

            <h3>
                Vertical Access Control
            </h3>

            <p>
                Tests lower-privileged users attempting
                administrator-only operations.
            </p>

        </div>


        <div class="coverage-card">

            <div class="icon">
                ✓
            </div>

            <h3>
                Horizontal Access Control / IDOR
            </h3>

            <p>
                Tests ownership-based access to
                user profiles and orders.
            </p>

        </div>


        <div class="coverage-card">

            <div class="icon">
                ✓
            </div>

            <h3>
                JWT Authentication
            </h3>

            <p>
                Authenticated requests are sent using
                Bearer JWT authorization tokens.
            </p>

        </div>


        <div class="coverage-card">

            <div class="icon">
                ✓
            </div>

            <h3>
                Role Permission Matrix
            </h3>

            <p>
                Expected authorization rules are loaded
                automatically from role_matrix.yaml.
            </p>

        </div>

    </div>

</div>


<div class="section">

    <div class="section-title">
        📋 DETAILED TEST RESULTS
    </div>

    <div class="table-container">

        <table>

            <thead>

                <tr>

                    <th>ROLE</th>
                    <th>METHOD</th>
                    <th>ENDPOINT</th>
                    <th>RULE</th>
                    <th>EXPECTED</th>
                    <th>ACTUAL</th>
                    <th>RESULT</th>

                </tr>

            </thead>

            <tbody>

                {rows}

            </tbody>

        </table>

    </div>

</div>


<div class="conclusion">

    <h2>

        {
            '✓ Security Test Passed'
            if failed == 0
            else
            '✗ Security Test Failed'
        }

    </h2>

    <p>

        <strong>{total}</strong>
        automated authorization tests were executed.

        <strong>{passed}</strong>
        tests passed and

        <strong>{failed}</strong>
        tests failed.

    </p>

    <p>

        The actual HTTP responses were compared against
        the expected permissions defined in the role matrix.

    </p>

</div>


<div class="footer">

    Automated Access Control Test Harness

    <br>

    {escape(TARGET_NAME)}
    •
    Role-Based Access Control
    •
    JWT
    •
    IDOR Testing

</div>

</div>

</body>

</html>
"""

    with open(
        HTML_REPORT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)

    print()
    print("=" * 60)
    print("HTML REPORT CREATED")
    print("=" * 60)
    print(f"Report: {HTML_REPORT}")
    print("=" * 60)


# ============================================================
# PDF HELPERS
# ============================================================

def pdf_color(hex_color):

    return colors.HexColor(hex_color)


def create_badge(
    text,
    background,
    foreground,
    font_size=6.5
):

    style = ParagraphStyle(
        "BadgeStyle",
        fontName="Helvetica-Bold",
        fontSize=font_size,
        leading=font_size + 2,
        textColor=pdf_color(foreground),
        alignment=TA_CENTER,
    )

    badge = Table(
        [[
            Paragraph(
                escape(str(text)),
                style
            )
        ]],
        colWidths=[20 * mm]
    )

    badge.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    pdf_color(background)
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    pdf_color(background)
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
            ]
        )
    )

    return badge


def role_badge(role):

    role = role.lower()

    if role == "admin":

        return create_badge(
            "ADMIN",
            "#FEE2E2",
            "#991B1B",
            6.2
        )

    if role == "user":

        return create_badge(
            "USER",
            "#DBEAFE",
            "#1D4ED8",
            6.2
        )

    return create_badge(
        "GUEST",
        "#F1F5F9",
        "#475569",
        6.2
    )


def method_badge(method):

    return create_badge(
        method,
        "#E0E7FF",
        "#3730A3",
        6.2
    )


def rule_badge(rule):

    if rule == "deny":

        return create_badge(
            "deny",
            "#FEE2E2",
            "#991B1B",
            6.2
        )

    if rule == "own":

        return create_badge(
            "own",
            "#EDE9FE",
            "#6D28D9",
            6.2
        )

    if rule == "any":

        return create_badge(
            "any",
            "#FFEDD5",
            "#C2410C",
            6.2
        )

    return create_badge(
        "allow",
        "#DCFCE7",
        "#166534",
        6.2
    )


def result_badge(passed):

    if passed:

        return create_badge(
            "✓ PASS",
            "#DCFCE7",
            "#166534",
            6.2
        )

    return create_badge(
        "✗ FAIL",
        "#FEE2E2",
        "#991B1B",
        6.2
    )


# ============================================================
# PDF REPORT
# ============================================================

def generate_pdf_report(
    results,
    passed,
    failed,
    generated_time
):

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    total = len(results)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=24,
        textColor=colors.white,
        alignment=TA_LEFT,
    )

    subtitle_style = ParagraphStyle(
        "PDFSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#DBEAFE"),
    )

    date_style = ParagraphStyle(
        "PDFDate",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#BFDBFE"),
    )

    section_style = ParagraphStyle(
        "PDFSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=pdf_color(NAVY),
        spaceBefore=5,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "PDFBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.7,
        leading=10.5,
        textColor=pdf_color(DARK),
    )

    endpoint_style = ParagraphStyle(
        "PDFEndpoint",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=6.5,
        leading=8,
        textColor=colors.HexColor("#1E3A8A"),
    )

    table_header_style = ParagraphStyle(
        "PDFTableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.2,
        leading=7,
        textColor=colors.white,
        alignment=TA_CENTER,
    )

    table_text_style = ParagraphStyle(
        "PDFTableText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.2,
        leading=7.5,
        textColor=pdf_color(DARK),
        alignment=TA_CENTER,
    )

    table_endpoint_style = ParagraphStyle(
        "PDFTableEndpoint",
        parent=table_text_style,
        fontName="Courier",
        fontSize=5.9,
        leading=7,
    )

    small_style = ParagraphStyle(
        "PDFSmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=pdf_color(SLATE),
    )

    conclusion_style = ParagraphStyle(
        "PDFConclusion",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=12,
        textColor=pdf_color(
            GREEN_DARK if failed == 0 else RED_DARK
        ),
    )

    doc = SimpleDocTemplate(
        PDF_REPORT,
        pagesize=A4,
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=13 * mm,
        bottomMargin=18 * mm,
    )

    story = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = Table(
        [
            [
                Paragraph(
                    "AUTOMATED ACCESS CONTROL",
                    title_style
                )
            ],
            [
                Paragraph(
                    "SECURITY TEST REPORT",
                    title_style
                )
            ],
            [
                Paragraph(
                    f"Target: <b>{escape(TARGET_NAME)}</b>"
                    f" &nbsp;•&nbsp; "
                    f"{escape(BASE_URL)}",
                    subtitle_style
                )
            ],
            [
                Paragraph(
                    "Role-Based Authorization &nbsp;•&nbsp; "
                    "JWT Authentication &nbsp;•&nbsp; "
                    "Horizontal Access Control &nbsp;•&nbsp; "
                    "Vertical Access Control",
                    subtitle_style
                )
            ],
            [
                Paragraph(
                    f"<b>Generated:</b> "
                    f"{escape(generated_time)}",
                    date_style
                )
            ],
        ],
        colWidths=[184 * mm],
    )

    header.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    pdf_color(NAVY)
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    14
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    14
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    12
                ),
                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, -1),
                    2
                ),
                (
                    "BOTTOMPADDING",
                    (0, 4),
                    (-1, 4),
                    12
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, 0),
                    2,
                    pdf_color(BLUE)
                ),
            ]
        )
    )

    story.append(header)
    story.append(Spacer(1, 8))

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary_header_style = ParagraphStyle(
        "SummaryHeader",
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=8,
        textColor=pdf_color(SLATE),
        alignment=TA_CENTER,
    )

    summary_number_style = ParagraphStyle(
        "SummaryNumber",
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=21,
        alignment=TA_CENTER,
    )

    summary = Table(
        [
            [
                Paragraph(
                    "TOTAL TESTS",
                    summary_header_style
                ),
                Paragraph(
                    "PASSED",
                    summary_header_style
                ),
                Paragraph(
                    "FAILED",
                    summary_header_style
                ),
                Paragraph(
                    "OVERALL STATUS",
                    summary_header_style
                ),
            ],
            [
                Paragraph(
                    str(total),
                    ParagraphStyle(
                        "BlueNumber",
                        parent=summary_number_style,
                        textColor=pdf_color(BLUE),
                    )
                ),
                Paragraph(
                    str(passed),
                    ParagraphStyle(
                        "GreenNumber",
                        parent=summary_number_style,
                        textColor=pdf_color(GREEN),
                    )
                ),
                Paragraph(
                    str(failed),
                    ParagraphStyle(
                        "RedNumber",
                        parent=summary_number_style,
                        textColor=pdf_color(RED),
                    )
                ),
                Paragraph(
                    "✓ PASS"
                    if failed == 0
                    else "✗ FAIL",
                    ParagraphStyle(
                        "OverallNumber",
                        parent=summary_number_style,
                        textColor=pdf_color(
                            GREEN
                            if failed == 0
                            else RED
                        ),
                    )
                ),
            ],
        ],
        colWidths=[
            46 * mm,
            46 * mm,
            46 * mm,
            46 * mm,
        ],
    )

    summary.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    pdf_color(LIGHT_BLUE)
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (0, 1),
                    pdf_color("#F0F7FF")
                ),
                (
                    "BACKGROUND",
                    (1, 1),
                    (1, 1),
                    pdf_color(LIGHT_GREEN)
                ),
                (
                    "BACKGROUND",
                    (2, 1),
                    (2, 1),
                    pdf_color(LIGHT_RED)
                ),
                (
                    "BACKGROUND",
                    (3, 1),
                    (3, 1),
                    pdf_color(
                        LIGHT_GREEN
                        if failed == 0
                        else LIGHT_RED
                    )
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    pdf_color(BORDER)
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    pdf_color(BORDER)
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    7
                ),
                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, 1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 1),
                    (-1, 1),
                    8
                ),
            ]
        )
    )

    story.append(summary)
    story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # SECURITY COVERAGE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "SECURITY COVERAGE",
            section_style
        )
    )

    coverage_style = ParagraphStyle(
        "Coverage",
        parent=body_style,
        fontSize=7.2,
        leading=10,
    )

    coverage = Table(
        [
            [
                Paragraph(
                    "<b><font color='#16A34A'>✓</font> "
                    "Vertical Access Control</b><br/>"
                    "Tests lower-privileged users attempting "
                    "administrator-only operations.",
                    coverage_style
                ),
                Paragraph(
                    "<b><font color='#16A34A'>✓</font> "
                    "Horizontal Access Control / IDOR</b><br/>"
                    "Tests ownership-based access to "
                    "user profiles and orders.",
                    coverage_style
                ),
            ],
            [
                Paragraph(
                    "<b><font color='#16A34A'>✓</font> "
                    "JWT Authentication</b><br/>"
                    "Authenticated requests use "
                    "Bearer JWT authorization tokens.",
                    coverage_style
                ),
                Paragraph(
                    "<b><font color='#16A34A'>✓</font> "
                    "Role Permission Matrix</b><br/>"
                    "Expected authorization rules are loaded "
                    "automatically from role_matrix.yaml.",
                    coverage_style
                ),
            ],
        ],
        colWidths=[
            92 * mm,
            92 * mm,
        ],
    )

    coverage.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    pdf_color(LIGHTER_BLUE)
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    pdf_color(BORDER)
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    pdf_color(BORDER)
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
            ]
        )
    )

    story.append(coverage)
    story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # DETAILED RESULTS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "DETAILED TEST RESULTS",
            section_style
        )
    )

    table_data = [
        [
            Paragraph("ROLE", table_header_style),
            Paragraph("METHOD", table_header_style),
            Paragraph("ENDPOINT", table_header_style),
            Paragraph("RULE", table_header_style),
            Paragraph("EXPECTED", table_header_style),
            Paragraph("ACTUAL", table_header_style),
            Paragraph("RESULT", table_header_style),
        ]
    ]

    for result in results:

        table_data.append(
            [
                role_badge(result["role"]),

                method_badge(
                    result["method"]
                ),

                Paragraph(
                    escape(result["path"]),
                    table_endpoint_style
                ),

                rule_badge(
                    result["access"]
                ),

                Paragraph(
                    str(result["expected"]),
                    table_text_style
                ),

                Paragraph(
                    str(result["actual"]),
                    table_text_style
                ),

                result_badge(
                    result["passed"]
                ),
            ]
        )

    result_table = Table(
        table_data,
        colWidths=[
            22 * mm,
            21 * mm,
            55 * mm,
            21 * mm,
            20 * mm,
            20 * mm,
            25 * mm,
        ],
        repeatRows=1,
        hAlign="CENTER",
    )

    result_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    pdf_color(NAVY)
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    pdf_color(BORDER)
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        pdf_color(LIGHTER_BLUE)
                    ]
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
            ]
        )
    )

    story.append(result_table)
    story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------------

    if failed == 0:

        conclusion_title = (
            "<font color='#166534'>"
            "✓ OVERALL SECURITY RESULT: PASS"
            "</font>"
        )

        conclusion_text = (
            f"<b>{total}</b> automated authorization tests "
            f"were executed. "
            f"<b>{passed}</b> tests passed and "
            f"<b>{failed}</b> tests failed.<br/><br/>"
            "All tested authorization responses matched "
            "the configured role-permission policy."
        )

        conclusion_bg = LIGHT_GREEN
        conclusion_border = GREEN

    else:

        conclusion_title = (
            "<font color='#991B1B'>"
            "✗ OVERALL SECURITY RESULT: FAIL"
            "</font>"
        )

        conclusion_text = (
            f"<b>{total}</b> automated authorization tests "
            f"were executed. "
            f"<b>{passed}</b> tests passed and "
            f"<b>{failed}</b> tests failed.<br/><br/>"
            "One or more authorization responses did not "
            "match the configured role-permission policy."
        )

        conclusion_bg = LIGHT_RED
        conclusion_border = RED

    conclusion_title_style = ParagraphStyle(
        "ConclusionTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=pdf_color(
            GREEN_DARK
            if failed == 0
            else RED_DARK
        ),
    )

    conclusion = Table(
        [
            [
                Paragraph(
                    conclusion_title,
                    conclusion_title_style
                )
            ],
            [
                Paragraph(
                    conclusion_text,
                    conclusion_style
                )
            ],
        ],
        colWidths=[184 * mm],
    )

    conclusion.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    pdf_color(conclusion_bg)
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.9,
                    pdf_color(conclusion_border)
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    3
                ),
                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, 1),
                    3
                ),
                (
                    "BOTTOMPADDING",
                    (0, 1),
                    (-1, 1),
                    9
                ),
            ]
        )
    )

    story.append(
        KeepTogether(conclusion)
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            f"Target: {escape(TARGET_NAME)} "
            f"• URL: {escape(BASE_URL)} "
            f"• Generated: {escape(generated_time)}",
            small_style
        )
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    def footer(canvas, doc):

        canvas.saveState()

        canvas.setStrokeColor(
            pdf_color(BORDER)
        )

        canvas.setLineWidth(0.5)

        canvas.line(
            13 * mm,
            10 * mm,
            197 * mm,
            10 * mm
        )

        canvas.setFont(
            "Helvetica",
            6.8
        )

        canvas.setFillColor(
            pdf_color(SLATE)
        )

        canvas.drawString(
            13 * mm,
            6 * mm,
            "Automated Access Control Test Harness"
        )

        canvas.drawRightString(
            197 * mm,
            6 * mm,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer
    )

    print()
    print("=" * 60)
    print("PDF REPORT CREATED")
    print("=" * 60)
    print(f"Report: {PDF_REPORT}")
    print("=" * 60)


# ============================================================
# RUN TESTS
# ============================================================

def run_tests():

    print()
    print("Loading role matrix...")
    print("=" * 60)

    tests = build_tests()

    print(
        f"Generated tests: {len(tests)}"
    )

    # --------------------------------------------------------
    # CHECK SERVER
    # --------------------------------------------------------

    if not check_target():

        return

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    print()
    print("Logging in test users...")
    print("=" * 60)

    tokens = {}

    for role, credentials in USERS.items():

        token = login(
            credentials["username"],
            credentials["password"]
        )

        tokens[role] = token

        if token:

            print(
                f"{role}: login successful"
            )

        else:

            print(
                f"{role}: login failed"
            )

    # --------------------------------------------------------
    # TESTS
    # --------------------------------------------------------

    print()
    print(
        f"Running access-control tests against "
        f"{TARGET_NAME}..."
    )

    print("=" * 60)

    passed = 0
    failed = 0

    results = []

    for test in tests:

        role = test["role"]

        token = tokens.get(role)

        expected = expected_status(
            test["access"]
        )

        actual = request_endpoint(
            test["method"],
            test["path"],
            token
        )

        test_passed = (
            actual == expected
        )

        if test_passed:

            result_text = "PASS"

            passed += 1

        else:

            result_text = "FAIL"

            failed += 1

        results.append(
            {
                "role": role,
                "method": test["method"],
                "path": test["path"],
                "access": test["access"],
                "expected": expected,
                "actual": actual,
                "passed": test_passed,
            }
        )

        print(
            f"{result_text:5} | "
            f"{role:5} | "
            f"{test['method']:6} | "
            f"{test['path']:30} | "
            f"expected={expected} "
            f"actual={actual}"
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("=" * 60)

    print(
        f"Target:  {TARGET_NAME}"
    )

    print(
        f"Passed:  {passed}"
    )

    print(
        f"Failed:  {failed}"
    )

    print(
        f"Total:   {len(tests)}"
    )

    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------

    generated_time = datetime.now().strftime(
        "%d %B %Y, %H:%M:%S"
    )

    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    generate_html_report(
        results,
        passed,
        failed,
        generated_time
    )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    generate_pdf_report(
        results,
        passed,
        failed,
        generated_time
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("REPORT GENERATION COMPLETE")
    print("=" * 60)

    print(
        f"Target : {TARGET_NAME}"
    )

    print(
        f"URL    : {BASE_URL}"
    )

    print(
        f"HTML   : {HTML_REPORT}"
    )

    print(
        f"PDF    : {PDF_REPORT}"
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()
