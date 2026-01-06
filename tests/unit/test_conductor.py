import pytest
from spss_engine.state import StateMachine
from spec_writer.conductor import Conductor


class TestConductor:

    def test_identify_islands(self):
        """
        Scenario: Two completely separate logic chains.
        1. Payroll: Gross -> Tax
        2. Demographics: DOB -> Age

        The Conductor should group these into two different clusters.
        """
        state = StateMachine()

        # Cluster 1: Payroll
        state.register_assignment("Gross", "Gross = 50000")
        state.register_assignment("Tax", "Tax = Gross * 0.2", dependencies=["GROSS_0"])

        # Cluster 2: Demographics
        state.register_assignment("DOB", "DOB = '1990-01-01'")
        state.register_assignment("Age", "Age = 2026 - DOB", dependencies=["DOB_0"])

        conductor = Conductor(state)
        clusters = conductor.identify_clusters()

        # We expect 2 clusters
        assert len(clusters) == 2

        # Verify contents (We don't know the order, so we check existence)
        flat_clusters = [set(c) for c in clusters]

        # Check Payroll Cluster exists
        payroll_vars = {"GROSS_0", "TAX_0"}
        assert any(payroll_vars.issubset(c) for c in flat_clusters)

        # Check Demographics Cluster exists
        demo_vars = {"DOB_0", "AGE_0"}
        assert any(demo_vars.issubset(c) for c in flat_clusters)

    def test_topological_sort(self):
        """
        Within a cluster, 'Gross' must be listed before 'Tax'.
        """
        state = StateMachine()
        state.register_assignment("Tax", "Tax = ...", dependencies=["GROSS_0"])
        state.register_assignment(
            "Gross", "Gross = ..."
        )  # Registered LATER, but depends IS earlier

        conductor = Conductor(state)
        clusters = conductor.identify_clusters()

        cluster = clusters[0]  # There is only one cluster

        # Verify order: Gross (Dependency) -> Tax (Dependent)
        assert cluster == ["GROSS_0", "TAX_0"]
