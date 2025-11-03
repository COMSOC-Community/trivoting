import abc
from enum import Enum

from pulp import LpProblem, LpMaximize, LpAffineExpression, LpVariable, LpBinary, lpSum, HiGHS, PULP_CBC_CMD, \
    LpStatusOptimal, value

from trivoting.election import AbstractTrichotomousProfile, Selection
from trivoting.fractions import Numeric


class ILPNotOptimalError(ValueError):
    pass

class PuLPSolvers(Enum):
    HIGHS = "HIGHS"
    CBC = "CBC"

class ILPBUilder(abc.ABC):
    model_name = "NoName"

    def __init__(self,
                 profile: AbstractTrichotomousProfile,
                 max_size_selection: int,
                 initial_selection: Selection = None,
                 max_seconds: int = 600,
                 verbose: bool = False,
                 solver_name: PuLPSolvers = None) -> None:
        self.profile = profile
        self.max_size_selection = max_size_selection
        self.initial_selection = initial_selection
        if solver_name is None:
            solver_name = PuLPSolvers.HIGHS
        if solver_name == PuLPSolvers.HIGHS:
            self.solver = HiGHS(msg=verbose, timeLimit=max_seconds)
        elif solver_name == PuLPSolvers.CBC:
            self.solver = PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds)
        else:
            raise ValueError("Unsupported solver name {}.".format(solver_name))

        self.model = LpProblem(self.model_name, sense=LpMaximize)
        self.vars = dict()


    def init_selection_vars(self):
        self.vars["selection"] = {
            alt: LpVariable(f"y_{alt.name}", cat=LpBinary)
            for alt in self.profile.alternatives
        }

    def init_vars(self) -> None:
        """"""
        self.init_selection_vars()

    def constrain_initial_selection(self):
        if self.initial_selection is not None:
            for alt in self.initial_selection.selected:
                self.model += self.vars["selection"][alt] == 1
            if not self.initial_selection.implicit_reject:
                for alt in self.initial_selection.rejected:
                    self.model += self.vars["selection"][alt] == 0

    def constrain_max_size_selection(self):
        self.model += lpSum(self.vars["selection"].values()) <= self.max_size_selection

    def apply_constraints(self):
        self.constrain_max_size_selection()

    @abc.abstractmethod
    def objective(self) -> LpAffineExpression:
        """"""

    def set_objective(self):
        self.model += self.objective()

    def solve(self):
        return self.model.solve(self.solver)

    def force_objective_value(self, v: Numeric):
        self.model += self.objective() == v

    def ban_selection(self, selection: Selection) -> None:
        # See http://yetanothermathprogrammingconsultant.blogspot.com/2011/10/integer-cuts.html
        self.model += (
            lpSum((1 - self.vars["selection"][a]) for a in selection.selected)
            + lpSum(v for a, v in self.vars["selection"].items() if a not in selection)
        ) >= 1

        self.model += (
            lpSum(self.vars["selection"][a] for a in selection.selected)
            - lpSum(v for a, v in self.vars["selection"].items() if a not in selection)
        ) <= len(selection) - 1



def ilp_optimiser_rule(
    ilp_builder: ILPBUilder,
    resoluteness: bool = True,
) -> Selection | list[Selection]:

    ilp_builder.init_vars()
    ilp_builder.apply_constraints()
    ilp_builder.set_objective()

    status = ilp_builder.solve()

    all_selections = []

    if status == LpStatusOptimal:
        selection = Selection(implicit_reject=True)
        for alt, v in ilp_builder.vars["selection"].items():
            if value(v) >= 0.9:
                selection.add_selected(alt)
        all_selections.append(selection)
    else:
        raise ILPNotOptimalError(
            f"Solver did not find an optimal solution, status is {status}."
        )

    if resoluteness:
        return all_selections[0]

    # If irresolute, we solve again, banning the previous selections
    ilp_builder.force_objective_value(value(ilp_builder.model.objective))

    previous_selection = selection
    while True:
        ilp_builder.ban_selection(previous_selection)

        status = ilp_builder.solve()

        if status != LpStatusOptimal:
            break

        previous_selection = Selection(
            [a for a, v in ilp_builder.vars["selection"].items() if value(v) is not None and value(v) >= 0.9],
            implicit_reject=True,
        )
        if previous_selection not in all_selections:
            all_selections.append(previous_selection)

    return all_selections
