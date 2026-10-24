
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="AthletiQ | Sports Talent Assessment",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "assessments.db"

# ---------- STYLING ----------
st.markdown("""
<style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(120deg, #10213D, #176B87);
        color: white;
        margin-bottom: 22px;
    }
    .hero h1 {
        color: white;
        margin-bottom: 8px;
        font-size: 38px;
    }
    .hero p {
        color: #E5F4FA;
        font-size: 17px;
    }
    div[data-testid="stMetric"] {
        background: #F0F6FA;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #DCE8EF;
    }
    .section-note {
        color: #64748B;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- DATABASE ----------
def setup_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                athlete TEXT NOT NULL,
                sport TEXT NOT NULL DEFAULT 'Push-ups',
                reps INTEGER NOT NULL,
                form_rate REAL NOT NULL,
                assessment_score REAL NOT NULL,
                assessment_type TEXT NOT NULL DEFAULT 'Manual entry',
                created_at TEXT NOT NULL
            )
        """)

        # Add columns if the database was created by
        # an earlier version of our prototype.
        columns = {
            row[1] for row in
            conn.execute("PRAGMA table_info(assessments)")
        }

        additions = {
            "sport": "TEXT NOT NULL DEFAULT 'Push-ups'",
            "assessment_score": "REAL NOT NULL DEFAULT 0",
            "assessment_type": "TEXT NOT NULL DEFAULT 'Manual entry'"
        }

        for column, definition in additions.items():
            if column not in columns:
                conn.execute(
                    f"ALTER TABLE assessments "
                    f"ADD COLUMN {column} {definition}"
                )


def load_data():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query("""
            SELECT id, athlete, sport, reps, form_rate,
                   assessment_score, assessment_type, created_at
            FROM assessments
            ORDER BY id DESC
        """, conn)


setup_database()


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🏆 AthletiQ")
    st.caption("SPORTS TALENT ASSESSMENT")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Overview", "New Assessment", "Leaderboard", "About Project"]
    )

    st.divider()
    st.caption("AthletiQ v1.0 • Innovation Prototype")
    st.caption("Computer vision + accessible sports screening")


df = load_data()


