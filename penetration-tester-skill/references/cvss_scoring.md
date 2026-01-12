# CVSS Scoring Reference

## Overview
Comprehensive guide to CVSS (Common Vulnerability Scoring System) scoring for penetration testing.

## CVSS v3.1 Overview

CVSS v3.1 provides a framework for characterizing and rating vulnerabilities. Scores range from 0.0 to 10.0.

## Base Metrics

### Attack Vector (AV)

How the vulnerability is exploited.

| Metric | Value | Score | Description |
|---------|--------|--------|-------------|
| Network (N) | 0.85 | Exploitable over network |
| Adjacent (A) | 0.62 | Requires same logical network |
| Local (L) | 0.55 | Requires local access |
| Physical (P) | 0.2 | Requires physical access |

### Attack Complexity (AC)

Conditions beyond attacker's control.

| Metric | Value | Score | Description |
|---------|--------|--------|-------------|
| Low (L) | 0.77 | No specialized access conditions |
| High (H) | 0.44 | Specialized conditions required |

### Privileges Required (PR)

Privileges the attacker must possess before exploiting.

| Metric | Value | Score | Description |
|---------|--------|--------|-------------|
| None (N) | 0.85 | No privileges required |
| Low (L) | 0.62 | Low privileges required |
| High (H) | 0.27 | High privileges required |

### User Interaction (UI)

Whether user interaction is required for exploitation.

| Metric | Value | Score | Description |
|---------|--------|--------|-------------|
| None (N) | 0.85 | No user interaction required |
| Required (R) | 0.62 | User interaction required |

### Scope (S)

Does the vulnerable component impact other components?

| Metric | Value | Description |
|---------|--------|-------------|
| Unchanged (U) | Vulnerable component only |
| Changed (C) | Impacts other components |

### Confidentiality (C)

Impact on data confidentiality.

| Metric | Value | Description |
|---------|--------|-------------|
| High (H) | Total loss of confidentiality |
| Low (L) | Some data loss |
| None (N) | No impact |

### Integrity (I)

Impact on data integrity.

| Metric | Value | Description |
|---------|--------|-------------|
| High (H) | Total loss of integrity |
| Low (L) | Some data modification |
| None (N) | No impact |

### Availability (A)

Impact on availability of the component.

| Metric | Value | Description |
|---------|--------|-------------|
| High (H) | Total loss of availability |
| Low (L) | Reduced performance |
| None (N) | No impact |

## Base Score Calculation

```python
#!/usr/bin/env python3
def calculate_base_score(av, ac, pr, ui, scope, c, i, a):
    """Calculate CVSS v3.1 base score"""
    
    # Metric values mapping
    av_values = {'N': 0.85, 'A': 0.62, 'L': 0.55, 'P': 0.2}
    ac_values = {'L': 0.77, 'H': 0.44}
    pr_values = {'N': 0.85, 'L': 0.62, 'H': 0.27}
    ui_values = {'N': 0.85, 'R': 0.62}
    cia_values = {'H': 0.56, 'L': 0.22, 'N': 0.0}
    
    # Impact calculation
    iss = 1 - ((1 - cia_values[c]) * 
                 (1 - cia_values[i]) * 
                 (1 - cia_values[a]))
    
    # Impact sub-score
    if scope == 'C':
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02)**15
    else:
        impact = 6.42 * iss
    
    # Exploitability
    exploitability = 8.22 * av_values[av] * ac_values[ac] * pr_values[pr] * ui_values[ui]
    
    # Base score
    if impact <= 0:
        return 0.0
    
    if scope == 'C':
        base = min(10, impact + exploitability)
    else:
        base = min(10, (impact + exploitability) * 1.08)
    
    return round(base, 1)
```

## Severity Ratings

| Score Range | Severity | Color |
|-------------|----------|--------|
| 9.0 - 10.0 | Critical | 🔴 |
| 7.0 - 8.9 | High | 🟠 |
| 4.0 - 6.9 | Medium | 🟡 |
| 0.1 - 3.9 | Low | 🟢 |
| 0.0 | None | ⚪ |

