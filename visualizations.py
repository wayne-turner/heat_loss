import pandas as pd
from matplotlib.patches import Rectangle, Polygon
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt


def _require_columns(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")


def plot_heat_loss_by_insulation(df, ax=None):
    """
    args:
        df (DataFrame): output from heat_loss_scenarios().
        ax (matplotlib.axes.Axes, optional): axis to plot on.
    returns:
        matplotlib.axes.Axes
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    _require_columns(df, ["insulation_r_value", "Q_total_kWh"])
    grouped = (
        df.groupby("insulation_r_value", as_index=False)["Q_total_kWh"]
        .mean()
        .rename(columns={"Q_total_kWh": "Q_total_mean_kWh"})
    )
    order = ["R13-R15", "R16-R21", "R22-R33", "R34-R60"]
    present = [r for r in order if r in grouped["insulation_r_value"].tolist()]
    if present:
        grouped = (
            grouped.set_index("insulation_r_value")
            .loc[present]
            .reset_index()
        )
    if ax is None:
        fig, ax = plt.subplots()
    ax.bar(grouped["insulation_r_value"], grouped["Q_total_mean_kWh"])
    ax.set_xlabel("insulation r band")
    ax.set_ylabel("avg total heat loss (kWh)")
    ax.set_title("heat loss by insulation band")
    return ax


def plot_cost_by_window_type(df, ax=None):
    """
    args:
        df (DataFrame): output from heat_loss_scenarios().
        ax (matplotlib.axes.Axes, optional): axis to plot on.
    returns:
        matplotlib.axes.Axes
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    _require_columns(df, ["window_type", "total_cost"])
    grouped = (
        df.groupby("window_type", as_index=False)["total_cost"]
        .mean()
        .rename(columns={"total_cost": "total_cost_mean"})
    )
    order = ["single", "double", "triple"]
    present = [w for w in order if w in grouped["window_type"].tolist()]
    if present:
        grouped = (
            grouped.set_index("window_type")
            .loc[present]
            .reset_index()
        )
    if ax is None:
        fig, ax = plt.subplots()
    ax.bar(grouped["window_type"], grouped["total_cost_mean"])
    ax.set_xlabel("window type")
    ax.set_ylabel("avg total cost ($)")
    ax.set_title("cost by window type")
    return ax


def plot_component_breakdown(df_single_case, ax=None):
    """
    args:
        df_single_case (DataFrame or Series or dict):
            single row from compute_specific_heat_loss() or heat_loss_scenarios().
        ax (matplotlib.axes.Axes, optional): axis to plot on.
    returns:
        matplotlib.axes.Axes
    """
    if isinstance(df_single_case, pd.DataFrame):
        if df_single_case.shape[0] == 0:
            raise ValueError("df_single_case is empty")
        row = df_single_case.iloc[0]
    elif isinstance(df_single_case, pd.Series):
        row = df_single_case
    elif isinstance(df_single_case, dict):
        row = pd.Series(df_single_case)
    else:
        raise TypeError(
            "df_single_case must be a DataFrame, Series, or dict representing one case"
        )
    cols = [
        "Q_roof_kWh",
        "Q_walls_kWh",
        "Q_windows_kWh",
        "Q_infiltration_kWh",
    ]
    _require_columns(pd.DataFrame([row]), cols)
    labels = ["roof", "walls", "windows", "infiltration"]
    values = [
        row["Q_roof_kWh"],
        row["Q_walls_kWh"],
        row["Q_windows_kWh"],
        row["Q_infiltration_kWh"],
    ]
    if ax is None:
        fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_ylabel("heat loss (kWh)")
    ax.set_title("component breakdown")
    return ax


def plot_house_thermal_map(df_single_case, ax=None):
    """
    thermal-style house view.

    parameters:
    df_single_case : DataFrame, Series, or dict
        Single row from compute_specific_heat_loss() or heat_loss_scenarios().
    ax : matplotlib.axes.Axes, optional

    returns:
    matplotlib.axes.Axes
    """
    if isinstance(df_single_case, pd.DataFrame):
        if df_single_case.shape[0] == 0:
            raise ValueError("df_single_case is empty")
        row = df_single_case.iloc[0]
    elif isinstance(df_single_case, pd.Series):
        row = df_single_case
    elif isinstance(df_single_case, dict):
        row = pd.Series(df_single_case)
    else:
        raise TypeError(
            "df_single_case must be a DataFrame, Series, or dict representing one case"
        )

    cols = [
        "Q_roof_kWh",
        "Q_walls_kWh",
        "Q_windows_kWh",
        "Q_infiltration_kWh",
        "roof_material_type",
        "wall_material_type",
        "insulation_r_value",
        "window_type",
        "air_changes_per_hour",
        "ambient_temp_F",
        "T_inside_F",
        "total_cost",
        "Q_total_kWh",
    ]
    _require_columns(pd.DataFrame([row]), cols)

    q_roof = float(row["Q_roof_kWh"])
    q_walls = float(row["Q_walls_kWh"])
    q_windows = float(row["Q_windows_kWh"])
    q_infil = float(row["Q_infiltration_kWh"])
    total_q = float(row["Q_total_kWh"])
    if total_q <= 0:
        total_q = q_roof + q_walls + q_windows + q_infil
        if total_q <= 0:
            total_q = 1.0

    max_q = max(q_roof, q_walls, q_windows, q_infil, 1e-6)

    norm = Normalize(vmin=0, vmax=max_q)
    cmap = plt.cm.get_cmap("inferno")

    def color_for(q, alpha=1.0):
        rgba = list(cmap(norm(q)))
        rgba[3] = alpha
        return rgba

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    wall_rect = Rectangle(
        (0.2, 0.15),
        0.6,
        0.45,
        facecolor=color_for(q_walls, alpha=0.95),
        edgecolor="black",
        linewidth=1.5,
    )
    ax.add_patch(wall_rect)

    roof_poly = Polygon(
        [[0.2, 0.6], [0.5, 0.9], [0.8, 0.6]],
        closed=True,
        facecolor=color_for(q_roof, alpha=0.95),
        edgecolor="black",
        linewidth=1.5,
    )
    ax.add_patch(roof_poly)

    window1 = Rectangle(
        (0.26, 0.28),
        0.14,
        0.14,
        facecolor=color_for(q_windows, alpha=0.9),
        edgecolor="black",
        linewidth=1.0,
    )
    window2 = Rectangle(
        (0.60, 0.28),
        0.14,
        0.14,
        facecolor=color_for(q_windows, alpha=0.9),
        edgecolor="black",
        linewidth=1.0,
    )
    ax.add_patch(window1)
    ax.add_patch(window2)

    door = Rectangle(
        (0.46, 0.15),
        0.08,
        0.2,
        facecolor="#fdfdfd",
        edgecolor="black",
        linewidth=1.0,
    )
    ax.add_patch(door)

    pct_roof = q_roof / total_q * 100.0
    pct_walls = q_walls / total_q * 100.0
    pct_windows = q_windows / total_q * 100.0
    pct_infil = q_infil / total_q * 100.0

    # text labels
    ax.text(
        0.5,
        0.52,
        f"inside {row['T_inside_F']:.0f} F",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        0.02,
        0.96,
        f"outside {row['ambient_temp_F']:.0f} F",
        ha="left",
        va="top",
        fontsize=9,
    )
    ax.text(
        0.5,
        0.82,
        f"roof\n{q_roof:.1f} kWh\n{pct_roof:.0f}%",
        ha="center",
        va="center",
        fontsize=9,
    )
    ax.text(
        0.23,
        0.26,
        f"walls\n{q_walls:.1f} kWh\n{pct_walls:.0f}%",
        ha="center",
        va="center",
        fontsize=8,
    )
    ax.text(
        0.33,
        0.37,
        f"windows\n{q_windows:.1f} kWh\n{pct_windows:.0f}%",
        ha="center",
        va="center",
        fontsize=8,
    )
    ax.text(
        0.88,
        0.10,
        f"infiltration\n{q_infil:.1f} kWh\n{pct_infil:.0f}%",
        ha="center",
        va="center",
        fontsize=8,
    )
    ax.text(
        0.5,
        0.02,
        (
            f"roof: {row['roof_material_type']}, "
            f"walls: {row['wall_material_type']}, "
            f"insulation: {row['insulation_r_value']}, "
            f"windows: {row['window_type']}, "
            f"ACH: {row['air_changes_per_hour']}"
        ),
        ha="center",
        va="bottom",
        fontsize=8,
        wrap=True,
    )
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("heat loss (kWh)", fontsize=9)

    return ax