# ---------- OVERVIEW ----------
if page == "Overview":

    st.markdown("""
    <div class="hero">
        <h1>Discover Potential. Empower Athletes.</h1>
        <p>
            An AI-assisted sports screening platform exploring
            accessible performance assessment and grassroots scouting.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Platform Overview")
    st.write(
        "AthletiQ combines pose estimation with athlete assessment "
        "records to demonstrate how digital tools could support "
        "sports screening beyond traditional scouting networks."
    )

    total = len(df)
    athletes = df["athlete"].nunique() if total else 0
    total_reps = int(df["reps"].sum()) if total else 0
    avg_form = float(df["form_rate"].mean()) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Assessments", total)
    c2.metric("Athletes Recorded", athletes)
    c3.metric("Total Repetitions", total_reps)
    c4.metric("Average Form Rating", f"{avg_form:.1f}%")

    st.divider()

    left, right = st.columns([1.3, 1])

    with left:
        st.subheader("How It Works")

        st.markdown("""
        **01 — Capture**

        Use a webcam to detect body landmarks with MediaPipe.

        **02 — Assess**

        Demonstrate repetition counting and record performance results.

        **03 — Track**

        Store assessments and compare recorded results on a leaderboard.
        """)

    with right:
        st.subheader("Prototype Capabilities")

        st.success("✓ Webcam-based pose detection")
        st.success("✓ Basic push-up repetition counter")
        st.success("✓ Persistent athlete records")
        st.success("✓ Performance leaderboard")
        st.info(
            "Pose detection is implemented separately in "
            "`pushup_counter.py`. Dashboard records are entered "
            "manually in this prototype."
        )

    st.divider()
    st.caption(
        "Assessment scores are preliminary indicators, not validated "
        "measures of overall athletic talent."
    )


# ---------- NEW ASSESSMENT ----------
elif page == "New Assessment":

    st.title("📝 Record an Assessment")
    st.write(
        "Save athlete performance results for tracking and comparison."
    )

    st.info(
        "Enter results from an actual test. This form is not yet "
        "connected automatically to the webcam counter."
    )

    with st.form("assessment_form", clear_on_submit=True):

        athlete = st.text_input(
            "Athlete display name",
            placeholder="Enter a name or demo ID"
        )

        sport = st.selectbox(
            "Assessment",
            ["Push-ups"]
        )

        col1, col2 = st.columns(2)

        with col1:
            reps = st.number_input(
                "Completed repetitions",
                min_value=0,
                max_value=500,
                value=0,
                step=1
            )

        with col2:
            form_rate = st.slider(
                "Repetitions meeting selected form criteria (%)",
                min_value=0,
                max_value=100,
                value=70
            )

        st.caption(
            "Form percentage is manually entered for this prototype; "
            "it is not automatically calculated by the camera."
        )

        submitted = st.form_submit_button(
            "Save Assessment",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not athlete.strip():
            st.error("Please enter an athlete display name.")
        else:
            # Illustrative score, not a validated talent metric.
            score = round(
                min(int(reps), 50) / 50 * 70
                + float(form_rate) / 100 * 30,
                1
            )

            with sqlite3.connect(DB_NAME) as conn:
                conn.execute("""
                    INSERT INTO assessments
                    (athlete, sport, reps, form_rate,
                     assessment_score, assessment_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    athlete.strip(),
                    sport,
                    int(reps),
                    float(form_rate),
                    score,
                    "Manual entry",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

            st.success("Assessment saved successfully!")
            st.metric("Illustrative assessment score", f"{score}/100")
            st.caption(
                "This score uses a simple demonstration formula. "
                "It is not a scientifically validated talent score."
            )


# ---------- LEADERBOARD ----------
elif page == "Leaderboard":

    st.title("🥇 Grassroots Scouting Leaderboard")
    st.write(
        "Compare recorded assessments to explore performance tracking."
    )

    if df.empty:
        st.info(
            "No assessment records yet. Open New Assessment to add "
            "a test record and populate the leaderboard."
        )
    else:
        ranked = df.sort_values(
            ["reps", "form_rate"],
            ascending=[False, False]
        ).reset_index(drop=True)

        ranked.insert(0, "Rank", range(1, len(ranked) + 1))

        c1, c2 = st.columns(2)
        c1.metric("Participants", ranked["athlete"].nunique())
        c2.metric("Highest Repetition Count", int(ranked["reps"].max()))

        st.subheader("Rankings")

        display = ranked[
            ["Rank", "athlete", "sport", "reps",
             "form_rate", "assessment_score", "created_at"]
        ].rename(columns={
            "athlete": "Athlete",
            "sport": "Assessment",
            "reps": "Repetitions",
            "form_rate": "Form Rating (%)",
            "assessment_score": "Demo Score",
            "created_at": "Date Recorded"
        })

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )
        
        st.download_button(
            label="Download Assessment Records (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="athletiq_assessments.csv",
            mime="text/csv",
        )
        
        st.subheader("Repetition Comparison")

        chart_data = (
            ranked.groupby("athlete", as_index=True)["reps"]
            .max()
            .sort_values(ascending=False)
        )

        st.bar_chart(chart_data)

        st.caption(
            "Rankings are based on recorded repetitions, with form "
            "rating used as a tie-breaker. They do not establish "
            "overall athletic ability."
        )


# ---------- ABOUT ----------
elif page == "About Project":

    st.title("ℹ️ About AthletiQ")

    st.subheader("The Problem")
    st.write(
        "Athletes in underserved communities may have limited access "
        "to structured performance tracking and scouting opportunities. "
        "Manual assessments can also be difficult to compare consistently."
    )

    st.subheader("Our Proposed Solution")
    st.write(
        "AthletiQ is a software-based prototype exploring webcam pose "
        "estimation, basic exercise repetition counting, and digital "
        "assessment records in one accessible platform."
    )

    st.subheader("Technology Stack")

    tech1, tech2 = st.columns(2)

    with tech1:
        st.markdown("""
        - **Python** — application logic
        - **OpenCV** — webcam video processing
        - **MediaPipe** — body landmark detection
        """)

    with tech2:
        st.markdown("""
        - **Streamlit** — interactive dashboard
        - **Pandas** — data handling
        - **SQLite** — persistent assessment records
        """)

    st.subheader("Potential Impact")
    st.write(
        "The concept could help coaches organise basic performance "
        "records and explore more accessible grassroots screening. "
        "Real-world deployment would require accuracy testing, "
        "privacy safeguards, and validation with qualified coaches."
    )

    st.caption(
        "Built as a hackathon prototype. It is not a certified "
        "sports assessment or athlete selection system."
    )
