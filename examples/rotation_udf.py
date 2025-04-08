%%time
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StructType, StructField, DoubleType
import numpy as np

# User-defined function to compute group metrics using NumPy
def compute_group_metrics(mass, rel_vx, rel_vy, rel_vz, rel_px, rel_py, rel_pz, dist_cent_sq):
    # Convert inputs to numpy arrays for vectorized operations
    mass = np.array(mass)
    rel_vx = np.array(rel_vx)
    rel_vy = np.array(rel_vy)
    rel_vz = np.array(rel_vz)
    rel_px = np.array(rel_px)
    rel_py = np.array(rel_py)
    rel_pz = np.array(rel_pz)
    dist_cent_sq = np.array(dist_cent_sq)

    # Weighted averages
    mass_sum = np.sum(mass)
    vx_avg = np.sum(mass * rel_vx) / mass_sum
    vy_avg = np.sum(mass * rel_vy) / mass_sum
    vz_avg = np.sum(mass * rel_vz) / mass_sum

    # Velocity dispersion
    vx_disp = (rel_vx - vx_avg) ** 2
    vy_disp = (rel_vy - vy_avg) ** 2
    vz_disp = (rel_vz - vz_avg) ** 2
    dispersion_weighted = mass * (vx_disp + vy_disp + vz_disp)
    velocity_dispersion = np.sqrt(np.sum(dispersion_weighted) / mass_sum)

    # Angular momentum components
    #v_vec = np.array([rel_vx, rel_vy, rel_vz])
    #r_vec = np.array([rel_px, rel_py, rel_pz])
    v_vec = np.column_stack((rel_vx, rel_vy, rel_vz))  # Shape (N, 3)
    r_vec = np.column_stack((rel_px, rel_py, rel_pz))  # Shape (N, 3)

    
    j_vec = np.cross(r_vec, v_vec) * mass[:, None]  # Cross product per element
    j_tot = np.sum(j_vec, axis=0)
    j_tot_norm = j_tot / np.linalg.norm(j_tot)
    
    j_rot = np.dot(j_vec, j_tot_norm)  # Dot product for rotational component
    R_tot = np.dot(r_vec, j_tot_norm)  # Dot product for R_tot
    R_rot = np.sqrt(dist_cent_sq - R_tot**2)

    # Filter out invalid values
    valid_mask = R_rot != 0
    m_valid = mass[valid_mask]
    j_rot_valid = j_rot[valid_mask]
    R_rot_valid = R_rot[valid_mask]

    mV_rot = j_rot_valid / R_rot_valid
    velocity_rotation = np.sum(mV_rot) / mass_sum

    #return (velocity_dispersion, velocity_rotation)
    return float(velocity_dispersion), float(velocity_rotation)

# Define the schema for the UDF output
schema = StructType([
    StructField("velocity_dispersion", DoubleType(), False),
    StructField("velocity_rotation", DoubleType(), False)
])

# Register the UDF with PySpark
compute_group_metrics_udf = udf(compute_group_metrics, schema)

# Apply the UDF to the PySpark DataFrame, grouped by "sub_id"
# Use `groupBy` and `agg` to apply the UDF for each group (sub_id)
#velocity_dispersion_df = df.groupBy("sub_id").agg(
#    compute_group_metrics_udf(
#        col("mass"), col("rel_vx"), col("rel_vy"), col("rel_vz"),
#        col("rel_px"), col("rel_py"), col("rel_pz"), col("dist_cent_sq")
#    ).alias("metrics")
#)

from pyspark.sql.functions import collect_list

subname = 'hdfs://sohnic:54310/data/TNG300/snap62/parquet/extracted_region_less_cube_z0p62_241112.parquet.snappy'

df = spark.read.parquet(subname)

# Group by "sub_id" and collect the necessary columns
grouped_df = df.groupBy("sub_id").agg(
    collect_list("mass").alias("mass"),
    collect_list("rel_vx").alias("rel_vx"),
    collect_list("rel_vy").alias("rel_vy"),
    collect_list("rel_vz").alias("rel_vz"),
    collect_list("rel_px").alias("rel_px"),
    collect_list("rel_py").alias("rel_py"),
    collect_list("rel_pz").alias("rel_pz"),
    collect_list("dist_cent_sq").alias("dist_cent_sq")
)

# Apply the UDF to compute the group metrics
velocity_dispersion_df = grouped_df.withColumn(
    "metrics", 
    compute_group_metrics_udf(
        col("mass"), col("rel_vx"), col("rel_vy"), col("rel_vz"),
        col("rel_px"), col("rel_py"), col("rel_pz"), col("dist_cent_sq")
    )
)

# Extract and clean up the results
velocity_dispersion_df = velocity_dispersion_df.withColumn("velocity_dispersion", col("metrics.velocity_dispersion")) \
                                               .withColumn("velocity_rotation", col("metrics.velocity_rotation")) \
                                               .drop("metrics")
velocity_dispersion_df = velocity_dispersion_df.select(['sub_id', 'velocity_dispersion', 'velocity_rotation'])
# Show the results
velocity_dispersion_df.show()
