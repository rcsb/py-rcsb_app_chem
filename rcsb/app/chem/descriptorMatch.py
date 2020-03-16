import logging

from collections import namedtuple
from enum import Enum
from typing import List
from fastapi import APIRouter, Path, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field  # pylint disable: no-name-in-module

from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper

logger = logging.getLogger("app_chem")

MatchResults = namedtuple("MatchResults", "ccId oeMol searchType matchOpts screenType fpType fpScore oeIdx formula", defaults=(None,) * 9)

router = APIRouter()


class DescriptorType(str, Enum):
    smiles = "SMILES"
    inchi = "InChI"


class DescriptorMatchType(str, Enum):
    relaxed = "graph-relaxed"
    relaxedStereo = "graph-relaxed-stereo"
    strict = "graph-strict"
    fuzzy = "fingerprint-similarity"


class DescriptorQuery(BaseModel):
    query: str = Field(None, title="Descriptor string", description="SMILES or InChI chemical descriptor")
    generator: str = Field(None, title="Descriptor generator", description="Program or agent generating the descriptor")
    matchType: DescriptorMatchType = Field(None, title="Query match type", description="Qualitative graph matching comparison or fingerprint comparison criteria")


class DescriptorQueryResult(BaseModel):
    query: str = Field(None, title="Descriptor query string", description="SMILES or InChI chemical descriptor")
    descriptorType: DescriptorType = Field(None, title="Descriptor type", description="SMILES or InChI")
    matchedIdList: List[str] = Field(None, title="Matched identifiers", description="Matched chemical component or BIRD identifier codes")


@router.get("/{descriptorType}", response_model=DescriptorQueryResult, tags=["descriptor"])
def matchGetQuery(
    query: str = Query(None, title="Descriptor string", description="SMILES or InChI chemical descriptor"),
    matchType: DescriptorMatchType = Query(None, title="Query match type", description="Qualitative graph matching or fingerprint comparison criteria"),
    descriptorType: DescriptorType = Path(..., title="Descriptor type", description="Type of chemical descriptor (SMILES or InChI)"),
):
    logger.info("Got %r %r %r", descriptorType, query, matchType)
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, ssL, fpL = ccsw.matchByDescriptor(query, descriptorType, matchOpts=matchType)
    logger.info("Results (%r) ssL (%d) fpL (%d)", retStatus, len(ssL), len(fpL))
    if matchType in ["fingerprint-similarity"]:
        rL = [mr.ccId for mr in fpL]
    else:
        rL = [mr.ccId for mr in ssL]
    # ---
    return {"query": query, "descriptorType": descriptorType, "matchedIdList": rL}


@router.post("/{descriptorType}", response_model=DescriptorQueryResult, tags=["descriptor"])
def matchPostQuery(
    query: DescriptorQuery, descriptorType: DescriptorType = Path(..., title="Descriptor match query", description="Type of chemical descriptor (SMILES or InChI)"),
):
    logger.info("Got %r %r", descriptorType, query)
    qD = jsonable_encoder(query)
    logger.debug("qD %r", qD)
    # ---
    ccsw = ChemCompSearchWrapper()
    retStatus, ssL, fpL = ccsw.matchByDescriptor(qD["query"], descriptorType, matchOpts=qD["matchType"])
    logger.info("Results (%r) ssL (%d) fpL (%d)", retStatus, len(ssL), len(fpL))
    if qD["matchType"] in ["fingerprint-similarity"]:
        rL = [mr.ccId for mr in fpL]
    else:
        rL = [mr.ccId for mr in ssL]
    # ---
    return {"query": query.query, "descriptorType": descriptorType, "matchedIdList": rL}
