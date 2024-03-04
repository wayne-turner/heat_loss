import pandas as pd
import itertools

def compute_specific_heat_loss(sqft_roof=1800, sqft_walls=1500, roof_material_type='asphalt', wall_material_type='wood', ambient_temp_F=50, T_inside_F=70, duration_hours=24,
                              insulation_r_value='R13-R15', air_changes_per_hour=0.5, window_area_sqft=500, window_type='double',
                              electricity_cost_per_kWh=0.12):
    """
    calc the total heat loss and associated cost over duration.
    
    args:
        sqft_roof (float): Square footage of the roof.
        sqft_walls (float): Square footage of the walls.
        roof_material_type (str): Type of material used for the roof (options: 'asphalt', 'wood', 'metal', 'tile').
        wall_material_type (str): Type of material used for the walls (options: 'brick', 'concrete', 'wood').
        ambient_temp_F (float): Ambient temperature in Fahrenheit.
        T_inside_F (float): Interior temperature in Fahrenheit.
        duration_hours (int): Duration of the heat loss calculation in hours.
        insulation_r_value (str, optional): Insulation R-value category. Defaults to 'R13-R15'.
        air_changes_per_hour (float, optional): Air changes per hour. Defaults to 0.5.
        window_area_sqft (float, optional): Area of windows in square feet. Defaults to 500.
        window_type (str, optional): Type of window (options: 'single', 'double', 'triple'). Defaults to 'double'.
        electricity_cost_per_kWh (float, optional): Cost of electricity per kWh. Defaults to 0.12.
    
    returns:
        DataFrame: containing inputs used and calc Q_total_kWh, total_cost.
    """
    
    # constants
    SQFT_TO_SQM = 0.092903
    HOURS_TO_SECONDS = 3600
    JOULES_TO_KWH = 3600000
    CEILING_HEIGHT_M = 2.5
    F_TO_C = 1.8
    ROOF_MATERIALS = {
        'asphalt': {'thermal_conductivity': 0.2, 'thickness': 0.005},
        'wood': {'thermal_conductivity': 0.08, 'thickness': 0.01},
        'metal': {'thermal_conductivity': 50, 'thickness': 0.0007},
        'tile': {'thermal_conductivity': 1.1, 'thickness': 0.015}
    }
    WALL_MATERIALS = {
        'brick': {'thermal_conductivity': 0.6, 'thickness': 0.2},
        'concrete': {'thermal_conductivity': 1.0, 'thickness': 0.15},
        'wood': {'thermal_conductivity': 0.12, 'thickness': 0.1}
    }
    WINDOW_U_VALUES = {'single': 5.7, 'double': 2.8, 'triple': 1.6}
    INFILTRATION_FACTOR = 0.33
    INSULATION_R_VALUES = {
        'R13-R15': 14, 
        'R16-R21': 18, 
        'R22-R33': 28,
        'R34-R60': 47
    }

    # validation
    def validate_input(parameter, value, value_type):
        if not isinstance(value, value_type) or value <= 0:
            return f"Invalid value for {parameter}. must be a positive number."
        return None

    validation_errors = [
        validate_input('sqft_roof', sqft_roof, (int, float)),
        validate_input('sqft_walls', sqft_walls, (int, float)),
        "invalid roof material type. asphalt, wood, metal, or tile." if roof_material_type not in ROOF_MATERIALS else None,
        "invalid wall material type. brick, concrete, wood." if wall_material_type not in WALL_MATERIALS else None,
        "invalid insulation R-value. 'R13-R15','R16-R21','R22-R33','R34-R60'" if insulation_r_value not in INSULATION_R_VALUES else None,
        "invalid input type for one or more parameters. must be numeric values or specified categories." if not all(isinstance(val, (int, float, str)) for val in [ambient_temp_F, T_inside_F, duration_hours, air_changes_per_hour, window_area_sqft, electricity_cost_per_kWh]) else None
    ]

    validation_errors = [error for error in validation_errors if error is not None]
    if validation_errors:
        return pd.DataFrame({"Error": validation_errors})

    # temp diff
    delta_T_C = (T_inside_F - ambient_temp_F) / F_TO_C

    # r-value conversion
    insulation_r_value_SI = INSULATION_R_VALUES[insulation_r_value] * 0.176110

    # material thickness
    thickness_roof_m = ROOF_MATERIALS[roof_material_type]['thickness']
    thickness_wall_m = WALL_MATERIALS[wall_material_type]['thickness']

    # convert sf to sm
    area_roof_m2 = sqft_roof * SQFT_TO_SQM
    area_walls_m2 = sqft_walls * SQFT_TO_SQM

    # loss through roof and walls
    def calculate_heat_loss(area, thickness, material_type):
        return (area * delta_T_C) / (thickness / material_type['thermal_conductivity'] + insulation_r_value_SI)

    Q_roof_material = calculate_heat_loss(area_roof_m2, thickness_roof_m, ROOF_MATERIALS[roof_material_type])
    Q_walls_material = calculate_heat_loss(area_walls_m2, thickness_wall_m, WALL_MATERIALS[wall_material_type])

    # time conversion
    t_seconds = duration_hours * HOURS_TO_SECONDS

    # loss from materials
    Q_roof_total_joules = Q_roof_material * t_seconds
    Q_walls_total_joules = Q_walls_material * t_seconds

    # conversion to kWh
    Q_roof_total_kWh = Q_roof_total_joules / JOULES_TO_KWH
    Q_walls_total_kWh = Q_walls_total_joules / JOULES_TO_KWH

    # air infiltration loss
    volume_m3 = (sqft_roof + sqft_walls) * SQFT_TO_SQM * CEILING_HEIGHT_M
    air_infiltration_loss_kWh = (volume_m3 * air_changes_per_hour * duration_hours * (T_inside_F - ambient_temp_F) / F_TO_C * INFILTRATION_FACTOR) / JOULES_TO_KWH

    # window loss
    window_area_m2 = window_area_sqft * SQFT_TO_SQM
    window_heat_loss_kWh = (window_area_m2 * WINDOW_U_VALUES[window_type] * delta_T_C * duration_hours) / JOULES_TO_KWH

    # total loss
    Q_total_kWh = Q_roof_total_kWh + Q_walls_total_kWh + air_infiltration_loss_kWh + window_heat_loss_kWh

    # electricity cost
    total_cost = Q_total_kWh * electricity_cost_per_kWh

    data = {
        'sqft_roof': [sqft_roof],
        'sqft_walls': [sqft_walls],
        'roof_material_type': [roof_material_type],
        'wall_material_type': [wall_material_type],
        'ambient_temp_F': [ambient_temp_F],
        'T_inside_F': [T_inside_F],
        'duration_hours': [duration_hours],
        'insulation_r_value': [insulation_r_value],
        'air_changes_per_hour': [air_changes_per_hour],
        'window_area_sqft': [window_area_sqft],
        'window_type': [window_type],
        'electricity_cost_per_kWh': [electricity_cost_per_kWh],
        'total_cost': [total_cost],
        'Q_total_kWh': [Q_total_kWh],
    }
    df = pd.DataFrame(data)

    return df


