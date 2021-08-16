#!/usr/bin/env python
# coding: utf-8
"""
Abstract optimization model based on pyomo
"""

from copy import copy
from pyomo import opt as po
from pyomo import environ as pe

from spo.model import optModel


class optOmoModel(optModel):
    """
    This is an abstract class for pyomo-based optimization model

    Args:
        solver: optimization solver
    """

    def __init__(self, solver="glpk"):
        super().__init__()
        # init obj
        self._model.obj = pe.Objective(sense=pe.minimize, expr=0)
        # set solver
        self.solver = solver
        if self.solver == "gurobi":
            self._solverfac = po.SolverFactory(self.solver, solver_io="python")
        else:
            self._solverfac = po.SolverFactory(self.solver)

    def __repr__(self):
        return "optOmoModel " + self.__class__.__name__

    def setObj(self, c):
        """
        A method to set objective function

        Args:
            c (ndarray): cost of objective function
        """
        if len(c) != self.num_cost:
            raise ValueError("Size of cost vector cannot match vars.")
        # delete previous component
        self._model.del_component(self._model.obj)
        # set obj
        obj = sum(c[i] * self.x[k] for i, k in enumerate(self.x))
        self._model.obj = pe.Objective(sense=pe.minimize, expr=obj)

    def solve(self):
        """
        A method to solve model

        Returns:
            tuple: optimal solution (list) and objective value (float)
        """
        # solve
        self._solverfac.solve(self._model)
        return [pe.value(self.x[k]) for k in self.x], pe.value(self._model.obj)

    def copy(self):
        """
        A method to copy model

        Returns:
            optModel: new copied model
        """
        new_model = copy(self)
        # new model
        new_model._model = self._model.clone()
        # variables for new model
        new_model.x = new_model._model.x
        return new_model

    def addConstr(self, coefs, rhs):
        """
        A method to add new constraint

        Args:
            coefs (ndarray): coeffcients of new constraint
            rhs (float): right-hand side of new constraint

        Returns:
            optModel: new model with the added constraint
        """
        if len(coefs) != self.num_cost:
            raise ValueError("Size of coef vector cannot cost.")
        # copy
        new_model = self.copy()
        # add constraint
        expr = sum(coefs[i] * new_model.x[k]
                   for i, k in enumerate(new_model.x)) <= rhs
        new_model._model.cons.add(expr)
        return new_model
