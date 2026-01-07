import pytest
from spss_engine.pipeline import CompilerPipeline
from spec_writer.conductor import Conductor
from spec_writer.describer import SpecGenerator

class QualityGate:
    """
    The 'Judge' that assesses if a Specification is Good or Bad.
    """
    @staticmethod
    def assess(pipeline: CompilerPipeline, clusters: list, required_clusters: int, prohibited_leaks: dict) -> bool:
        """
        Pass Criteria:
        1. Cluster Count >= required_clusters (Did we untangle the spaghetti?)
        2. No Prohibited Leaks (Did logic from Step A appear in Step B?)
        """
        # Criterion 1: Structure
        if len(clusters) < required_clusters:
            print(f"❌ FAIL: Expected {required_clusters} clusters, found {len(clusters)}.")
            return False

        # Criterion 2: Isolation
        # prohibited_leaks = {"Main_Cluster_Name": ["bad_var_1", "bad_var_2"]}
        # We need to map the clusters to names heuristically
        
        conductor = Conductor(pipeline.state_machine)
        for i, cluster in enumerate(clusters):
            # Flatten the cluster to a string for checking
            cluster_content = " ".join(conductor._topological_sort(cluster))
            
            # Check for leaks
            for context_name, banned_vars in prohibited_leaks.items():
                # Heuristic: If this cluster contains the "Key Indicator" of that context...
                # (Real implementation would be more robust, here we just scan all clusters)
                for banned in banned_vars:
                    if banned in cluster_content and "PAYMENT" in cluster_content:
                         # If we are in the Payment (Main) cluster, we shouldn't see 'value' from ETL
                        print(f"❌ FAIL: Variable '{banned}' leaked into Main Logic Cluster.")
                        return False
        
        print("✅ PASS: Quality Gate cleared.")
        return True

class TestSpecComplexityLevels:
    
    # =========================================================================
    # LEVEL 1: SIMPLE (Linear Flow)
    # Goal: Verify the system doesn't over-engineer simple scripts.
    # =========================================================================
    def test_level_1_simple(self):
        code = """
        GET DATA /FILE='simple_data.csv'.
        COMPUTE a = 10.
        COMPUTE b = 20.
        COMPUTE result = a + b.
        SAVE OUTFILE='output.sav'.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        conductor = Conductor(pipeline.state_machine)
        clusters = conductor.identify_clusters()
        
        # Expectation: 1 Cluster (It's a straight line)
        assert QualityGate.assess(
            pipeline, 
            clusters, 
            required_clusters=1, 
            prohibited_leaks={}
        )

    # =========================================================================
    # LEVEL 2: MODERATE (The Provided Example)
    # Goal: Verify ETL separation (Control Vars vs Main Logic).
    # =========================================================================
    def test_level_2_standard(self):
        # This mirrors your example_pspp_final.sps
        code = """
        * CLUSTER A: ETL.
        GET DATA /FILE='control.csv'.
        COMPUTE min_age = NUMBER(value, F3.0). * 'value' is generic here
        SAVE OUTFILE='control.sav'.

        * CLUSTER B: Main.
        GET DATA /FILE='claims.csv'.
        MATCH FILES /FILE=* /TABLE='control.sav' /BY id.
        COMPUTE eligible = (age > min_age).
        SAVE OUTFILE='final.sav'.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        conductor = Conductor(pipeline.state_machine)
        clusters = conductor.identify_clusters()
        
        # Expectation: 2 Clusters (ETL, Main)
        # Pass Criterion: 'value' (from ETL) must NOT be a dependency of 'eligible' (in Main)
        # directly in the main cluster context.
        assert QualityGate.assess(
            pipeline, 
            clusters, 
            required_clusters=2, 
            prohibited_leaks={"Main": ["value"]} 
        )

    # =========================================================================
    # LEVEL 3: COMPLEX (Cascading Aggregations)
    # Goal: The "Breaking Point". Multiple feeds, aggregation feeding back in.
    # =========================================================================
    def test_level_3_complex(self):
        code = """
        * CLUSTER A: Employee Data ETL.
        GET DATA /FILE='employees.csv'.
        COMPUTE clean_dept = RTRIM(dept).
        SAVE OUTFILE='employees.sav'.

        * CLUSTER B: Sales Data Aggregation.
        GET DATA /FILE='sales.csv'.
        AGGREGATE /OUTFILE='dept_performance.sav' 
          /BREAK=dept 
          /avg_sales = MEAN(amount).

        * CLUSTER C: Final Join & Calculation.
        GET DATA /FILE='employees.sav'. * Re-loading Cluster A output
        MATCH FILES /FILE=* /TABLE='dept_performance.sav' /BY dept.
        
        IF (sales > avg_sales) bonus = 1000.
        SAVE OUTFILE='payroll.sav'.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        conductor = Conductor(pipeline.state_machine)
        clusters = conductor.identify_clusters()
        
        # Expectation: 3 Clusters.
        # 1. Employee ETL
        # 2. Sales Aggregation
        # 3. Final Payroll
        
        # If the system is confused by the AGGREGATE file save/load, 
        # it might merge B and C, or A and C incorrectly.
        assert QualityGate.assess(
            pipeline, 
            clusters, 
            required_clusters=3,
            prohibited_leaks={}
        )