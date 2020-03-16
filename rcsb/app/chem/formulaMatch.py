##
# File: formulaMatch.py
# Date: 12-Mar-2020
#
##
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
from typing import Dict, List
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder

# pylint disable=no-name-in-module
from pydantic import BaseModel, Field  # pylint disable=no-name-in-module

from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper
from rcsb.app.chem.ElementSymbol import ElementSymbol

logger = logging.getLogger("app_chem")

router = APIRouter()


class ElementRange(BaseModel):
    min: int = Field(None, ge=0, title="Mininum element count", description="Minimum number of occurences of element in molecular formula (inclusive)")
    max: int = Field(None, ge=0, title="Maximum element count", description="Maximum number of occurences of element in molecular formula (inclusive)")


class FormulaQuery(BaseModel):
    query: str = Field(None, title="Molecular formula", description="Molecular formula (ex. C6H11NO2S)")
    matchSubset: bool = Field(False, title="Formula subsets", description="Match formulas satisfying only the subset of query the conditions")


class FormulaQueryResult(BaseModel):
    query: str = Field(None, title="Molecular formula", description="Molecular formula (ex. C6H11NO2S)")
    matchedIdList: List[str] = Field(None, title="Matched identifiers", description="Matched chemical component or BIRD identifier codes")


class FormulaRangeQuery(BaseModel):
    query: Dict[ElementSymbol, ElementRange] = Field(
        None, title="Formula query dictionary", description="Dictionary representing a formula query as a dictionary of element symbols and minimum and maximum boundary conditions"
    )
    matchSubset: bool = Field(False, title="Match formula subsets", description="Match formulas satisfying only the subset of query the conditions")


class FormulaRangeQueryResult(BaseModel):
    query: Dict[str, ElementRange] = Field(
        None,
        title="Formula range query dictionary",
        description="Dictionary representing a formula query as a dictionary of element symbols and minimum and maximum boundary conditions",
    )
    matchedIdList: List[str] = Field(None, title="Matched identifiers", description="Matched chemical component or BIRD identifier codes")


@router.get("/formula", tags=["formula"], response_model=FormulaQueryResult)
def matchGetQuery(
    query: str = Query(None, title="Molecular formula", description="Molecular formula (ex. C6H11NO2S"),
    matchSubset: bool = Query(False, title="Formula subsets", description="Find formulas satisfying only the subset of query the conditions"),
):
    logger.debug("Got %r", query)
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, matchResultL = ccsw.matchByFormula(query, matchSubset=matchSubset)
    logger.info("Results (%r) rL %r", retStatus, matchResultL)
    rL = [mr.ccId for mr in matchResultL]
    # ---
    return {"query": query, "matchedIdList": rL}


@router.post("/formula", tags=["formula"], response_model=FormulaQueryResult)
def matchPostQuery(query: FormulaQuery):
    logger.debug("Got %r", query)
    qD = jsonable_encoder(query)
    logger.debug("qD %r", qD)
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, matchResultL = ccsw.matchByFormula(qD["query"], matchSubset=qD["matchSubset"])
    logger.info("Results (%r) rL %r", retStatus, matchResultL)
    rL = [mr.ccId for mr in matchResultL]
    # ---
    return {"query": qD["query"], "matchedIdList": rL}


@router.post("/formula/range", tags=["formula"], response_model=FormulaRangeQueryResult)
def matchRangePostQuery(query: FormulaRangeQuery):
    logger.debug("Got %r", query)
    qD = jsonable_encoder(query)
    logger.debug("qD %r", qD)
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, matchResultL = ccsw.matchByFormulaRange(qD["query"], qD["matchSubset"])
    logger.info("Results (%r) rL %r", retStatus, matchResultL)
    rL = [mr.ccId for mr in matchResultL]
    # ---
    return {"query": qD["query"], "matchedIdList": rL}
