import bullet
import importlib.util

from .exceptions import InvalidBlueprint


def is_entry_name(value):
    def wrapped(entry):
        return entry["name"] == value

    return wrapped


class ContextBuilder:
    types = ["input", "number", "boolean", "password", "select", "multiselect"]

    basic_transforms = {"int": int, "float": float, "str": str, "bool": bool}

    prompt_to_questions = {}

    def __init__(self):
        self.prompt = None

    def bullet_workaround(self, prompt: str):
        if prompt.startswith("[y/n] "):
            return prompt[6:]

        return prompt

    def transform_result(self, tmp_result: dict, utils_path: str):
        result = {}

        utils = None
        if utils_path:
            spec = importlib.util.spec_from_file_location("utils", utils_path)
            utils = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(utils)

        for (key, answer) in tmp_result:
            question = self.prompt_to_questions[self.bullet_workaround(key)]
            values = question.get("values", None)
            if values and isinstance(answer, list):
                converted_answer = []
                for value in answer:
                    entry = next(filter(is_entry_name(value), question["values"]))
                    converted_answer.append(entry.get("value", entry["name"]))
                answer = converted_answer
            elif values:
                entry = next(filter(is_entry_name(answer), question["values"]))
                answer = entry.get("value", entry["name"])

            transform = question.get("transform", None)
            if transform:
                transform_func = self.basic_transforms.get(transform, None)

                if transform_func:
                    answer = transform_func(answer)
                elif utils:
                    answer = getattr(utils, transform)(answer)

            result[question["id"]] = answer

        return result

    def build_context(self, manifest: dict, utils_path: str = None) -> dict:
        self.create_prompt(manifest)
        tmp_result = self.prompt.launch()
        result = self.transform_result(tmp_result, utils_path)
        return result

    def create_prompt(self, manifest: dict):
        self.prompt = bullet.SlidePrompt(
            [self.question_to_prompt(question) for question in manifest.get("questions", [])]
        )

    def extract_names(self, values: list):
        return list(map(lambda value: value["name"], values))

    def question_to_prompt(self, question: dict):
        self.prompt_to_questions[question.get("prompt")] = question

        question_type = question.get("type", None)

        if question_type is None or question_type not in self.types:
            raise InvalidBlueprint(f"Invalid question type: {question_type}")

        if question_type == "input":
            return bullet.Input(question["prompt"])
        if question_type == "number":
            return bullet.Numbers(question["prompt"])
        if question_type == "boolean":
            return bullet.YesNo(question["prompt"])
        if question_type == "password":
            return bullet.Password(question["prompt"])
        if question_type == "select":
            return bullet.Bullet(question["prompt"], choices=self.extract_names(question.get("values", [])))
        if question_type == "multiselect":
            return bullet.Check(question["prompt"], choices=self.extract_names(question.get("values", [])))

