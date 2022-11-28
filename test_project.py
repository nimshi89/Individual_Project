from pathlib import Path
from typing import Tuple
import pytest
import rdflib
import Project


def test_get_responses():
    file = Path("tes_tes_file.ttl")

    g = rdflib.Graph()

    g.parse(file, format='ttl')
    
    the_uri = Project.get_first_interaction_uri(g)

    tes_variable = Project.get_responses(the_uri, g)

    assert len(tes_variable) == 1
    response_text_1, maybe_next_interaction_uri = tes_variable[0]
    assert response_text_1 == "I'm doing alright."
    assert maybe_next_interaction_uri == "http://example.com/interaction/interaction-doing-ok"


    assert type(tes_variable) is list
    assert type(tes_variable[0]) is tuple
    assert type(((tes_variable)[0])[0]) is str

def test_get_responses_without_next_interaction():
    file = Path("tes_tes_file_no_next_niteraction.ttl")

    g = rdflib.Graph()

    g.parse(file, format='ttl')
    
    the_uri = Project.get_first_interaction_uri(g)

    tes_variable = Project.get_responses(the_uri, g)  

    assert len(tes_variable) == 1
    response_text_1, maybe_next_interaction_uri = tes_variable[0]
    assert response_text_1 == "I'm doing alright."
    assert maybe_next_interaction_uri is None

def test_get_intitial_statement():
    file = Path("tes_tes_file_no_next_niteraction.ttl")

    g = rdflib.Graph()

    g.parse(file, format='ttl')
    
    the_uri = Project.get_first_interaction_uri(g) 

    interaction = Project.get_initial_question(the_uri, g)

    assert interaction.statement == "How are you doing today?"
    assert interaction.character_name == "Billy-bob"