## Common CVSS Scores by Attack Type

### SQL Injection
```
Attack Vector: Network (N) - 0.85
Attack Complexity: Low (L) - 0.77
Privileges Required: None (N) - 0.85
User Interaction: None (N) - 0.85
Scope: Unchanged (U)
Confidentiality: High (H) - 0.56
Integrity: High (H) - 0.56
Availability: High (H) - 0.56

Score: 9.8 (Critical)
```

### Cross-Site Scripting (Reflected)
```
Attack Vector: Network (N) - 0.85
Attack Complexity: Low (L) - 0.77
Privileges Required: None (N) - 0.85
User Interaction: Required (R) - 0.62
Scope: Unchanged (U)
Confidentiality: Low (L) - 0.22
Integrity: Low (L) - 0.22
Availability: None (N) - 0.0

Score: 6.1 (Medium)
```

### Stored XSS
```
Attack Vector: Network (N) - 0.85
Attack Complexity: Low (L) - 0.77
Privileges Required: None (N) - 0.85
User Interaction: Required (R) - 0.62
Scope: Changed (C)
Confidentiality: High (H) - 0.56
Integrity: High (H) - 0.56
Availability: None (N) - 0.0

Score: 8.1 (High)
```

### CSRF
```
Attack Vector: Network (N) - 0.85
Attack Complexity: Low (L) - 0.77
Privileges Required: None (N) - 0.85
User Interaction: Required (R) - 0.62
Scope: Unchanged (U)
Confidentiality: Low (L) - 0.22
Integrity: High (H) - 0.56
Availability: None (N) - 0.0

Score: 6.5 (Medium)
```

### Broken Access Control
```
Attack Vector: Network (N) - 0.85
Attack Complexity: Low (L) - 0.77
Privileges Required: Low (L) - 0.62
User Interaction: None (N) - 0.85
Scope: Changed (C)
Confidentiality: High (H) - 0.56
Integrity: High (H) - 0.56
Availability: High (H) - 0.56

Score: 9.6 (Critical)
```

### Hardcoded Credentials
```
Attack Vector: Network (N) - 0.85
Attack Complexity: Low (L) - 0.77
Privileges Required: None (N) - 0.85
User Interaction: None (N) - 0.85
Scope: Unchanged (U)
Confidentiality: High (H) - 0.56
Integrity: None (N) - 0.0
Availability: None (N) - 0.0

Score: 9.8 (Critical)
```

## Temporal Metrics (Optional)

### Exploit Code Maturity (E)
- **Not Defined (X):** Assign no score
- **Unproven (U):** No exploit code exists
- **Proof of Concept (P):** Proof-of-concept code
- **Functional (F):** Functional exploit exists
- **High (H):** Reliable, weaponized exploit

### Remediation Level (R)
- **Not Defined (X):** Assign no score
- **Official Fix (O):** Vendor has issued fix
- **Temporary Fix (T):** Temporary workaround available
- **Workaround (W):** Non-vendor workaround available
- **Unavailable (U):** No fix available

### Report Confidence (C)
- **Not Defined (X):** Assign no score
- **Unknown (U):** Unknown
- **Reasonable (R):** Reasonable confidence
- **Confirmed (C):** Vulnerability confirmed

## Environmental Metrics (Optional)

### Confidentiality Requirement (CR)
- **Not Defined (X):** Assign no score
- **Low (L):** Low impact to organization
- **Medium (M):** Medium impact to organization
- **High (H):** High impact to organization

### Integrity Requirement (IR)
Same as Confidentiality Requirement

### Availability Requirement (AR)
Same as Confidentiality Requirement

### Modified Base Metrics
Same as Base Metrics but adjusted for environment

## CVSS Calculator

