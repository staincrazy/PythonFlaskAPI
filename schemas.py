from marshmallow import Schema, fields


class PlainItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class PlainTagSchema(Schema):
    id = fields.Integer(dump_only = True)
    name = fields.String()


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Integer()

class ItemSchema(PlainItemSchema):
    store_id = fields.Integer(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema(), dump_only=True))


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainStoreSchema(),dump_only=True))
    tags = fields.List(fields.Nested(PlainTagSchema(),dump_only=True))

class TagSchema(PlainTagSchema):
    store_id = fields.Integer(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))


class TagAndItemSchema(Schema):
    message = fields.String()
    items = fields.Nested(ItemSchema)
    tags = fields.Nested(TagSchema)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)