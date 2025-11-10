import argparse
from heat_loss_simulation import compute_specific_heat_loss

PROFILES = {
    "1950s_leaky_home": {
        "roof_material_type": "asphalt",
        "wall_material_type": "brick",
        "insulation_r_value": "R13-R15",
        "air_changes_per_hour": 0.9,
        "window_type": "single",
    },
    "new_code_min": {
        "roof_material_type": "wood",
        "wall_material_type": "wood",
        "insulation_r_value": "R22-R33",
        "air_changes_per_hour": 0.5,
        "window_type": "double",
    },
    "high_performance": {
        "roof_material_type": "wood",
        "wall_material_type": "wood",
        "insulation_r_value": "R34-R60",
        "air_changes_per_hour": 0.3,
        "window_type": "triple",
    },
}


def _ask_float(prompt, default):
    text = input(f"{prompt} [{default}]: ").strip()
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        print("invalid number, using default.")
        return default


def _print_profiles():
    print("profiles:")
    for name, params in PROFILES.items():
        print(f"  {name}:")
        for key, value in params.items():
            print(f"    {key} = {value}")


def main():
    parser = argparse.ArgumentParser(
        description="heat loss cli with presets and simple prompts"
    )
    parser.add_argument("--profile",choices=sorted(PROFILES.keys()),help="preset profile name",)
    parser.add_argument("--sqft-roof",type=float,help="roof area in sqft",)
    parser.add_argument("--sqft-walls",type=float,help="wall area in sqft",)
    parser.add_argument("--ambient-temp",type=float,help="ambient temp in F",)
    parser.add_argument("--inside-temp",type=float,help="inside temp in F",)
    parser.add_argument("--duration-hours",type=float,help="duration in hours",)
    parser.add_argument("--window-area",type=float,help="window area in sqft",)
    parser.add_argument("--roof-material",choices=["asphalt", "wood", "metal", "tile"],help="roof material type",)
    parser.add_argument("--wall-material",choices=["brick", "concrete", "wood"],help="wall material type",)
    parser.add_argument("--insulation",choices=["R13-R15", "R16-R21", "R22-R33", "R34-R60"],help="insulation r band",)
    parser.add_argument("--ach",type=float,help="air changes per hour",)
    parser.add_argument("--window-type",choices=["single", "double", "triple"],help="window type",)
    parser.add_argument("--electricity-cost",type=float,help="electricity cost per kWh",)
    parser.add_argument("--list-profiles",action="store_true",help="list preset profiles and exit",)

    args = parser.parse_args()

    if args.list_profiles:
        _print_profiles()
        return

    params = {}

    if args.profile:
        params.update(PROFILES[args.profile])

    if args.roof_material:
        params["roof_material_type"] = args.roof_material
    if args.wall_material:
        params["wall_material_type"] = args.wall_material
    if args.insulation:
        params["insulation_r_value"] = args.insulation
    if args.ach is not None:
        params["air_changes_per_hour"] = args.ach
    if args.window_type:
        params["window_type"] = args.window_type
    if args.electricity_cost is not None:
        params["electricity_cost_per_kWh"] = args.electricity_cost

    if args.sqft_roof is not None:
        params["sqft_roof"] = args.sqft_roof
    if args.sqft_walls is not None:
        params["sqft_walls"] = args.sqft_walls
    if args.ambient_temp is not None:
        params["ambient_temp_F"] = args.ambient_temp
    if args.inside_temp is not None:
        params["T_inside_F"] = args.inside_temp
    if args.duration_hours is not None:
        params["duration_hours"] = args.duration_hours
    if args.window_area is not None:
        params["window_area_sqft"] = args.window_area

    if "sqft_roof" not in params:
        params["sqft_roof"] = _ask_float("roof area sqft", 1800)
    if "sqft_walls" not in params:
        params["sqft_walls"] = _ask_float("wall area sqft", 1500)
    if "ambient_temp_F" not in params:
        params["ambient_temp_F"] = _ask_float("ambient temp F", 50)
    if "T_inside_F" not in params:
        params["T_inside_F"] = _ask_float("inside temp F", 70)

    df = compute_specific_heat_loss(**params)

    if "Error" in df.columns:
        print("error in inputs:")
        for msg in df["Error"]:
            print(f"  - {msg}")
        return

    cols = [
        "roof_material_type",
        "wall_material_type",
        "insulation_r_value",
        "window_type",
        "air_changes_per_hour",
        "sqft_roof",
        "sqft_walls",
        "window_area_sqft",
        "ambient_temp_F",
        "T_inside_F",
        "duration_hours",
        "Q_roof_kWh",
        "Q_walls_kWh",
        "Q_windows_kWh",
        "Q_infiltration_kWh",
        "Q_total_kWh",
        "Q_roof_pct",
        "Q_walls_pct",
        "Q_windows_pct",
        "Q_infiltration_pct",
        "total_cost",
    ]

    existing_cols = [c for c in cols if c in df.columns]
    out = df[existing_cols].copy()
    numeric_cols = out.select_dtypes(include="number").columns
    out[numeric_cols] = out[numeric_cols].round(2)

    print(out.to_string(index=False))


if __name__ == "__main__":
    main()

