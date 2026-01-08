import pytest
import shutil
import os
import textwrap
from spss_engine.spss_runner import PsppRunner

pspp_installed = shutil.which("pspp") is not None


@pytest.mark.skipif(not pspp_installed, reason="PSPP is not installed on this system")
class TestGroundTruth:

    def test_payroll_calculation(self):
        """
        Verify that the actual PSPP binary calculates Net Pay correctly.
        """
        file_path = "payroll.spss"
        csv_path = "payroll_probe.csv"  # The runner defaults to {basename}_probe.csv

        # 1. Clean up previous runs
        if os.path.exists(csv_path):
            os.remove(csv_path)

        # 2. Define valid SPSS code
        spss_code = textwrap.dedent(
            """
        DATA LIST LIST /dummy.
        BEGIN DATA
        1
        END DATA.
        COMPUTE Gross = 50000.
        COMPUTE Tax_Rate = 0.20.
        COMPUTE Tax = Gross * Tax_Rate.
        COMPUTE Net_Pay = Gross - Tax.
        EXECUTE.
        """
        )

        with open(file_path, "w") as f:
            f.write(spss_code.strip())

        # 3. Run
        runner = PsppRunner()
        results = runner.run_and_probe(file_path)

        # 4. Debugging: If GROSS is missing, print what WE DID find.
        if "GROSS" not in results:
            print("\nDEBUG: 'GROSS' missing from results.")
            print(f"Keys found: {list(results.keys())}")

            if os.path.exists(csv_path):
                print(f"CSV File Content ({csv_path}):")
                with open(csv_path, "r") as f:
                    print(f.read())
            else:
                print(f"CSV File {csv_path} was NOT created.")

        # 5. Verify
        assert "GROSS" in results, f"Missing GROSS. Found: {results.keys()}"
        assert float(results["GROSS"]) == 50000.0
        assert float(results["TAX"]) == 10000.0
        assert float(results["NET_PAY"]) == 40000.0

    def test_runner_handles_errors(self):
        bad_code = "payroll_bad.spss"
        with open(bad_code, "w") as f:
            f.write("COMPUTE X = .")

        runner = PsppRunner()

        try:
            with pytest.raises(RuntimeError):
                runner.run_and_probe(bad_code)
        finally:
            if os.path.exists(bad_code):
                os.remove(bad_code)