```python
#!/usr/bin/env python3
"""
CVSS v3.1 Calculator
Usage: python3 cvss_calculator.py
"""

from typing import Dict, Tuple

class CVSSCalculator:
    def __init__(self):
        self.metrics = {
            'AV': {'N': 0.85, 'A': 0.62, 'L': 0.55, 'P': 0.2},
            'AC': {'L': 0.77, 'H': 0.44},
            'PR': {'N': 0.85, 'L': 0.62, 'H': 0.27},
            'UI': {'N': 0.85, 'R': 0.62},
            'CIA': {'H': 0.56, 'L': 0.22, 'N': 0.0}
        }
    
    def calculate_base(self, av: str, ac: str, pr: str, ui: str, 
                     scope: str, c: str, i: str, a: str) -> Tuple[float, str]:
        """Calculate base score and severity"""
        
        # Impact sub-score
        iss = 1 - ((1 - self.metrics['CIA'][c]) * 
                     (1 - self.metrics['CIA'][i]) * 
                     (1 - self.metrics['CIA'][a]))
        
        # Impact calculation
        if scope == 'C':
            impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02)**15
        else:
            impact = 6.42 * iss
        
        # Exploitability
        exploitability = (8.22 * self.metrics['AV'][av] * 
                       self.metrics['AC'][ac] * 
                       self.metrics['PR'][pr] * 
                       self.metrics['UI'][ui])
        
        # Base score
        if impact <= 0:
            base_score = 0.0
        elif scope == 'C':
            base_score = min(10, impact + exploitability)
        else:
            base_score = min(10, (impact + exploitability) * 1.08)
        
        return round(base_score, 1), self._get_severity(base_score)
    
    def _get_severity(self, score: float) -> str:
        """Get severity rating from score"""
        if score >= 9.0:
            return "Critical"
        elif score >= 7.0:
            return "High"
        elif score >= 4.0:
            return "Medium"
        elif score > 0.0:
            return "Low"
        else:
            return "None"

# Example usage
if __name__ == '__main__':
    calc = CVSSCalculator()
    
    # SQL Injection example
    score, severity = calc.calculate_base('N', 'L', 'N', 'N', 'U', 'H', 'H', 'H')
    print(f"SQL Injection: {score} ({severity})")
    
    # XSS example
    score, severity = calc.calculate_base('N', 'L', 'N', 'R', 'U', 'L', 'L', 'N')
    print(f"Reflected XSS: {score} ({severity})")
```

## CVSS String Format

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
         |  |  |  |  |  |  |  |
         |  |  |  |  |  |  |  + Availability
         |  |  |  |  |  |  + Integrity
         |  |  |  |  |  + Confidentiality
         |  |  |  |  + Scope
         |  |  |  + User Interaction
         |  |  + Privileges Required
         |  + Attack Complexity
         + Attack Vector
```

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                    CVSS v3.1                         │
├─────────────────────────────────────────────────────────┤
│                                                     │
│  AV  N(0.85)  A(0.62)  L(0.55)  P(0.2)         │
│  AC  L(0.77)  H(0.44)                              │
│  PR  N(0.85)  L(0.62)  H(0.27)                     │
│  UI  N(0.85)  R(0.62)                             │
│  CIA H(0.56)  L(0.22)  N(0.0)                     │
│                                                     │
│  Critical 9.0-10.0  High 7.0-8.9                   │
│  Medium 4.0-6.9    Low 0.1-3.9                     │
│                                                     │
│  Impact = 6.42 × ISS (Scope Unchanged)             │
│  Impact = 7.52 × (ISS-0.029) - 3.25×(ISS-0.02)^15 │
│            (Scope Changed)                           │
│                                                     │
│  Exploitability = 8.22 × AV × AC × PR × UI          │
│                                                     │
└─────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Be Conservative:** When in doubt, score lower
2. **Document Assumptions:** Record what you assumed
3. **Use Calculators:** Use official CVSS calculators
4. **Consider Context:** Adjust for your environment
5. **Review Regularly:** Scores can change with new info

## References

- [First.org CVSS Calculator](https://www.first.org/cvss/calculator/3.1)
- [NIST CVSS Standard](https://nvd.nist.gov/vuln-metrics/cvss)
- [CVSS v3.1 Specification](https://www.first.org/cvss/specification-document)
