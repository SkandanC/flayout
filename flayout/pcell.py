# AUTOGENERATED! DO NOT EDIT! File to edit: source/03_pcell.ipynb (unless otherwise specified).

__all__ = ['pcell']

# Internal Cell
from functools import partial
from inspect import Parameter
from typing import Any, Callable, Optional

import pya
from .cell import copy_tree

CELL_CONVERTERS = {}

# Internal Cell
def _klayout_type(param: Parameter):
    type_map = {
        pya.PCellDeclarationHelper.TypeInt: pya.PCellDeclarationHelper.TypeInt,
        "TypeInt": pya.PCellDeclarationHelper.TypeInt,
        "int": pya.PCellDeclarationHelper.TypeInt,
        int: pya.PCellDeclarationHelper.TypeInt,
        Optional[int]: pya.PCellDeclarationHelper.TypeInt,
        pya.PCellDeclarationHelper.TypeDouble: pya.PCellDeclarationHelper.TypeDouble,
        "TypeDouble": pya.PCellDeclarationHelper.TypeDouble,
        "float": pya.PCellDeclarationHelper.TypeDouble,
        float: pya.PCellDeclarationHelper.TypeDouble,
        Optional[float]: pya.PCellDeclarationHelper.TypeDouble,
        pya.PCellDeclarationHelper.TypeString: pya.PCellDeclarationHelper.TypeString,
        "TypeString": pya.PCellDeclarationHelper.TypeString,
        "str": pya.PCellDeclarationHelper.TypeString,
        str: pya.PCellDeclarationHelper.TypeString,
        Optional[str]: pya.PCellDeclarationHelper.TypeString,
        pya.PCellDeclarationHelper.TypeBoolean: pya.PCellDeclarationHelper.TypeBoolean,
        "TypeBoolean": pya.PCellDeclarationHelper.TypeBoolean,
        "bool": pya.PCellDeclarationHelper.TypeBoolean,
        bool: pya.PCellDeclarationHelper.TypeBoolean,
        Optional[bool]: pya.PCellDeclarationHelper.TypeBoolean,
        pya.PCellDeclarationHelper.TypeLayer: pya.PCellDeclarationHelper.TypeLayer,
        "TypeLayer": pya.PCellDeclarationHelper.TypeLayer,
        "LayerInfo": pya.PCellDeclarationHelper.TypeLayer,
        pya.LayerInfo: pya.PCellDeclarationHelper.TypeLayer,
        pya.PCellDeclarationHelper.TypeShape: pya.PCellDeclarationHelper.TypeShape,
        "TypeShape": pya.PCellDeclarationHelper.TypeShape,
        "Shape": pya.PCellDeclarationHelper.TypeShape,
        pya.Shape: pya.PCellDeclarationHelper.TypeShape,
        pya.PCellDeclarationHelper.TypeList: pya.PCellDeclarationHelper.TypeList,
        "TypeList": pya.PCellDeclarationHelper.TypeList,
        "list": pya.PCellDeclarationHelper.TypeList,
        list: pya.PCellDeclarationHelper.TypeList,
        Optional[list]: pya.PCellDeclarationHelper.TypeList,
    }
    try:
        annotation = param.annotation
        if annotation is Parameter.empty:
            annotation = type(param.default)
    except AttributeError:
        annotation = param
    if not annotation in type_map:
        raise ValueError(
            f"Cannot create pcell. Parameter {param.name!r} has unsupported type: {annotation!r}"
        )
    return type_map[annotation]

