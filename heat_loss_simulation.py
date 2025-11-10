import pandas as pd
import itertools


def compute_specific_heat_loss(
    sqft_roof=1800,
    sqft_walls=1500,
    roof_material_type="wood",
    wall_material_type="wood",
    ambient_temp_F=50,
    T_inside_F=70,
    duration_hours=24,
    insulation_r_value="R13-R15",
    air_changes_per_hour=0.5,
    window_area_sqft=500,
    window_type="double",
    electricity_cost_per_kWh=0.12,
):
    """
    calc the total heat loss and associated cost over duration.

    args:
        sqft_roof (float): square footage of the roof.
        sqft_walls (float): square footage of the walls.
        roof_material_type (str): roof material ('asphalt','wood','metal','tile').
        wall_material_type (str): wall material ('brick','concrete','wood').
        ambient_temp_F (float): ambient temp in F.
        T_inside_F (float): interior temp in F.
        duration_hours (float): duration in hours.
        insulation_r_value (str): insulation band ('R13-R15','R16-R21','R22-R33','R34-R60').
        air_changes_per_hour (float): air changes per hour.
        window_area_sqft (float): window area in square feet.
        window_type (str): window type ('single','double','triple').
        electricity_cost_per_kWh (float): electricity cost per kWh.

    returns:
        DataFrame: inputs used and calc Q_total_kWh, total_cost, and per-component breakdown.
    """

    # constants
    SQFT_TO_SQM = 0.092903
    HOURS_TO_SECONDS = 3600
    JOULES_TO_KWH = 3_600_000
    CEILING_HEIGHT_M = 2.5
    F_TO_C = 1.8

    ROOF_MATERIALS = {
        "asphalt": {"thermal_conductivity": 0.2, "thickness": 0.005},
        "wood": {"thermal_conductivity": 0.08, "thickness": 0.01},
        "metal": {"thermal_conductivity": 50, "thickness": 0.0007},
        "tile": {"thermal_conductivity": 1.1, "thickness": 0.015},
    }

    WALL_MATERIALS = {
        "brick": {"thermal_conductivity": 0.6, "thickness": 0.2},
        "concrete": {"thermal_conductivity": 1.0, "thickness": 0.15},
        "wood": {"thermal_conductivity": 0.12, "thickness": 0.1},
    }

    WINDOW_U_VALUES = {"single": 5.7, "double": 2.8, "triple": 1.6}

    # approx Wh / (m3 * K) for air
    INFILTRATION_FACTOR = 0.33

    INSULATION_R_VALUES = {
        "R13-R15": 14,
        "R16-R21": 18,
        "R22-R33": 28,
        "R34-R60": 47,
    }

    def validate_input(parameter, value, value_type):
        if not isinstance(value, value_type) or value <= 0:
            return f"invalid value for {parameter}. must be a positive number."
        return None

    validation_errors = [
        validate_input("sqft_roof", sqft_roof, (int, float)),
        validate_input("sqft_walls", sqft_walls, (int, float)),
        "invalid roof material type. asphalt, wood, metal, or tile."
        if roof_material_type not in ROOF_MATERIALS
        else None,
        "invalid wall material type. brick, concrete, wood."
        if wall_material_type not in WALL_MATERIALS
        else None,
        "invalid insulation R-value. 'R13-R15','R16-R21','R22-R33','R34-R60'"
        if insulation_r_value not in INSULATION_R_VALUES
        else None,
        "invalid window type. 'single','double','triple'."
        if window_type not in WINDOW_U_VALUES
        else None,
        "invalid input type for one or more parameters. must be positive numeric."
        if not all(
            isinstance(v, (int, float)) and v > 0
            for v in [
                ambient_temp_F,
                T_inside_F,
                duration_hours,
                air_changes_per_hour,
                window_area_sqft,
                electricity_cost_per_kWh,
            ]
        )
        else None,
    ]

    validation_errors = [error for error in validation_errors if error is not None]
    if validation_errors:
        return pd.DataFrame({"Error": validation_errors})

    delta_T_C = (T_inside_F - ambient_temp_F) / F_TO_C

    insulation_r_value_SI = INSULATION_R_VALUES[insulation_r_value] * 0.176110

    thickness_roof_m = ROOF_MATERIALS[roof_material_type]["thickness"]
    thickness_wall_m = WALL_MATERIALS[wall_material_type]["thickness"]

    area_roof_m2 = sqft_roof * SQFT_TO_SQM
    area_walls_m2 = sqft_walls * SQFT_TO_SQM

    def conduction_loss_W(area_m2, thickness_m, material):
        return (area_m2 * delta_T_C) / (
            thickness_m / material["thermal_conductivity"] + insulation_r_value_SI
        )

    Q_roof_W = conduction_loss_W(
        area_roof_m2, thickness_roof_m, ROOF_MATERIALS[roof_material_type]
    )
    Q_walls_W = conduction_loss_W(
        area_walls_m2, thickness_wall_m, WALL_MATERIALS[wall_material_type]
    )

    t_seconds = duration_hours * HOURS_TO_SECONDS

    Q_roof_J = Q_roof_W * t_seconds
    Q_walls_J = Q_walls_W * t_seconds

    Q_roof_kWh = Q_roof_J / JOULES_TO_KWH
    Q_walls_kWh = Q_walls_J / JOULES_TO_KWH

    volume_m3 = (sqft_roof + sqft_walls) * SQFT_TO_SQM * CEILING_HEIGHT_M
    air_infiltration_kWh = (
        volume_m3
        * air_changes_per_hour
        * delta_T_C
        * INFILTRATION_FACTOR
        * duration_hours
        / 1000.0
    )

    window_area_m2 = window_area_sqft * SQFT_TO_SQM
    Q_windows_W = (
        window_area_m2 * WINDOW_U_VALUES[window_type] * delta_T_C
    )
    Q_windows_J = Q_windows_W * t_seconds
    Q_windows_kWh = Q_windows_J / JOULES_TO_KWH

    Q_total_kWh = Q_roof_kWh + Q_walls_kWh + air_infiltration_kWh + Q_windows_kWh

    if Q_total_kWh > 0:
        pct_roof = Q_roof_kWh / Q_total_kWh * 100.0
        pct_walls = Q_walls_kWh / Q_total_kWh * 100.0
        pct_windows = Q_windows_kWh / Q_total_kWh * 100.0
        pct_infiltration = air_infiltration_kWh / Q_total_kWh * 100.0
    else:
        pct_roof = pct_walls = pct_windows = pct_infiltration = 0.0

    total_cost = Q_total_kWh * electricity_cost_per_kWh

    data = {
        "sqft_roof": [sqft_roof],
        "sqft_walls": [sqft_walls],
        "roof_material_type": [roof_material_type],
        "wall_material_type": [wall_material_type],
        "ambient_temp_F": [ambient_temp_F],
        "T_inside_F": [T_inside_F],
        "duration_hours": [duration_hours],
        "insulation_r_value": [insulation_r_value],
        "air_changes_per_hour": [air_changes_per_hour],
        "window_area_sqft": [window_area_sqft],
        "window_type": [window_type],
        "electricity_cost_per_kWh": [electricity_cost_per_kWh],
        "Q_roof_kWh": [Q_roof_kWh],
        "Q_walls_kWh": [Q_walls_kWh],
        "Q_windows_kWh": [Q_windows_kWh],
        "Q_infiltration_kWh": [air_infiltration_kWh],
        "Q_roof_pct": [pct_roof],
        "Q_walls_pct": [pct_walls],
        "Q_windows_pct": [pct_windows],
        "Q_infiltration_pct": [pct_infiltration],
        "total_cost": [total_cost],
        "Q_total_kWh": [Q_total_kWh],
    }

    df = pd.DataFrame(data)
    return df


