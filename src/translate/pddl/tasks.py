from typing import List, Union

from translate.pddl import axioms
from translate.pddl import predicates
from translate.pddl.actions import Action
from translate.pddl.axioms import Axiom
from translate.pddl.conditions import Atom, Condition
from translate.pddl.f_expression import Assign
from translate.pddl.functions import Function
from translate.pddl.pddl_types import Type, TypedObject
from translate.pddl.predicates import Predicate
from collections import Counter

class Task:
    def __init__(self, domain_name: str, task_name: str,
                 requirements: "Requirements",
                 types: List[Type], objects: List[TypedObject], predicates:
                 List[Predicate], functions: List[Function],
                 init: List[Union[Atom, Assign]], goal: Condition,
                 actions: List[Action], axioms: List[Axiom],
                 use_metric: bool) -> None:
        self.domain_name = domain_name
        self.task_name = task_name
        self.requirements = requirements
        self.types = types
        self.objects = objects
        self.predicates = predicates
        self.functions = functions
        self.init = init
        self.goal = goal
        self.actions = actions
        self.axioms = axioms
        self.axiom_counter = 0
        self.use_min_cost_metric = use_metric
        self.axiom_dict = {} # could become the main datastructure for storing axioms in FD later
        for axiom in axioms:
            self.axiom_dict.setdefault(axiom.name, []).append(axiom)


    # Add a single axiom to both self.axioms and self.axiom_dict.
    def _register_axiom(self, axiom):
        self.axioms.append(axiom)
        self.axiom_dict.setdefault(axiom.name, []).append(axiom)

    def add_axiom(self, parameters, condition):
        name = "new-axiom@%d" % self.axiom_counter
        self.axiom_counter += 1
        axiom = axioms.Axiom(name, parameters, len(parameters), condition)
        self.predicates.append(predicates.Predicate(name, parameters))
        self._register_axiom(axiom)
        return axiom

    # Alternative implementation of add_axiom. Adds one new rule for each condition 
    # with the same derived variable each head.
    # This method is used by step [2-axiom] of normalize.py to replace disjunctions 
    # in conditions with axioms.
    def add_axioms_from_disjunction(self, parameters, conditions):
        name = "new-axiom@%d" % self.axiom_counter
        self.axiom_counter += 1
        for cond in conditions:
            axiom = axioms.Axiom(name, parameters, len(parameters), cond)
            self._register_axiom(axiom)
        self.predicates.append(predicates.Predicate(name, parameters))
        return name

    # used to check wether there is already an equivalent axiom (theoretically O(n^2))
    def get_equivalent_axiom(self, conditions):
        for derived_predicate_name in self.axiom_dict:
            other_conditions = [cond.condition for cond in  self.axiom_dict[derived_predicate_name]]
            # check if both lists are the same
            if (Counter(conditions) == Counter(other_conditions)):
                # TODO: figure out if condition hashes are unique
                return derived_predicate_name


    def dump(self):
        print("Problem %s: %s [%s]" % (
            self.domain_name, self.task_name, self.requirements))
        print("Types:")
        for type in self.types:
            print("  %s" % type)
        print("Objects:")
        for obj in self.objects:
            print("  %s" % obj)
        print("Predicates:")
        for pred in self.predicates:
            print("  %s" % pred)
        print("Functions:")
        for func in self.functions:
            print("  %s" % func)
        print("Init:")
        for fact in self.init:
            print("  %s" % fact)
        print("Goal:")
        self.goal.dump()
        print("Actions:")
        for action in self.actions:
            action.dump()
        if self.axioms:
            print("Axioms:")
            for axiom in self.axioms:
                axiom.dump()


REQUIREMENT_LABELS = [
    ":strips", ":adl", ":typing", ":negation", ":equality",
    ":negative-preconditions", ":disjunctive-preconditions",
    ":existential-preconditions", ":universal-preconditions",
    ":quantified-preconditions", ":conditional-effects",
    ":derived-predicates", ":action-costs"
]


class Requirements:
    def __init__(self, requirements: List[str]):
        self.requirements = requirements
        for req in requirements:
            if req not in REQUIREMENT_LABELS:
                raise ValueError(f"Invalid requirement. Got: {req}\n"
                                 f"Expected: {', '.join(REQUIREMENT_LABELS)}")
    def __str__(self):
        return ", ".join(self.requirements)
