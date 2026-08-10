import sqlite3
from pathlib import Path

import streamlit as st

from youtube_analyzer import (
    analyze_database,
    calculate_signal
)

from product_analyzer import (
    analyze_all_products
)


# ============================================================
# TCG RADAR DASHBOARD
# ============================================================

st.set_page_config(
    page_title="TCG Radar",
    page_icon="📡",
    layout="wide"
)

PROJECT_FOLDER = Path(__file__).resolve().parent
DATABASE_FILE = PROJECT_FOLDER / "tcg_radar.db"


# ============================================================
# DATABASE STATS
# ============================================================

def get_database_stats():

    if not DATABASE_FILE.exists():
        return 0, 0, 0, []

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM youtube_videos"
        )
        video_count = cursor.fetchone()[0]

    except sqlite3.OperationalError:
        video_count = 0


    try:
        cursor.execute(
            "SELECT COUNT(*) FROM youtube_comments"
        )
        comment_count = cursor.fetchone()[0]

    except sqlite3.OperationalError:
        comment_count = 0


    try:
        cursor.execute("""
            SELECT game, COUNT(*)
            FROM youtube_videos
            GROUP BY game
            ORDER BY COUNT(*) DESC
        """)

        game_rows = cursor.fetchall()

    except sqlite3.OperationalError:
        game_rows = []


    connection.close()

    return (
        video_count,
        comment_count,
        len(game_rows),
        game_rows
    )


# ============================================================
# HEADER
# ============================================================

st.title("📡 TCG Radar")

st.caption(
    "Trading Card Market Intelligence"
)

st.divider()


# ============================================================
# DATABASE OVERVIEW
# ============================================================

videos, comments, games, game_rows = (
    get_database_stats()
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Saved YouTube Videos",
    videos
)

col2.metric(
    "Saved Comments",
    comments
)

col3.metric(
    "TCGs With Data",
    games
)


if videos == 0:

    st.info(
        "No saved YouTube data yet. "
        "The next discovery scan will populate the database."
    )


# ============================================================
# MAIN TABS
# ============================================================

overview_tab, market_tab, product_tab, sources_tab = (
    st.tabs([
        "📡 Overview",
        "📊 Market Analysis",
        "🔥 Product Intelligence",
        "🔌 Data Sources"
    ])
)


# ============================================================
# OVERVIEW
# ============================================================

with overview_tab:

    st.subheader(
        "Radar Control Center"
    )

    left, middle, right = st.columns(3)


    # --------------------------------------------------------
    # DAILY SCAN
    # --------------------------------------------------------

    with left:

        st.button(
            "📡 Run Daily Scan",
            use_container_width=True,
            disabled=True
        )

        st.caption(
            "Temporarily disabled while today's "
            "YouTube search quota is exhausted."
        )


    # --------------------------------------------------------
    # MARKET BUTTON
    # --------------------------------------------------------

    with middle:

        if st.button(
            "📊 Analyze Market",
            use_container_width=True
        ):

            st.session_state[
                "run_market"
            ] = True

            st.success(
                "Market analysis ready. "
                "Open the Market Analysis tab."
            )


    # --------------------------------------------------------
    # PRODUCT BUTTON
    # --------------------------------------------------------

    with right:

        if st.button(
            "🔥 Analyze Products",
            use_container_width=True
        ):

            st.session_state[
                "run_products"
            ] = True

            st.success(
                "Product analysis ready. "
                "Open the Product Intelligence tab."
            )


    # --------------------------------------------------------
    # DATA BREAKDOWN
    # --------------------------------------------------------

    if game_rows:

        st.subheader(
            "Saved Data by TCG"
        )

        table_data = []

        for game, count in game_rows:

            table_data.append({
                "Trading Card Game":
                    game,

                "Saved Videos":
                    count
            })

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# MARKET ANALYSIS TAB
# ============================================================