def heat_loss_scenarios(
    sqft_roof=1800,
    sqft_walls=1500,
    ambient_temp_F=50,
    T_inside_F=70,
    duration_hours=24,
    air_changes_per_hour=0.5,
    window_area_sqft=500,
    electricity_cost_per_kWh=0.12,
):
    """
    gen heat loss calcs across range of roof materials, window types, and insulation R-values.

    args:
        sqft_roof (float): square footage of the roof.
        sqft_walls (float): square footage of the walls.
        ambient_temp_F (float): ambient temp in F.
        T_inside_F (float): interior temp in F.
        duration_hours (float): duration in hours.
        air_changes_per_hour (float): air changes per hour.
        window_area_sqft (float): window area in square feet.
        electricity_cost_per_kWh (float): cost of electricity per kWh.

    returns:
        DataFrame: heat loss, cost, and component breakdown for combinations of materials and insulation.
    """
    roof_materials = ["asphalt", "wood", "metal", "tile"]
    window_types = ["single", "double", "triple"]
    insulation_values = ["R13-R15", "R16-R21", "R22-R33", "R34-R60"]
    
    combinations = itertools.product(roof_materials, window_types, insulation_values)
    results_list = [
        compute_specific_heat_loss(
            sqft_roof=sqft_roof,
            sqft_walls=sqft_walls,
            ambient_temp_F=ambient_temp_F,
            T_inside_F=T_inside_F,
            duration_hours=duration_hours,
            air_changes_per_hour=air_changes_per_hour,
            window_area_sqft=window_area_sqft,
            electricity_cost_per_kWh=electricity_cost_per_kWh,
            roof_material_type=roof,
            window_type=window,
            insulation_r_value=insulation,
        )
        for roof, window, insulation in combinations
    ]
    results = pd.concat(results_list, ignore_index=True)

    if "Q_total_kWh" in results.columns:
        results = results.sort_values(by="Q_total_kWh", ascending=True)
    else:
        raise KeyError("column 'Q_total_kWh' does not exist in the results DataFrame.")

    return results

