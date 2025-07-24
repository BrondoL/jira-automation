from marshmallow import Schema, fields, validate

class FormSchema(Schema):
    summary = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(required=True, validate=validate.Length(min=1))
    priority = fields.Str(required=True, validate=validate.Length(min=1))
    assignee = fields.Str(required=True, validate=validate.Length(min=1))
    reporter = fields.Email(required=True)