# Internal Cell
def _python_type(param: Parameter):
    type_map = {
        pya.PCellDeclarationHelper.TypeInt: int,
        "TypeInt": int,
        "int": int,
        int: int,
        pya.PCellDeclarationHelper.TypeDouble: float,
        "TypeDouble": float,
        "float": float,
        float: float,
        pya.PCellDeclarationHelper.TypeString: str,
        "TypeString": str,
        "str": str,
        str: str,
        pya.PCellDeclarationHelper.TypeBoolean: bool,
        "TypeBoolean": bool,
        "bool": bool,
        bool: bool,
        pya.PCellDeclarationHelper.TypeLayer: pya.LayerInfo,
        "TypeLayer": pya.LayerInfo,
        "LayerInfo": pya.LayerInfo,
        pya.LayerInfo: pya.LayerInfo,
        pya.PCellDeclarationHelper.TypeShape: pya.Shape,
        "TypeShape": pya.Shape,
        "Shape": pya.Shape,
        pya.Shape: pya.Shape,
        pya.PCellDeclarationHelper.TypeList: list,
        "TypeList": list,
        "list": list,
        list: list,
    }
    try:
        annotation = param.annotation
        if annotation is Parameter.empty:
            annotation = type(param.default)
    except AttributeError:
        annotation = param
    if not annotation in type_map:
        raise ValueError(
            f"Cannot create pcell. Parameter {param.name!r} has unsupported type: {annotation!r}"
        )
    return type_map[annotation]

# Internal Cell

def _validate_on_error(on_error):
    on_error = on_error.lower()
    if not on_error in ["raise", "ignore"]:
        raise ValueError("on_error should be 'raise' or 'ignore'.")
    return on_error

def _validate_parameter(name, param):
    if param.kind == Parameter.VAR_POSITIONAL:
        raise ValueError(
            f"Cannot create pcell from functions with var positional [*args] arguments."
        )
    elif param.kind == Parameter.VAR_KEYWORD:
        raise ValueError(
            f"Cannot create pcell from functions with var keyword [**kwargs] arguments."
        )
    elif param.kind == Parameter.POSITIONAL_ONLY:
        raise ValueError(
            f"Cannot create pcell from functions with positional arguments. Please use keyword arguments."
        )
    elif (param.kind == Parameter.POSITIONAL_OR_KEYWORD) and (param.default is Parameter.empty):
        raise ValueError(
            f"Cannot create pcell from functions with positional arguments. Please use keyword arguments."
        )
    annotation = _python_type(_klayout_type(_python_type(param)))
    default = param.default
    try:
        default = annotation(default)
    except Exception:
        pass
    return Parameter(
        name,
        kind=Parameter.KEYWORD_ONLY,
        default=default,
        annotation=annotation,
    )


class DynamicPCell(pya.PCellDeclarationHelper):
    """PCell class to create a PCell from a function."""
    def __init__(self, func: Callable):
        f"""a {func().name} PCell."""
        super().__init__()
        self.func = func
        self.func_name = func().name
        params = self._pcell_parameters(self.func, on_error="raise")
        self._param_keys = [param for param in params.keys()]
        self._param_values = []
        for name, param in params.items():
            # Add the parameter to the PCell
            self._param_values.append(
                self.param(
                    name=name,
                    value_type=_klayout_type(param),
                    description=name.replace("_", " "),
                    default=param.default,
                )
            )

    def produce_impl(self):
        """Produce the PCell."""
        params = {k: v for k, v in zip(self._param_keys, self._param_values)}
        cell = self.func(**params)

        # Add the cell to the layout
        copy_tree(cell, self.cell, on_same_name="replace")
        self.cell.name = self.func_name

    def _pcell_parameters(self, func: Callable, on_error="ignore"):
        """Get the parameters of a function."""
        # NOTE: There could be a better way to do this, than use __signature__.
        new_params = {}

        try:
            sig = func.__signature__
        except AttributeError:
            return new_params

        new_params.update({'name': Parameter('name', kind=Parameter.KEYWORD_ONLY, default=self.func_name, annotation=str)})
        params = sig.parameters
        on_error = _validate_on_error(on_error)
        for name, param in params.items():
            try:
                new_params[name] = _validate_parameter(name, param)
            except ValueError:
                if on_error == "raise":
                    raise
        return new_params

# Cell

def pcell(func=None, on_error="raise"):
    """create a KLayout PCell from a native python function

    Args:
        func: the function creating a KLayout cell

    Returns:
        the Klayout PCell
    """
    if func is None:
        return partial(pcell, on_error=on_error)

    return DynamicPCell(func)
