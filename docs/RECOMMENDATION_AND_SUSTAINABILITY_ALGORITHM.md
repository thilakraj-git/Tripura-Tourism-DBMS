# Algorithmic Foundations: Recommendation Engine & Eco Responsibility Index

## 1. The Multi-Criteria Recommendation Algorithm

The Tripura Terra recommendation algorithm avoids black-box approaches, employing an **explainable, multi-attribute utility theory (MAUT)** framework that balances user preferences with ecological sustainability and crowding constraints.

### 1.1 Mathematical Formulation

For a user $u$ with preference profile $\mathbf{P}_u = \langle w_{\text{nat}}, w_{\text{cult}}, B_u, P_u, A_u \rangle$ and candidate destination $d \in \mathcal{D}$ with attribute vector $\mathbf{A}_d = \langle \tau_d, ERI_d, C_d, R_d, H_d \rangle$:

$$\text{AffinityScore}(u, d) = \Big( w_1 \cdot \text{Sim}_{\text{interest}}(u, d) + w_2 \cdot \frac{ERI_d}{100} + w_3 \cdot \Phi(C_d) + w_4 \cdot \frac{R_d}{5.0} + w_5 \cdot H_d \Big) \times 100$$

Where:
- $w_1 = 0.35$ (Interest similarity weight)
- $w_2 = 0.25$ (Eco Responsibility Index weight)
- $w_3 = 0.15$ (Crowd density cushion weight)
- $w_4 = 0.15$ (Empirical user satisfaction / rating weight)
- $w_5 = 0.10$ (Off-peak / lesser-known site promotion factor)

### 1.2 Sub-Component Definitions

1. **Interest Similarity $\text{Sim}_{\text{interest}}(u, d)$**:
   $$\text{Sim}_{\text{interest}}(u, d) = \frac{w_{\text{nat}} \cdot (1 - |w_{\text{nat}} - \tau_{d,\text{nat}}|) + w_{\text{cult}} \cdot (1 - |w_{\text{cult}} - \tau_{d,\text{cult}}|)}{w_{\text{nat}} + w_{\text{cult}}}$$
   Where $\tau_{d,\text{nat}}$ and $\tau_{d,\text{cult}}$ represent the inherent nature and cultural affinity characteristics of destination type $d$.

2. **Crowd Density Function $\Phi(C_d)$**:
   $$\Phi(C_d) = \begin{cases} 
   1.00 & \text{if } C_d = \text{'Very Low'} \\
   0.85 & \text{if } C_d = \text{'Low'} \\
   0.65 & \text{if } C_d = \text{'Moderate'} \\
   0.40 & \text{if } C_d = \text{'High'} 
   \end{cases}$$

3. **Accessibility Hard Filter**:
   If user profile specifies accessibility requirement ($A_u = 1$) and destination accessibility is limited ($d_{\text{access}} = \text{'Limited'}$):
   $$\text{AffinityScore}(u, d) = 0, \quad \text{Eligible}(u, d) = \text{False}$$

---

## 2. Eco Responsibility Index (ERI) Mathematical Model

The **Eco Responsibility Index (ERI)** provides a transparent, multi-indicator metric quantifying a destination's ecological health, conservation commitment, and sustainable tourism capacity.

### 2.1 ERI Composite Formula

$$ERI = \sum_{i=1}^{6} \lambda_i \cdot S_i$$

$$\begin{aligned}
ERI = &\; 0.25 \cdot \text{Bio} \\
      &+ 0.20 \cdot \max\big(0, 100 - 0.3 \cdot \text{Sens}\big) \\
      &+ 0.15 \cdot \text{Waste} \\
      &+ 0.15 \cdot \text{Comm} \\
      &+ 0.15 \cdot \max\big(0, 100 - \text{Pressure}\big) \\
      &+ 0.10 \cdot \text{Transit}
\end{aligned}$$

### 2.2 Parameter Breakdown

| Parameter | Indicator Name | Weight ($\lambda_i$) | Scale | Description |
|:---|:---|:---:|:---:|:---|
| **$\text{Bio}$** | Biodiversity Index | $0.25$ | $0-100$ | Richness of endemic avifauna, primates, and botanical density. |
| **$\text{Sens}$** | Habitat Sensitivity | $0.20$ | $0-100$ | Inverted vulnerability measure ($\max(0, 100 - 0.3 \times \text{Sens})$). |
| **$\text{Waste}$** | Waste Management | $0.15$ | $0-100$ | Zero-single-use-plastic enforcement and organic composting availability. |
| **$\text{Comm}$** | Community Benefit | $0.15$ | $0-100$ | Percentage of tourism revenue channeled directly to indigenous tribal workers. |
| **$\text{Pressure}$** | Visitor Pressure | $0.15$ | $0-100$ | Carrying capacity cushion calculated as $(100 - \text{Pressure})$. |
| **$\text{Transit}$** | Sustainable Transit | $0.10$ | $0-100$ | Access via walking trails, electric boats, or shared low-emission mobility. |

### 2.3 Tier Classifications

- **Tier I: Pristine Eco Sanctuary** ($ERI \ge 90.0$): Zero-plastic compliance, prime conservation corridor, indigenous co-management.
- **Tier II: High Sustainability Certified** ($80.0 \le ERI < 90.0$): Regulated visitor quotas, active waste management, moderate sensitivity.
- **Tier III: Balanced Cultural-Eco Site** ($70.0 \le ERI < 80.0$): Mixed visitor traffic with basic green amenities.
- **Tier IV: Developing Green Destination** ($ERI < 70.0$): High carrying pressure requiring priority infrastructure interventions.

---

## 3. Explainability Logic Generation

Every recommendation is supplemented with an explicit, rule-based natural language explanation generated directly from the mathematical contributor scores:

```text
Reasons = []
if interest_affinity > 0.8:
    Reasons.append("High affinity with your preference for " + dominant_interest)
if ERI >= 85.0:
    Reasons.append("Certified High Eco Responsibility Index (" + ERI + "/100)")
if crowd_score >= 0.85:
    Reasons.append("Low crowd density offering serene immersion")
if is_lesser_known:
    Reasons.append("Pristine lesser-known destination reducing mass-tourism pressure")
if average_rating >= 4.7:
    Reasons.append("Top-rated visitor satisfaction (" + rating + "★)")

Explanation = " • ".join(Reasons)
```

This ensures complete **algorithmic transparency** without hallucinated rationale.
