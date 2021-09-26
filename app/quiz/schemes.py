from marshmallow import Schema, fields


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested("AnswerSchema", many=True, required=True)


class GameStateSchema(Schema):
    id = fields.Int(required=False)
    state = fields.String(required=False)
    date = fields.Int(required=False)
    answered = fields.Dict(required=False, many=True)
    theme = fields.String(required=False)
    start_date = fields.Int(required=False)
    user_id = fields.Int(required=True)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ThemeIdSchema(Schema):
    theme_id = fields.Int()


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)


class ListGameStateSchema(Schema):
    states = fields.Nested(GameStateSchema, many=True)
