from typing import Type

from pydantic import ValidationError, BaseModel


def validate_log_pydantic_obj_errors(
        PydanticBaseModel: Type[BaseModel],
        request_json: dict,
        log_success_validation: bool = False
) -> BaseModel | None:
    try:
        validated_obj = PydanticBaseModel(**request_json)
        validated_dict = validated_obj.model_dump()
        if log_success_validation:
            print(f"PYDANTIC VALIDATION [OK]: "
                  f"validated_obj: '{validated_obj}', "
                  f"validated_dict: {validated_dict}\n")
        return validated_obj
    except ValidationError as error:
        errors_list = []
        for error in error.errors():
            field_name = ".".join(str(loc) for loc in error["loc"])
            error_type = error["type"]
            error_message = error["msg"]
            input_value = error.get("input", "N/A")

            error_info = {"field_name": field_name,
                          "error_type": error_type,
                          "error_message": error_message,
                          "input_value": input_value}
            errors_list.append(error_info)

            error_log = (f"PYDANTIC VALIDATION [ERROR]: "
                         f"field_name: '{field_name}', "
                         f"error_type: {error_type}, "
                         f"error_message: {error_message}, "
                         f"input_value: {input_value}\n")
            print(error_log)