def heat_loss_scenarios(sqft_roof=1800, sqft_walls=1500, ambient_temp_F=50, T_inside_F=70, duration_hours=24,
               air_changes_per_hour=0.5, window_area_sqft=500, electricity_cost_per_kWh=0.12):
    """
    gen heat loss calcs across range of roof materials, window types, and insulation R-values, optional user input.

    args:
        sqft_roof (float): Square footage of the roof.
        sqft_walls (float): Square footage of the walls.
        ambient_temp_F (float): Ambient temperature in Fahrenheit.
        T_inside_F (float): Interior temperature in Fahrenheit.
        duration_hours (int): Duration of the heat loss calculation in hours.
        air_changes_per_hour (float): Air changes per hour.
        window_area_sqft (float): Area of windows in square feet.
        electricity_cost_per_kWh (float): Cost of electricity per kWh.
    
    returns:
        DataFrame: containing inputs and calc Q_total_kWh, total_cost for various combinations of roof materials, window types,  insulation R-values.
    """
    roof_materials = ['asphalt', 'wood', 'metal', 'tile']
    window_types = ['single', 'double', 'triple']
    insulation_values = ['R13-R15', 'R16-R21', 'R22-R33', 'R34-R60']
    
    # gen combinations
    combinations = itertools.product(roof_materials, window_types, insulation_values)
    
    # each combination
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
            insulation_r_value=insulation
        ) for roof, window, insulation in combinations
    ]
    results = pd.concat(results_list)
    
    # column exists
    if 'Q_total_kWh' in results.columns:
        results = results.sort_values(by='Q_total_kWh', ascending=True)
    else:
        raise KeyError("Column 'Q_total_kWh' does not exist in the results DataFrame.")
    
    return results
