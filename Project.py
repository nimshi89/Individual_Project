from dataclasses import dataclass
from distutils.sysconfig import PREFIX
from tokenize import maybe
from typing import List, Optional, Tuple
import rdflib
from pathlib import Path




def get_first_interaction_uri(grap: rdflib.Graph) ->str:
    interaction_uri = """
    SELECT ?conversationmap ?interaction
    WHERE{
        ?conversationmap a <http://example.com/types/conversation-map>.

        ?interaction a <http://example.com/types/interaction>.

        ?conversationmap <http://example.com/predicates/hasNextInteraction> ?interaction.

    }
    
    """
    sparql_results = grap.query(interaction_uri)
    results: List[rdflib.query.ResultRow] = list(sparql_results)  #  type: ignore

    if len(results) != 1:
        raise Exception(f"Got an unexpected number of results {len(results)}.")

    result_dict = results[0].asdict()
    
    return str(result_dict["interaction"])


@dataclass
class Interaction:
    statement: str
    character_name: str

def get_initial_question(interaction_uri: str, graph: rdflib.Graph)-> Interaction:

    query = """
        BASE <http://example.com/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?initialStatement ?name
        WHERE{
            ?character a <types/character>.

            ?interaction <predicates/hasInitialStatement> ?initialStatement.

            ?interaction <predicates/initiatedBy> ?character.

            ?character rdf:label ?name. 

        }

        """
    stuff = graph.query(query, initBindings={"interaction": rdflib.URIRef(interaction_uri)})

    results: List[rdflib.query.ResultRow] = list(stuff)  #  type: ignore
    
    if len(results) != 1:
        raise Exception(f"Got an unexpected number of results {len(results)}.")

    
    result_dict = results[0].asdict()

    return Interaction(statement=str(result_dict["initialStatement"]),
     character_name=str(result_dict["name"]))

def no_furter_interaction()-> None:


    print("Conversation over!")

    quit()


def get_responses(interaction_uri: str, graph: rdflib.Graph)->List[Tuple[str, str]]:
    quey2 = """

    BASE <http://example.com/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?response_text ?nexInteraction
    WHERE{

        ?response a <types/response>.

        ?interaction <predicates/hasResponseOptions> ?response.

        ?response rdf:label  ?response_text.

        OPTIONAL {
            ?response <predicates/hasNextInteraction> ?nexInteraction
        }
    }
    """
    
    responses = graph.query(quey2, initBindings={"interaction": rdflib.URIRef(interaction_uri)})
    
    results: List[rdflib.query.ResultRow] = list(responses)  #  type: ignore
    
    results_list = []

    for response in results:
        result_dict = response.asdict()
        response_text = str(result_dict["response_text"])
        #this will lead to a bug in the future
        if "nexInteraction" in result_dict:
            next_interaction_uri = str(result_dict["nexInteraction"])
        else:
            next_interaction_uri = None
        results_list.append((response_text, next_interaction_uri))


    return results_list


def get_interaction_information(maybe_interaction_uri: Optional[str] = None):
    interaction_uri =  maybe_interaction_uri or get_first_interaction_uri(g)

    person_inertacting = get_initial_question(interaction_uri, g)

    print(f"{person_inertacting.character_name} says: {person_inertacting.statement}")
    
    list_of_anwsers = get_responses(interaction_uri, g)

    if not any(list_of_anwsers):
        no_furter_interaction()

    for i, answer in enumerate(list_of_anwsers):
        print(f"({i}) {answer[0]}")
    
    the_anwser = int(input("What would you like to respond?"))

    print(f"you have selected {list_of_anwsers[the_anwser][0]}" )

    maybe_next_interaction_uri = list_of_anwsers[the_anwser][1]
    if maybe_next_interaction_uri is None:
        no_furter_interaction()
    else:
        get_interaction_information(maybe_next_interaction_uri)


if __name__ == '__main__':
    file = Path("tes_file.ttl")

    g = rdflib.Graph()

    g.parse(file, format='ttl')

    get_interaction_information()