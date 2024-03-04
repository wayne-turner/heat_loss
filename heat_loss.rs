use std::collections::HashMap;

#[derive(Debug)]
struct MaterialProperties {
    thermal_conductivity: f64,
    thickness: f64,
}

#[derive(Debug)]
struct CalculationInput {
    sqft_roof: f64,
    sqft_walls: f64,
    roof_material_type: String,
    wall_material_type: String,
    ambient_temp_f: f64,
    t_inside_f: f64,
    duration_hours: u64,
    insulation_r_value: String,
    air_changes_per_hour: f64,
    window_area_sqft: f64,
    window_type: String,
    electricity_cost_per_kwh: f64,
}

#[derive(Debug)]
struct CalculationResult {
    total_cost: f64,
    q_total_kwh: f64,
}

// Constants (example)
const SQFT_TO_SQM: f64 = 0.092903;
const HOURS_TO_SECONDS: u64 = 3600;
const F_TO_C: f64 = 1.8;
const JOULES_TO_KWH: f64 = 3600000.0;

fn calculate_heat_loss(
    area: f64,
    delta_t_c: f64,
    material: &MaterialProperties,
    insulation_r_value_si: f64,
) -> f64 {
    area * delta_t_c / (material.thickness / material.thermal_conductivity + insulation_r_value_si)
}

fn compute_specific_heat_loss(input: &CalculationInput) -> Result<CalculationResult, &'static str> {
    let roof_materials = HashMap::from([
        ("asphalt".to_string(), MaterialProperties { thermal_conductivity: 0.2, thickness: 0.005 }),
        ("wood".to_string(), MaterialProperties { thermal_conductivity: 0.08, thickness: 0.01 }),
        // Add other materials as needed
    ]);

    let wall_materials = HashMap::from([
        ("wood".to_string(), MaterialProperties { thermal_conductivity: 0.12, thickness: 0.1 }),
        // Add other materials as needed
    ]);

    let roof_material = roof_materials.get(&input.roof_material_type).ok_or("Invalid roof material type")?;
    let wall_material = wall_materials.get(&input.wall_material_type).ok_or("Invalid wall material type")?;

    let delta_t_c = (input.t_inside_f - input.ambient_temp_f) / F_TO_C;
    let insulation_r_value_si = match input.insulation_r_value.as_str() {
        "R13-R15" => 14.0 * 0.176110, // Convert to SI units
        _ => return Err("Invalid insulation R-value"),
    };

    let area_roof_m2 = input.sqft_roof * SQFT_TO_SQM;
    let area_walls_m2 = input.sqft_walls * SQFT_TO_SQM;

    let q_roof = calculate_heat_loss(area_roof_m2, delta_t_c, roof_material, insulation_r_value_si);
    let q_walls = calculate_heat_loss(area_walls_m2, delta_t_c, wall_material, insulation_r_value_si);

    let q_total_joules = (q_roof + q_walls) * input.duration_hours as f64 * HOURS_TO_SECONDS as f64;
    let q_total_kwh = q_total_joules / JOULES_TO_KWH;

    let total_cost = q_total_kwh * input.electricity_cost_per_kwh;

    Ok(CalculationResult {
        total_cost,
        q_total_kwh,
    })
}

fn main() {
    let input = CalculationInput {
        sqft_roof: 1800.0,
        sqft_walls: 1500.0,
        roof_material_type: "asphalt".to_string(),
        wall_material_type: "wood".to_string(),
        ambient_temp_f: 50.0,
        t_inside_f: 70.0,
        duration_hours: 24,
        insulation_r_value: "R13-R15".to_string(),
        air_changes_per_hour: 0.5,
        window_area_sqft: 500.0,
        window_type: "double".to_string(),
        electricity_cost_per_kwh: 0.12,
    };

    match compute_specific_heat_loss(&input) {
        Ok(result) => println!("Total cost: {:.2}, Total kWh: {:.2}", result.total_cost, result.q_total_kwh),
        Err(e) => println!("Error: {}", e),
    }
}
