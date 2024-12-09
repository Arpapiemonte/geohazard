## Geohazard Plugin

The Geohazard plugin provides four algorithms designed for analyzing and managing geohazards, including ground motion, shallow landslides, and rockfall events. Below is an overview of the available modules:

### **1. Groundmotion - C Index**

This algorithm calculates the **C index**, an indicator representing the percentage of detectable ground motion by a satellite. The C index ranges from -1 to 1 and is crucial for evaluating the satellite's ability to monitor ground deformation and terrain changes. 

The algorithm generates:
- A **C index map**, indicating areas of detectable motion.
- A **visibility percentage map**, highlighting the portion of terrain visible from the satellite based on radar acquisition angles.
- A **visibility class map**, dividing the terrain into five visibility classes to identify zones that can be monitored with varying precision.

### **2. SHALSTAB**

SHALSTAB is a physically-based model for assessing the risk of shallow landslides triggered by infiltrated rainfall, based on the methods by Montgomery & Dietrich (1994) and Dietrich & Montgomery (1998). It combines:
- A **limit equilibrium stability model** for infinite slopes.
- A **steady-state hydrological model**.

The algorithm evaluates slope instability hazard by estimating net infiltrated rainfall and classifying terrain into seven susceptibility classes. It provides a spatial hazard assessment (susceptibility) without temporal predictions. Model outputs should ideally be compared with observed landslides for validation.

### **3. DROKA BASIC**

DROKA BASIC employs the **Cone method** to define areas affected by rockfall events. This is achieved by modeling a cone-shaped envelope of potential rockfall paths. The cone's geometry is defined by:
- **Dip direction angle (θ)**: Orientation of the cone.
- **Energy angle (ϕp)**: Vertical extent.
- **Lateral spreading angle (α)**: Horizontal extent.

The algorithm produces a **frequency map**, showing areas most prone to rockfall impacts, aiding in identifying high-risk zones.

### **4. DROKA FLOW**

DROKA FLOW uses a hydrological approach to simulate potential rockfall paths by tracing the line of maximum slope from each source point. The path stops when the slope inclination becomes less than the user-defined **energy line inclination**.

Key features:
- Simulates five rockfall trajectories per source point using a **Monte Carlo approach**, adjusting DTM elevation within a user-defined standard deviation.
- Models variability in rockfall trajectories, accounting for factors like ground impact, bouncing, and obstacles (e.g., rocks, trees, or structures).

These tools provide valuable insights into geohazards, supporting effective risk management and mitigation strategies.