with market_tab:

    st.header(
        "📊 Overall Market Analysis"
    )

    st.caption(
        "Uses saved data only — no YouTube API calls."
    )


    if st.button(
        "Run Market Analysis",
        key="market_analysis_button"
    ):

        st.session_state[
            "run_market"
        ] = True


    if st.session_state.get(
        "run_market",
        False
    ):

        results = analyze_database()


        if not results:

            st.info(
                "There is no saved market data to analyze yet."
            )


        for game, data in results.items():

            signals = data[
                "community_signals"
            ]

            score, label = (
                calculate_signal(
                    signals
                )
            )


            with st.expander(
                f"{game} — {label}",
                expanded=True
            ):

                a, b, c, d = st.columns(4)


                a.metric(
                    "Radar Score",
                    score
                )

                b.metric(
                    "Videos",
                    data[
                        "videos_analyzed"
                    ]
                )

                c.metric(
                    "Comments",
                    data[
                        "comments_analyzed"
                    ]
                )

                d.metric(
                    "Relevant Comments",
                    data[
                        "relevant_comments"
                    ]
                )


                st.markdown(
                    "#### Community Signals"
                )


                signal_table = [
                    {
                        "Signal":
                            "Buying",

                        "Mentions":
                            signals[
                                "buying"
                            ]
                    },

                    {
                        "Signal":
                            "Hype",

                        "Mentions":
                            signals[
                                "hype"
                            ]
                    },

                    {
                        "Signal":
                            "Shortage",

                        "Mentions":
                            signals[
                                "shortage"
                            ]
                    },

                    {
                        "Signal":
                            "Restock",

                        "Mentions":
                            signals[
                                "restock"
                            ]
                    },

                    {
                        "Signal":
                            "Undervalued",

                        "Mentions":
                            signals[
                                "undervalued"
                            ]
                    },

                    {
                        "Signal":
                            "Overpriced",

                        "Mentions":
                            signals[
                                "overpriced"
                            ]
                    },

                    {
                        "Signal":
                            "Price Up",

                        "Mentions":
                            signals[
                                "price_up"
                            ]
                    },

                    {
                        "Signal":
                            "Price Down",

                        "Mentions":
                            signals[
                                "price_down"
                            ]
                    },

                    {
                        "Signal":
                            "Skip",

                        "Mentions":
                            signals[
                                "skip"
                            ]
                    },

                    {
                        "Signal":
                            "Waiting",

                        "Mentions":
                            signals[
                                "waiting"
                            ]
                    }
                ]


                st.dataframe(
                    signal_table,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# PRODUCT INTELLIGENCE TAB
# ============================================================

with product_tab:

    st.header(
        "🔥 Product Intelligence"
    )

    st.caption(
        "Detects product/topic signals from saved data."
    )


    if st.button(
        "Run Product Analysis",
        key="product_analysis_button"
    ):

        st.session_state[
            "run_products"
        ] = True


    if st.session_state.get(
        "run_products",
        False
    ):

        product_results = (
            analyze_all_products()
        )


        if not product_results:

            st.info(
                "There is no saved product data to analyze yet."
            )


        for game, products in (
            product_results.items()
        ):

            st.subheader(game)


            if not products:

                st.write(
                    "No repeated product or "
                    "topic signals detected."
                )

                continue


            for product in products[:10]:

                with st.expander(
                    f"{product['label']} "
                    f"— "
                    f"{product['product'].title()}"
                ):

                    a, b, c = st.columns(3)


                    a.metric(
                        "Radar Score",
                        product[
                            "score"
                        ]
                    )


                    b.metric(
                        "Video Mentions",
                        product[
                            "video_mentions"
                        ]
                    )


                    c.metric(
                        "Comment Mentions",
                        product[
                            "comment_mentions"
                        ]
                    )


                    signals = (
                        product[
                            "signals"
                        ]
                    )


                    signal_table = [
                        {
                            "Signal":
                                "Buying",

                            "Mentions":
                                signals[
                                    "buying"
                                ]
                        },

                        {
                            "Signal":
                                "Hype",

                            "Mentions":
                                signals[
                                    "hype"
                                ]
                        },

                        {
                            "Signal":
                                "Shortage",

                            "Mentions":
                                signals[
                                    "shortage"
                                ]
                        },

                        {
                            "Signal":
                                "Restock",

                            "Mentions":
                                signals[
                                    "restock"
                                ]
                        },

                        {
                            "Signal":
                                "Undervalued",

                            "Mentions":
                                signals[
                                    "undervalued"
                                ]
                        },

                        {
                            "Signal":
                                "Overpriced",

                            "Mentions":
                                signals[
                                    "overpriced"
                                ]
                        },

                        {
                            "Signal":
                                "Price Up",

                            "Mentions":
                                signals[
                                    "price_up"
                                ]
                        },

                        {
                            "Signal":
                                "Price Down",

                            "Mentions":
                                signals[
                                    "price_down"
                                ]
                        }
                    ]


                    st.dataframe(
                        signal_table,
                        use_container_width=True,
                        hide_index=True
                    )


                    if product[
                        "examples"
                    ]:

                        st.markdown(
                            "**Example videos**"
                        )

                        for title in product[
                            "examples"
                        ]:

                            st.write(
                                f"• {title}"
                            )


# ============================================================
# DATA SOURCES TAB
# ============================================================

with sources_tab:

    st.header(
        "🔌 Data Sources"
    )


    youtube_col, reddit_col = (
        st.columns(2)
    )


    with youtube_col:

        st.markdown(
            "### ▶️ YouTube"
        )

        st.write(
            "Video discovery, metadata "
            "and public comments."
        )

        st.success(
            "Connected"
        )


    with reddit_col:

        st.markdown(
            "### Reddit"
        )

        st.write(
            "Public TCG posts and comments."
        )

        st.warning(
            "Waiting for API access"
        )