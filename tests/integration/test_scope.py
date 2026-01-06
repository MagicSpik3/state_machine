import pytest
from spss_engine.pipeline import CompilerPipeline
from tests.corpus import COMPREHENSIVE_SCOPE_CORPUS


class TestScopeCorpus:

    def test_comprehensive_corpus_parsing(self):
        """
        Runs the full corpus through the pipeline and verifies that
        variable versions (SSA) increment correctly despite complex syntax.
        """
        pipeline = CompilerPipeline()
        pipeline.process(COMPREHENSIVE_SCOPE_CORPUS)

        # 1. Check Simple Initialization
        # Age was init(0) -> assigned(25) -> assigned(in DO IF)
        # We expect at least version 2 (AGE_2) or higher depending on flow.
        # Let's count:
        #   1. COMPUTE Age = 0.         (AGE_0)
        #   2. COMPUTE Age = 25.        (AGE_1)
        #   3. No other updates to Age (Age_Group is different).
        assert pipeline.get_variable_version("Age").id == "AGE_1"

        # 2. Check Variable Declaration
        # Gender was declared STRING (GENDER_0) -> RECODE In-Place (GENDER_1)
        assert pipeline.get_variable_version("Gender").id == "GENDER_1"
        # 3. Check Arithmetic & Whitespace
        # Income_2023 init(-1) -> assigned(math)
        assert pipeline.get_variable_version("Income_2023").id == "INCOME_2023_1"

        # 4. Check Conditional Logic Extraction
        # 'Description' set in IF (DESCRIPTION_0) -> Recoded in DO IF (DESCRIPTION_1)
        assert pipeline.get_variable_version("Description").id == "DESCRIPTION_1"
        # 5. Check DO IF Block Logic
        # Age_Group set in IF (0) -> ELSE IF (1) -> ELSE (2)
        # Since it's the same variable being updated in different branches,
        # SSA logic treats them as sequential updates in the linear parse order.
        # Counts: DO IF(0), ELSE IF(1), ELSE(2) -> Final should be version 2
        assert pipeline.get_variable_version("Age_Group").id == "AGE_GROUP_2"

        # 6. Check RECODE INTO
        # Poverty_Flag is a new target.
        assert pipeline.get_variable_version("Poverty_Flag").id == "POVERTY_FLAG_0"