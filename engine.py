from pathlib import Path
from datetime import datetime
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import webbrowser


OPENER_WINDOW_MINUTES = 90


def load_schedule(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required_cols = {"date", "name", "role", "start_time", "end_time"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"])
    return df


def validate_schedule(df: pd.DataFrame) -> list[str]:
    warnings = []

    if df["start_time"].isna().any() or df["end_time"].isna().any():
        warnings.append("Some rows are missing start/end times.")

    return warnings


def time_to_minutes(time_str: str) -> int:
    dt = datetime.strptime(str(time_str).strip(), "%H:%M")
    return dt.hour * 60 + dt.minute


def is_tire_tech(role: str) -> bool:
    return str(role).lower().strip() == "tbc tire tech"


def is_service_advisor(role: str) -> bool:
    return str(role).lower().strip() == "service advisor"


def is_team_lead(role: str) -> bool:
    return str(role).lower().strip() in {"tbc lead", "team lead"}


def pick_backup(day_df: pd.DataFrame) -> tuple[str, str]:
    advisors = day_df[day_df["role"].apply(is_service_advisor)]
    leads = day_df[day_df["role"].apply(is_team_lead)]

    primary = advisors.iloc[0]["name"] if not advisors.empty else ""
    secondary = leads.iloc[0]["name"] if not leads.empty else ""

    return primary, secondary


def choose_fair_candidate(candidates, counts, last_used):
    if not candidates:
        return ""

    return min(
        set(candidates),
        key=lambda x: (
            counts.get(x, 0),
            last_used.get(x, -9999),
            x
        )
    )


def filter_schedule_to_month(df, year, month):
    return df[
        (df["date"].dt.year == year) &
        (df["date"].dt.month == month)
    ]


def build_month_rows(schedule_df):
    grouped = schedule_df.groupby(schedule_df["date"].dt.date)

    opener_counts = {}
    closer_counts = {}
    opener_last = {}
    closer_last = {}

    rows = []
    index = 0

    for date_value, day_df in grouped:
        techs = day_df[day_df["role"].apply(is_tire_tech)].copy()

        opener = ""
        closer = ""

        primary_backup, secondary_backup = pick_backup(day_df)
        backup = " / ".join(filter(None, [primary_backup, secondary_backup]))

        if not techs.empty:
            techs["start_minutes"] = techs["start_time"].apply(time_to_minutes)
            techs["end_minutes"] = techs["end_time"].apply(time_to_minutes)

            earliest = techs["start_minutes"].min()
            opener_candidates = techs.loc[
                techs["start_minutes"] <= earliest + OPENER_WINDOW_MINUTES, "name"
            ].tolist()

            opener = choose_fair_candidate(opener_candidates, opener_counts, opener_last)

            if opener:
                opener_counts[opener] = opener_counts.get(opener, 0) + 1
                opener_last[opener] = index

            latest = techs["end_minutes"].max()

            # allow anyone who ends within 60 minutes of the latest scheduled tech
            closer_cutoff = latest - 60

            closer_candidates = techs.loc[
                techs["end_minutes"] >= closer_cutoff, "name"
            ].tolist()

            closer_candidates = [c for c in closer_candidates if c != opener] or closer_candidates

            closer = choose_fair_candidate(closer_candidates, closer_counts, closer_last)

            if closer:
                closer_counts[closer] = closer_counts.get(closer, 0) + 1
                closer_last[closer] = index

        rows.append({
            "day_name": pd.Timestamp(date_value).strftime("%A"),
            "date": pd.Timestamp(date_value).strftime("%m/%d/%Y"),
            "opener": opener or "UNASSIGNED",
            "closer": closer or "UNASSIGNED",
            "backup": backup,
            "notes": ""
        })

        index += 1

    rows.sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"))

    summary = pd.DataFrame([
        {
            "name": name,
            "opener_assignments": opener_counts.get(name, 0),
            "closer_assignments": closer_counts.get(name, 0),
        }
        for name in set(opener_counts) | set(closer_counts)
    ])

    if not summary.empty:
        summary["total"] = summary["opener_assignments"] + summary["closer_assignments"]

    return rows, summary


def build_template_data(rows, year, month, summary):
    return {
        "club_number": "",
        "week_begin_date": datetime(year, month, 1).strftime("%B %Y"),
        "printed_timestamp": datetime.now().strftime("%B %d, %Y %I:%M %p"),
        "prepared_by": "Manager",
        "week_rows": rows,
        "row_height": 18,
        "table_font_size": 10,
    }


def render_template(template_path, output_path, data):
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    output_path.write_text(template.render(**data), encoding="utf-8")


def generate_sheet(csv_path, template_path, output_html, output_summary):
    df = load_schedule(csv_path)

    warnings = validate_schedule(df)

    first = df["date"].min()
    year, month = first.year, first.month

    df = filter_schedule_to_month(df, year, month)

    rows, summary = build_month_rows(df)
    data = build_template_data(rows, year, month, summary)

    render_template(template_path, output_html, data)

    if not summary.empty:
        summary.to_csv(output_summary, index=False)

    webbrowser.open(str(output_html))

    return warnings, len(rows), year, month