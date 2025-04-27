#
# Created by Renatus Madrigal on 04/24/2025
#

import argparse
from typing import get_origin, get_args
from typing import Type, Union, Optional, Dict, Tuple, Any, List
from pydantic import BaseModel


class PositionalArg:
    """
    A class to handle positional arguments for PyLaTeXFlow.
    """

    def __init__(
        self,
        position: int,
        nargs: Optional[str] = None,
        metavar: Optional[str] = None,
    ):
        self.position = position
        self.nargs = nargs
        self.metavar = metavar

    def __repr__(self):
        return f"PositionalConfig(position={self.position}, nargs={self.nargs}, metavar={self.metavar})"


class ArgumentParser:
    """
    A class to handle command-line arguments for PyLaTeXFlow.
    This class is responsible for parsing and validating command-line arguments
    using the Pydantic library.

    """

    class _DictAction(argparse.Action):
        """
        Custom action to handle dictionary-like command-line arguments.
        """

        def __init__(self, option_strings, dest, **kwargs):
            super().__init__(
                option_strings,
                dest,
                nargs="*",
                metavar="KEY=VALUE",
                **kwargs,
            )

        def type_convert(self, value: str) -> Any:
            """Auto type detection for the value."""
            true_val = ["true", "yes", "1", "on"]
            false_val = ["false", "no", "0", "off"]
            null_val = ["null", "none", "nil"]
            lower_val = value.lower()
            if lower_val in true_val:
                return True
            if lower_val in false_val:
                return False
            if lower_val in null_val:
                return None

            try:
                return int(value)
            except:
                pass
            try:
                return float(value)
            except:
                pass
            return value

        def __call__(self, parser, namespace, values, option_string=None):
            result = {}
            for item in values:
                if "=" not in item:
                    raise argparse.ArgumentError(
                        self,
                        f"Invalid key-value pair: {item}. Expected format: key=value.",
                    )

                key, value = item.split("=", 1)
                keys = key.split(".")
                current = result

                for k in keys[:-1]:
                    current = current.setdefault(k, {})

                final_key = keys[-1]
                converted = self.type_convert(value)

                if "[" in final_key and "]" in final_key:
                    base_key, index = final_key[:-1].split("[")
                    index = int(index) if index else 0
                    current.setdefault(base_key, [])
                    while len(current[base_key]) <= index:
                        current[base_key].append(None)
                    current[base_key][index] = converted
                else:
                    current[final_key] = converted

            setattr(namespace, self.dest, result)

    @staticmethod
    def _parse_kv_pair(arg: str) -> Tuple[str, str]:
        try:
            key, value = arg.split("=", 1)
            return key, value
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid key-value pair: {arg}. Expected format: key=value."
            )

    @staticmethod
    def _split_positional(
        model: Type[BaseModel],
    ) -> Tuple[List[Tuple[str, Any]], List[Tuple[str, Any]]]:
        positional = []
        optional = []
        for name, field in model.model_fields.items():
            metadata = (
                field.json_schema_extra.get("position", None)
                if field.json_schema_extra
                else None
            )
            if metadata is not None:
                if isinstance(metadata, PositionalArg):
                    positional.append((name, field))
                else:
                    raise ValueError(
                        f"Invalid positional argument config for field '{name}': {metadata}"
                    )
            else:
                optional.append((name, field))
        positional.sort(
            key=lambda x: x[1].json_schema_extra.get("position", 0).position
        )
        return positional, optional

    @staticmethod
    def _add_arguments_from_model(
        parser: argparse.ArgumentParser,
        model: Type[BaseModel],
    ):
        positional, optional = ArgumentParser._split_positional(model)
        for name, field in positional:
            metadata: PositionalArg = field.json_schema_extra.get("position", None)
            parser.add_argument(
                name,
                type=field.annotation,
                nargs=metadata.nargs,
                metavar=metadata.metavar,
                help=field.description or f"{name} argument",
            )

        for name, field in optional:
            required = field.is_required()

            if field.default is Ellipsis:
                print(f"Warning: Skipping field {name} (default_factory not supported)")
                continue

            arg_name = f"--{name.replace('_', '-')}"
            help_text = field.description or f"{name} argument"

            field_type = field.annotation
            origin_type = get_origin(field_type)
            type_args = get_args(field_type)

            if origin_type is Union:
                non_none_types = [t for t in type_args if t is not type(None)]
                if len(non_none_types) == 1:
                    field_type = non_none_types[0]
                else:
                    print(f"Warning: Skipping field {name} (unsupported Union type)")
                    continue
            elif origin_type is list:
                if len(type_args) == 1:
                    field_type = list
                else:
                    print(f"Warning: Skipping field {name} (unsupported list type)")
                    continue
            elif origin_type is dict:
                if len(type_args) == 2:
                    key_type, value_type = type_args
                    if key_type is not str:
                        print(
                            f"Warning: Skipping field {name} (unsupported dict key type)"
                        )
                        continue
                    if value_type is not str:
                        print(
                            f"Warning: Skipping field {name} (unsupported dict value type)"
                        )
                        continue
                    field_type = dict
                else:
                    print(f"Warning: Skipping field {name} (unsupported dict type)")
                    continue
            elif origin_type is not None:
                print(
                    f"Warning: Skipping field {name} (unsupported origin type: {origin_type})"
                )
                continue

            if field_type is bool:
                action = "store_false" if field.default else "store_true"
                parser.add_argument(
                    arg_name,
                    action=action,
                    help=help_text,
                    required=required,
                )
                continue
            elif field_type is dict:
                parser.add_argument(
                    arg_name,
                    action=ArgumentParser._DictAction,
                    default=field.default,
                    help=help_text,
                    required=required,
                )
                continue
            elif field_type is list:
                parser.add_argument(
                    arg_name,
                    type=field_type,
                    nargs="+",
                    default=field.default,
                    help=help_text,
                    required=required,
                )
                continue

            try:
                parser.add_argument(
                    arg_name,
                    type=field_type,
                    default=field.default,
                    help=help_text,
                    required=required,
                )
            except TypeError as e:
                print(f"Warning: Skipping field {name} (type parsing failed: {str(e)})")

    @staticmethod
    def _push_models(
        parent_parser: argparse.ArgumentParser,
        models: Dict[str, Type[BaseModel]],
    ) -> None:
        subparsers = parent_parser.add_subparsers(dest="command")
        for cmd, model in models.items():
            subparser = subparsers.add_parser(
                cmd.replace("_", "-"),
                help=(model.__doc__ if model.__doc__ else f"{cmd} command"),
            )
            ArgumentParser._add_arguments_from_model(subparser, model)
            subparser.set_defaults(model_class=model)

    @staticmethod
    def _parse_to_model(args) -> BaseModel:
        return args.model_class(**vars(args))

    def __init__(self, models: Dict[str, Type[BaseModel]]):
        self.parser = argparse.ArgumentParser(
            description="PyLaTeXFlow: A LaTeX document generation library."
        )
        self._push_models(self.parser, models)
        self.models = models

    def parse_args(
        self, args: Optional[list] = None
    ) -> Tuple[BaseModel, Optional[str]]:
        try:
            parsed_args = self.parser.parse_args(args)
            command = parsed_args.command if hasattr(parsed_args, "command") else None
            return self._parse_to_model(parsed_args), command
        except Exception as e:
            print(f"Error: {e}")
            self.print_help()

    def print_help(self):
        self.parser.print_help()
        self.parser.exit()
