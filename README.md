## Project 1: Cross-Border Academic Credential & GPA Normalization Engine

### 1. Problem Statement
International institutions issue transcripts using fundamentally incompatible grading and credit conventions (e.g., India 10-point CGPA, UK Honours classifications, European ECTS scales, and Francophone 20-point scales). Manual translation creates severe processing bottlenecks, and automated ingest fails when downstream systems demand standardized North American semester credits and a 4.0 GPA scale.

### 2. Architecture & Solution
I engineered `credential_engine.py` to:
* Parse raw course arrays with differing local scales.
* Apply dynamic credit hour multipliers (e.g., 4 UK credits = 1 US semester hour; 2 ECTS = 1 US semester hour).
* Calculate weighted quality points to output a verified 4.0 cumulative GPA.

### 3. Code Implementation
See [credential_engine.py](./credential_engine.py) for the complete implementation.
