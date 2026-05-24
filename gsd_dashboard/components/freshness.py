"""
Data freshness badge — shown in the sidebar on every page.
Reads etl_sync_log from demo_store or Supabase.
"""
from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from components.branding import FRESHNESS_TABLE_LABELS

_STALE_MINUTES = {
    "issues":        90,
    "stakeholders":  90,
    "standards":     1500,
    "kpi_snapshots": 1500,
}


def _age_label(age_min: float) -> str:
    """Return a human-readable age string: '2 min ago', '1 h ago', etc."""
    if age_min < 2:
        return "just now"
    if age_min < 60:
        return f"{int(age_min)} min ago"
    hours = age_min / 60
    if hours < 24:
        return f"{hours:.1f} h ago"
    return f"{hours / 24:.1f} d ago"


def render_freshness_badges() -> None:
    """Call inside a `with st.sidebar:` block."""
    try:
        from data.demo_store import _load_or_init
        live = _load_or_init()
        sync_rows = live.get("etl_sync_log", [])
    except Exception:
        return

    if not sync_rows:
        return

    st.sidebar.markdown("---")
    st.sidebar.caption("**Data freshness**")
    now = datetime.now(timezone.utc)

    for row in sync_rows:
        table     = row.get("table_name", "unknown")
        synced_at = row.get("synced_at", "")
        display   = FRESHNESS_TABLE_LABELS.get(table, table.replace("_", " ").title())
        try:
            ts      = datetime.fromisoformat(synced_at.replace("Z", "+00:00"))
            age_min = (now - ts).total_seconds() / 60
        except Exception:
            st.sidebar.caption(f"• {display}: —")
            continue

        threshold = _STALE_MINUTES.get(table, 120)
        age_text  = _age_label(age_min)
        if age_min > threshold:
            st.sidebar.warning(f"{display}: {age_text} ⚠")
        else:
            st.sidebar.caption(f"• {display}: {age_text}")
